"""
AgentMasterController - Enterprise-Grade Agent Architecture Implementation
Core system bootstrap with auto-scaling, intelligent routing, and real-time monitoring
"""

import os
import time
import json
import threading
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import uuid
import queue

from app import db
from models import AgentInstance, TaskRequest, SystemMetrics, UserSession
from ai_providers import AIProviderManager
from ai_providers_enhanced import initialize_enhanced_ai_provider, AssistantMode
from agent_pools import SpecializedAgentPools

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AgentMasterController:
    """Enterprise-grade multi-agent coordination system"""
    
    def __init__(self, max_agents_per_pool=10, health_check_interval=30):
        self.max_agents_per_pool = max_agents_per_pool
        self.health_check_interval = health_check_interval
        
        # Initialize AI providers and specialized agents
        self.ai_providers = AIProviderManager()
        self.enhanced_ai_providers = initialize_enhanced_ai_provider()
        self.specialized_pools = SpecializedAgentPools(self.ai_providers)
        
        # Agent management
        self.agent_pools: Dict[str, List[AgentInstance]] = {
            'healthcare': [],
            'financial': [],
            'sports': [],
            'business': [],
            'general': []
        }
        
        # Task management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        
        # Session management
        self.user_sessions: Dict[str, Dict] = {}
        self.conversation_context: Dict[str, List] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running = False
        self.start_time = datetime.now()
        
        # Agent type definitions
        self.agent_capabilities = {
            'healthcare': [
                'medical_diagnosis', 'pharmacology_analysis', 'insurance_navigation',
                'healthcare_finance', 'wellness_coaching', 'clinical_decision_support'
            ],
            'financial': [
                'wealth_optimization', 'debt_elimination', 'tax_strategy',
                'retirement_planning', 'business_finance', 'market_intelligence'
            ],
            'sports': [
                'sports_prediction', 'market_education', 'fantasy_sports',
                'compliance_monitoring', 'sports_content', 'analytics'
            ],
            'business': [
                'process_automation', 'workflow_optimization', 'project_management',
                'team_coordination', 'strategic_planning', 'operations'
            ],
            'general': [
                'general_assistance', 'research', 'analysis', 'writing', 'consulting'
            ]
        }
        
        logger.info("AgentMasterController initialized")
    
    def start(self):
        """Start the master controller system"""
        if self.running:
            logger.warning("AgentMasterController already running")
            return
        
        self.running = True
        logger.info("Starting AgentMasterController...")
        
        # Initialize core agent pools
        self._initialize_core_agents()
        
        # Start background services
        self._start_health_monitor()
        self._start_task_processor()
        self._start_auto_scaler()
        
        logger.info("AgentMasterController started successfully")
    
    def stop(self):
        """Stop the master controller system"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("AgentMasterController stopped")
    
    def _initialize_core_agents(self):
        """Initialize core agent instances for each pool"""
        try:
            for pool_name in self.agent_pools.keys():
                # Check existing agents in database
                existing_agents = db.session.query(AgentInstance).filter_by(
                    pool_name=pool_name, 
                    status='idle'
                ).count()
                
                # Start with 2 agents per pool if none exist
                if existing_agents < 2:
                    for i in range(2 - existing_agents):
                        agent = self._create_agent_instance(pool_name)
                        db.session.add(agent)
                        logger.info(f"Created {pool_name} agent: {agent.instance_id}")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing core agents: {e}")
        
        self._update_system_metrics()
    
    def _create_agent_instance(self, pool_name: str) -> AgentInstance:
        """Create a new agent instance"""
        instance_id = f"{pool_name}_{uuid.uuid4().hex[:8]}"
        
        # Different capacities based on agent type
        capacity_map = {
            'healthcare': 3,
            'financial': 5,
            'sports': 4,
            'business': 4,
            'general': 6
        }
        
        agent = AgentInstance()
        agent.instance_id = instance_id
        agent.agent_type = pool_name
        agent.pool_name = pool_name
        agent.status = 'idle'
        agent.current_load = 0
        agent.max_capacity = capacity_map.get(pool_name, 3)
        agent.success_rate = 100.0
        agent.avg_response_time = 0.0
        agent.last_health_check = datetime.utcnow()
        agent.created_at = datetime.utcnow()
        agent.total_tasks = 0
        agent.successful_tasks = 0
        agent.failed_tasks = 0
        
        return agent
    
    def submit_task(self, query: str, user_id: int = None, 
                   session_id: str = None, priority: int = 5,
                   required_capabilities: List[str] = None) -> str:
        """Submit a new task for processing"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        if session_id is None:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Analyze query to determine required capabilities
        if required_capabilities is None:
            required_capabilities = self._analyze_query_capabilities(query)
        
        # Create task in database
        try:
            task = TaskRequest()
            task.task_id = task_id
            task.query = query
            task.required_capabilities = required_capabilities
            task.priority = priority
            task.user_id = user_id
            task.status = 'pending'
            task.timeout = 30
            db.session.add(task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating task: {e}")
            raise
        
        # Add to priority queue (lower number = higher priority)
        self.task_queue.put((priority, time.time(), task_id))
        self.active_tasks[task_id] = task
        
        logger.info(f"Task submitted: {task_id} with capabilities: {required_capabilities}")
        return task_id
    
    def _analyze_query_capabilities(self, query: str) -> List[str]:
        """Analyze query to determine required capabilities and agent pool"""
        query_lower = query.lower()
        
        # Healthcare keywords
        health_keywords = [
            'health', 'medical', 'medicine', 'doctor', 'hospital', 'insurance',
            'medication', 'drug', 'symptom', 'diagnosis', 'treatment', 'pharmacy',
            'healthcare', 'clinical', 'patient', 'prescription', 'wellness'
        ]
        
        # Financial keywords
        finance_keywords = [
            'money', 'investment', 'stock', 'portfolio', 'tax', 'finance',
            'budget', 'loan', 'mortgage', 'retirement', 'savings', 'debt',
            'credit', 'bank', 'financial', 'wealth', 'market', 'economy'
        ]
        
        # Sports keywords
        sports_keywords = [
            'sports', 'game', 'bet', 'betting', 'odds', 'fantasy', 'nfl',
            'nba', 'mlb', 'nhl', 'football', 'basketball', 'baseball',
            'hockey', 'arbitrage', 'sportsbook', 'gambling'
        ]
        
        # Business keywords
        business_keywords = [
            'business', 'workflow', 'automation', 'process', 'management',
            'project', 'team', 'operations', 'strategy', 'planning',
            'organization', 'productivity', 'efficiency'
        ]
        
        # Count keyword matches
        health_score = sum(1 for keyword in health_keywords if keyword in query_lower)
        finance_score = sum(1 for keyword in finance_keywords if keyword in query_lower)
        sports_score = sum(1 for keyword in sports_keywords if keyword in query_lower)
        business_score = sum(1 for keyword in business_keywords if keyword in query_lower)
        
        # Determine primary capability
        scores = {
            'healthcare': health_score,
            'financial': finance_score,
            'sports': sports_score,
            'business': business_score
        }
        
        primary_domain = max(scores.keys(), key=lambda k: scores[k])
        
        if scores[primary_domain] == 0:
            return ['general_assistance']
        
        # Return capabilities for the primary domain
        return self.agent_capabilities.get(primary_domain, ['general_assistance'])
    
    def _start_task_processor(self):
        """Start the task processing thread"""
        from app import app
        
        def process_tasks():
            with app.app_context():
                while self.running:
                    try:
                        # Get task from queue with timeout
                        priority, timestamp, task_id = self.task_queue.get(timeout=1.0)
                        
                        # Get task from database
                        task = db.session.query(TaskRequest).filter_by(task_id=task_id).first()
                        if not task:
                            continue
                        
                        # Find suitable agent
                        agent = self._find_suitable_agent(task.required_capabilities)
                        
                        if agent:
                            # Process task with selected agent
                            self.executor.submit(self._process_task, task, agent)
                        else:
                            # No suitable agent available, requeue with delay
                            time.sleep(0.1)
                            self.task_queue.put((priority, timestamp, task_id))
                    
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Error in task processor: {e}")
        
        threading.Thread(target=process_tasks, daemon=True).start()
        logger.info("Task processor started")
    
    def _find_suitable_agent(self, required_capabilities: List[str]) -> Optional[AgentInstance]:
        """Find the best available agent for the required capabilities"""
        # Determine which pool to use based on capabilities
        target_pool = 'general'
        for pool_name, capabilities in self.agent_capabilities.items():
            if any(cap in capabilities for cap in required_capabilities):
                target_pool = pool_name
                break
        
        # Find available agent in target pool
        available_agents = db.session.query(AgentInstance).filter_by(
            pool_name=target_pool,
            status='idle'
        ).filter(
            AgentInstance.current_load < AgentInstance.max_capacity
        ).all()
        
        if not available_agents:
            # Try to find agent in general pool as fallback
            available_agents = db.session.query(AgentInstance).filter_by(
                pool_name='general',
                status='idle'
            ).filter(
                AgentInstance.current_load < AgentInstance.max_capacity
            ).all()
        
        if available_agents:
            # Select agent with best performance
            return min(available_agents, key=lambda a: (a.current_load, -a.success_rate))
        
        return None
    
    def _process_task(self, task: TaskRequest, agent: AgentInstance):
        """Process a task with the assigned agent"""
        start_time = time.time()
        
        try:
            # Update agent status
            try:
                agent.status = 'busy'
                agent.current_load += 1
                agent.total_tasks += 1
                task.status = 'processing'
                task.agent_id = agent.id
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating agent status: {e}")
            
            # Execute task using specialized agent pools
            result = self._execute_agent_task(task, agent)
            
            # Mark as successful
            try:
                agent.successful_tasks += 1
                task.status = 'completed'
                task.result = result
                task.completed_at = datetime.utcnow()
                
                # Update success rate
                agent.success_rate = (agent.successful_tasks / agent.total_tasks) * 100
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error marking task as successful: {e}")
        
        except Exception as e:
            logger.error(f"Task {task.task_id} failed on agent {agent.instance_id}: {e}")
            
            try:
                agent.failed_tasks += 1
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = datetime.utcnow()
                
                # Update success rate
                agent.success_rate = (agent.successful_tasks / agent.total_tasks) * 100
                db.session.commit()
            except Exception as db_e:
                db.session.rollback()
                logger.error(f"Error marking task as failed: {db_e}")
        
        finally:
            # Update agent status
            try:
                agent.current_load -= 1
                if agent.current_load == 0:
                    agent.status = 'idle'
                
                # Update response time
                response_time = time.time() - start_time
                task.processing_time = response_time
                agent.avg_response_time = (
                    (agent.avg_response_time * (agent.total_tasks - 1) + response_time) /
                    agent.total_tasks
                )
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating final agent status: {e}")
            
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            # Update system metrics
            self._update_system_metrics()
    
    def _execute_agent_task(self, task: TaskRequest, agent: AgentInstance) -> str:
        """Execute the actual agent task using specialized pools"""
        pool_name = agent.pool_name
        
        if pool_name == 'healthcare':
            return self.specialized_pools.process_healthcare_task(task.query)
        elif pool_name == 'financial':
            return self.specialized_pools.process_financial_task(task.query)
        elif pool_name == 'sports':
            return self.specialized_pools.process_sports_task(task.query)
        elif pool_name == 'business':
            return self.specialized_pools.process_business_task(task.query)
        else:
            return self.specialized_pools.process_general_task(task.query)
    
    def _start_health_monitor(self):
        """Start the health monitoring system"""
        from app import app
        
        def health_check():
            with app.app_context():
                while self.running:
                    try:
                        agents = db.session.query(AgentInstance).all()
                        for agent in agents:
                            self._check_agent_health(agent)
                        
                        # Check if we need to scale
                        self._check_scaling_needs()
                        
                        time.sleep(self.health_check_interval)
                    
                    except Exception as e:
                        logger.error(f"Error in health monitor: {e}")
        
        threading.Thread(target=health_check, daemon=True).start()
        logger.info("Health monitor started")
    
    def _check_agent_health(self, agent: AgentInstance):
        """Check individual agent health"""
        try:
            agent.last_health_check = datetime.utcnow()
            
            # Mark agent as failed if success rate is too low
            if agent.total_tasks > 10 and agent.success_rate < 70:
                agent.status = 'failed'
                logger.warning(f"Agent {agent.instance_id} marked as failed (success rate: {agent.success_rate}%)")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating agent health: {e}")
    
    def _start_auto_scaler(self):
        """Start the auto-scaling system"""
        from app import app
        
        def auto_scale():
            with app.app_context():
                while self.running:
                    try:
                        self._check_scaling_needs()
                        time.sleep(60)  # Check every minute
                    
                    except Exception as e:
                        logger.error(f"Error in auto-scaler: {e}")
        
        threading.Thread(target=auto_scale, daemon=True).start()
        logger.info("Auto-scaler started")
    
    def _check_scaling_needs(self):
        """Check if we need to scale agent pools up or down"""
        for pool_name in self.agent_pools.keys():
            active_agents = db.session.query(AgentInstance).filter_by(
                pool_name=pool_name
            ).filter(
                AgentInstance.status.in_(['idle', 'busy'])
            ).all()
            
            busy_agents = [a for a in active_agents if a.status == 'busy']
            idle_agents = [a for a in active_agents if a.status == 'idle']
            
            # Scale up if all agents are busy and we have pending tasks
            if len(busy_agents) == len(active_agents) and len(active_agents) < self.max_agents_per_pool:
                if not self.task_queue.empty():
                    try:
                        new_agent = self._create_agent_instance(pool_name)
                        db.session.add(new_agent)
                        db.session.commit()
                        logger.info(f"Scaled up {pool_name} pool: added {new_agent.instance_id}")
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error scaling up {pool_name} pool: {e}")
            
            # Scale down if we have too many idle agents
            elif len(idle_agents) > 2 and len(active_agents) > 2:
                agent_to_remove = idle_agents[0]
                try:
                    db.session.delete(agent_to_remove)
                    db.session.commit()
                    logger.info(f"Scaled down {pool_name} pool: removed {agent_to_remove.instance_id}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error scaling down {pool_name} pool: {e}")
    
    def _update_system_metrics(self):
        """Update system-wide metrics"""
        try:
            agents = db.session.query(AgentInstance).all()
            tasks = db.session.query(TaskRequest).all()
            
            total_agents = len(agents)
            active_agents = len([a for a in agents if a.status in ['idle', 'busy']])
            idle_agents = len([a for a in agents if a.status == 'idle'])
            failed_agents = len([a for a in agents if a.status == 'failed'])
            
            total_requests = len(tasks)
            successful_requests = len([t for t in tasks if t.status == 'completed'])
            failed_requests = len([t for t in tasks if t.status == 'failed'])
            
            avg_response_time = 0.0
            if successful_requests > 0:
                response_times = [t.processing_time for t in tasks if t.processing_time]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
            
            # Save metrics to database
            try:
                metrics = SystemMetrics()
                metrics.total_agents = total_agents
                metrics.active_agents = active_agents
                metrics.idle_agents = idle_agents
                metrics.failed_agents = failed_agents
                metrics.total_requests = total_requests
                metrics.successful_requests = successful_requests
                metrics.failed_requests = failed_requests
                metrics.avg_response_time = avg_response_time
                metrics.peak_concurrent_requests = len(self.active_tasks)
                metrics.api_usage = {'openai': 0, 'anthropic': 0}  # TODO: Track actual usage
                db.session.add(metrics)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error saving metrics: {e}")
        
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        agents = db.session.query(AgentInstance).all()
        tasks = db.session.query(TaskRequest).all()
        
        return {
            'total_agents': len(agents),
            'active_agents': len([a for a in agents if a.status in ['idle', 'busy']]),
            'idle_agents': len([a for a in agents if a.status == 'idle']),
            'busy_agents': len([a for a in agents if a.status == 'busy']),
            'failed_agents': len([a for a in agents if a.status == 'failed']),
            'pending_tasks': len([t for t in tasks if t.status == 'pending']),
            'processing_tasks': len([t for t in tasks if t.status == 'processing']),
            'completed_tasks': len([t for t in tasks if t.status == 'completed']),
            'failed_tasks': len([t for t in tasks if t.status == 'failed']),
            'uptime': str(datetime.now() - self.start_time),
            'is_running': self.running
        }

# Global instance - initialize in app context
master_controller = None

def get_master_controller():
    """Get or initialize the master controller"""
    global master_controller
    if master_controller is None:
        master_controller = AgentMasterController()
    return master_controller
