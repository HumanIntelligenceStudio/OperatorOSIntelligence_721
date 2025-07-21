"""
Health Monitor - System health monitoring and agent recovery
Real-time monitoring of agent health and automatic recovery
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import psutil
import os

from app import db
from models import AgentInstance, SystemMetrics

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitors system and agent health with automatic recovery"""
    
    def __init__(self, check_interval=30, recovery_enabled=True):
        self.check_interval = check_interval
        self.recovery_enabled = recovery_enabled
        self.running = False
        self.health_history = []
        self.alerts = []
        
        # Health thresholds
        self.thresholds = {
            'agent_success_rate_min': 70.0,
            'agent_response_time_max': 30.0,
            'system_cpu_max': 80.0,
            'system_memory_max': 85.0,
            'failed_agents_max': 3
        }
    
    def start(self):
        """Start the health monitoring system"""
        if self.running:
            return
        
        self.running = True
        self._start_health_checker()
        self._start_system_monitor()
        logger.info("Health monitor started")
    
    def stop(self):
        """Stop the health monitoring system"""
        self.running = False
        logger.info("Health monitor stopped")
    
    def _start_health_checker(self):
        """Start the agent health checking thread"""
        def health_check_loop():
            while self.running:
                try:
                    self._check_agent_health()
                    self._check_system_health()
                    self._perform_recovery_actions()
                    time.sleep(self.check_interval)
                
                except Exception as e:
                    logger.error(f"Error in health check loop: {e}")
                    time.sleep(5)  # Short delay on error
        
        threading.Thread(target=health_check_loop, daemon=True).start()
    
    def _start_system_monitor(self):
        """Start the system resource monitoring thread"""
        def system_monitor_loop():
            while self.running:
                try:
                    self._record_system_metrics()
                    time.sleep(60)  # Record every minute
                
                except Exception as e:
                    logger.error(f"Error in system monitor: {e}")
                    time.sleep(10)
        
        threading.Thread(target=system_monitor_loop, daemon=True).start()
    
    def _check_agent_health(self):
        """Check health of all agents"""
        agents = AgentInstance.query.all()
        unhealthy_agents = []
        
        for agent in agents:
            health_issues = self._assess_agent_health(agent)
            
            if health_issues:
                unhealthy_agents.append({
                    'agent': agent,
                    'issues': health_issues
                })
                
                # Log health issues
                logger.warning(f"Agent {agent.instance_id} health issues: {health_issues}")
        
        # Record health check
        self._record_health_check(len(agents), len(unhealthy_agents))
        
        return unhealthy_agents
    
    def _assess_agent_health(self, agent: AgentInstance) -> List[str]:
        """Assess individual agent health"""
        issues = []
        
        # Check success rate
        if agent.total_tasks > 10 and agent.success_rate < self.thresholds['agent_success_rate_min']:
            issues.append(f"Low success rate: {agent.success_rate:.1f}%")
        
        # Check response time
        if agent.avg_response_time > self.thresholds['agent_response_time_max']:
            issues.append(f"High response time: {agent.avg_response_time:.2f}s")
        
        # Check last health check time
        if agent.last_health_check:
            time_since_check = datetime.utcnow() - agent.last_health_check
            if time_since_check > timedelta(minutes=10):
                issues.append(f"Stale health check: {time_since_check}")
        
        # Check if agent is stuck in busy state
        if agent.status == 'busy' and agent.current_load == 0:
            issues.append("Agent stuck in busy state")
        
        # Update last health check
        with db.session.begin():
            agent.last_health_check = datetime.utcnow()
        
        return issues
    
    def _check_system_health(self):
        """Check overall system health"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['system_cpu_max']:
                self._add_alert(f"High CPU usage: {cpu_percent:.1f}%", 'warning')
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds['system_memory_max']:
                self._add_alert(f"High memory usage: {memory.percent:.1f}%", 'warning')
            
            # Check failed agents
            failed_agents = AgentInstance.query.filter_by(status='failed').count()
            if failed_agents > self.thresholds['failed_agents_max']:
                self._add_alert(f"Too many failed agents: {failed_agents}", 'error')
            
            # Check database connectivity
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db.session.commit()
            except Exception as e:
                self._add_alert(f"Database connectivity issue: {e}", 'critical')
        
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    def _perform_recovery_actions(self):
        """Perform automatic recovery actions"""
        if not self.recovery_enabled:
            return
        
        try:
            # Restart failed agents
            failed_agents = AgentInstance.query.filter_by(status='failed').all()
            for agent in failed_agents:
                if self._should_restart_agent(agent):
                    self._restart_agent(agent)
            
            # Clear stuck agents
            stuck_agents = AgentInstance.query.filter_by(status='busy').filter(
                AgentInstance.current_load == 0
            ).all()
            
            for agent in stuck_agents:
                logger.info(f"Clearing stuck agent: {agent.instance_id}")
                with db.session.begin():
                    agent.status = 'idle'
                    agent.current_load = 0
        
        except Exception as e:
            logger.error(f"Error in recovery actions: {e}")
    
    def _should_restart_agent(self, agent: AgentInstance) -> bool:
        """Determine if an agent should be restarted"""
        # Don't restart recently failed agents
        if agent.last_health_check:
            time_since_failure = datetime.utcnow() - agent.last_health_check
            if time_since_failure < timedelta(minutes=5):
                return False
        
        # Restart if failure rate is not too high
        if agent.total_tasks > 0:
            failure_rate = agent.failed_tasks / agent.total_tasks
            return failure_rate < 0.5  # Don't restart if >50% failure rate
        
        return True
    
    def _restart_agent(self, agent: AgentInstance):
        """Restart a failed agent"""
        try:
            logger.info(f"Restarting agent: {agent.instance_id}")
            
            with db.session.begin():
                agent.status = 'idle'
                agent.current_load = 0
                agent.last_health_check = datetime.utcnow()
            
            self._add_alert(f"Restarted agent: {agent.instance_id}", 'info')
        
        except Exception as e:
            logger.error(f"Error restarting agent {agent.instance_id}: {e}")
    
    def _record_health_check(self, total_agents: int, unhealthy_agents: int):
        """Record health check results"""
        health_record = {
            'timestamp': datetime.utcnow(),
            'total_agents': total_agents,
            'unhealthy_agents': unhealthy_agents,
            'health_score': ((total_agents - unhealthy_agents) / total_agents * 100) if total_agents > 0 else 100
        }
        
        self.health_history.append(health_record)
        
        # Keep only last 100 records
        if len(self.health_history) > 100:
            self.health_history.pop(0)
    
    def _record_system_metrics(self):
        """Record system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Count agents by status
            agents = AgentInstance.query.all()
            agent_stats = {
                'total': len(agents),
                'active': len([a for a in agents if a.status in ['idle', 'busy']]),
                'idle': len([a for a in agents if a.status == 'idle']),
                'busy': len([a for a in agents if a.status == 'busy']),
                'failed': len([a for a in agents if a.status == 'failed'])
            }
            
            # Save to database
            with db.session.begin():
                metrics = SystemMetrics()
                metrics.total_agents = agent_stats['total']
                metrics.active_agents = agent_stats['active']
                metrics.idle_agents = agent_stats['idle']
                metrics.failed_agents = agent_stats['failed']
                metrics.api_usage = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
                db.session.add(metrics)
        
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
    
    def _add_alert(self, message: str, level: str):
        """Add a system alert"""
        alert = {
            'timestamp': datetime.utcnow(),
            'message': message,
            'level': level
        }
        
        self.alerts.append(alert)
        logger.log(
            logging.ERROR if level == 'critical' else 
            logging.WARNING if level in ['error', 'warning'] else 
            logging.INFO,
            f"Health Alert [{level.upper()}]: {message}"
        )
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts.pop(0)
    
    def get_health_status(self) -> Dict:
        """Get current health status"""
        agents = AgentInstance.query.all()
        
        return {
            'overall_health': 'good' if len(self.alerts) == 0 else 'warning',
            'agent_health': {
                'total': len(agents),
                'healthy': len([a for a in agents if a.status in ['idle', 'busy']]),
                'failed': len([a for a in agents if a.status == 'failed'])
            },
            'recent_alerts': self.alerts[-10:],  # Last 10 alerts
            'health_history': self.health_history[-20:],  # Last 20 health checks
            'recovery_enabled': self.recovery_enabled
        }
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_average': [0, 0, 0]
            }
