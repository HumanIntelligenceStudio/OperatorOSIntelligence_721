"""
Task Processor - Handles task execution and queue management
Priority-based task queuing with load balancing
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import queue

from app import db
from models import TaskRequest, AgentInstance

logger = logging.getLogger(__name__)

class TaskProcessor:
    """Handles task processing and queue management"""
    
    def __init__(self, max_workers=20):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.PriorityQueue()
        self.running = False
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'avg_processing_time': 0.0
        }
        
    def start(self):
        """Start the task processor"""
        if self.running:
            return
        
        self.running = True
        self._start_queue_processor()
        logger.info("Task processor started")
    
    def stop(self):
        """Stop the task processor"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Task processor stopped")
    
    def submit_task(self, task_id: str, priority: int = 5):
        """Submit a task to the processing queue"""
        timestamp = time.time()
        self.task_queue.put((priority, timestamp, task_id))
        logger.debug(f"Task {task_id} submitted with priority {priority}")
    
    def _start_queue_processor(self):
        """Start the queue processing thread"""
        def process_queue():
            while self.running:
                try:
                    # Get task from queue with timeout
                    priority, timestamp, task_id = self.task_queue.get(timeout=1.0)
                    
                    # Submit task for processing
                    self.executor.submit(self._process_single_task, task_id)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in queue processor: {e}")
        
        threading.Thread(target=process_queue, daemon=True).start()
    
    def _process_single_task(self, task_id: str):
        """Process a single task"""
        start_time = time.time()
        
        try:
            # Get task from database
            task = TaskRequest.query.filter_by(task_id=task_id).first()
            if not task:
                logger.error(f"Task {task_id} not found in database")
                return
            
            # Find available agent
            agent = self._find_available_agent(task.required_capabilities)
            if not agent:
                # No agents available, requeue task
                self.task_queue.put((task.priority, time.time(), task_id))
                time.sleep(1)  # Wait before retrying
                return
            
            # Update task status
            with db.session.begin():
                task.status = 'processing'
                task.agent_id = agent.id
                agent.status = 'busy'
                agent.current_load += 1
            
            # Process the task
            result = self._execute_task(task, agent)
            
            # Update task with result
            processing_time = time.time() - start_time
            with db.session.begin():
                task.status = 'completed'
                task.result = result
                task.completed_at = datetime.utcnow()
                task.processing_time = processing_time
                
                # Update agent stats
                agent.total_tasks += 1
                agent.successful_tasks += 1
                agent.current_load -= 1
                if agent.current_load == 0:
                    agent.status = 'idle'
                
                # Update success rate
                agent.success_rate = (agent.successful_tasks / agent.total_tasks) * 100
                
                # Update response time
                agent.avg_response_time = (
                    (agent.avg_response_time * (agent.total_tasks - 1) + processing_time) /
                    agent.total_tasks
                )
            
            # Update processing stats
            self._update_processing_stats(processing_time, True)
            logger.info(f"Task {task_id} completed in {processing_time:.2f}s")
            
        except Exception as e:
            # Handle task failure
            processing_time = time.time() - start_time
            logger.error(f"Task {task_id} failed: {e}")
            
            try:
                with db.session.begin():
                    task = TaskRequest.query.filter_by(task_id=task_id).first()
                    if task:
                        task.status = 'failed'
                        task.error_message = str(e)
                        task.completed_at = datetime.utcnow()
                        task.processing_time = processing_time
                        
                        # Update agent stats if agent was assigned
                        if task.agent_id:
                            agent = AgentInstance.query.get(task.agent_id)
                            if agent:
                                agent.total_tasks += 1
                                agent.failed_tasks += 1
                                agent.current_load -= 1
                                if agent.current_load == 0:
                                    agent.status = 'idle'
                                
                                # Update success rate
                                agent.success_rate = (agent.successful_tasks / agent.total_tasks) * 100
                
                self._update_processing_stats(processing_time, False)
                
            except Exception as db_error:
                logger.error(f"Error updating failed task {task_id}: {db_error}")
    
    def _find_available_agent(self, required_capabilities: List[str]) -> Optional[AgentInstance]:
        """Find an available agent for the task"""
        # Determine target pool based on capabilities
        target_pool = 'general'
        
        # Map capabilities to pools
        capability_pool_map = {
            'medical_diagnosis': 'healthcare',
            'pharmacology_analysis': 'healthcare',
            'insurance_navigation': 'healthcare',
            'healthcare_finance': 'healthcare',
            'wellness_coaching': 'healthcare',
            'clinical_decision_support': 'healthcare',
            'wealth_optimization': 'financial',
            'debt_elimination': 'financial',
            'tax_strategy': 'financial',
            'retirement_planning': 'financial',
            'business_finance': 'financial',
            'market_intelligence': 'financial',
            'sports_prediction': 'sports',
            'market_education': 'sports',
            'fantasy_sports': 'sports',
            'compliance_monitoring': 'sports',
            'sports_content': 'sports',
            'analytics': 'sports',
            'process_automation': 'business',
            'workflow_optimization': 'business',
            'project_management': 'business',
            'team_coordination': 'business',
            'strategic_planning': 'business',
            'operations': 'business'
        }
        
        # Find the most specific pool
        for capability in required_capabilities:
            if capability in capability_pool_map:
                target_pool = capability_pool_map[capability]
                break
        
        # Find available agent in target pool
        agent = AgentInstance.query.filter_by(
            pool_name=target_pool,
            status='idle'
        ).filter(
            AgentInstance.current_load < AgentInstance.max_capacity
        ).order_by(
            AgentInstance.current_load,
            AgentInstance.success_rate.desc()
        ).first()
        
        # Fallback to general pool
        if not agent and target_pool != 'general':
            agent = AgentInstance.query.filter_by(
                pool_name='general',
                status='idle'
            ).filter(
                AgentInstance.current_load < AgentInstance.max_capacity
            ).order_by(
                AgentInstance.current_load,
                AgentInstance.success_rate.desc()
            ).first()
        
        return agent
    
    def _execute_task(self, task: TaskRequest, agent: AgentInstance) -> str:
        """Execute the task using the assigned agent"""
        # Import here to avoid circular imports
        from agent_pools import SpecializedAgentPools
        from ai_providers import AIProviderManager
        
        # Get AI provider and specialized pools
        ai_provider = AIProviderManager()
        specialized_pools = SpecializedAgentPools(ai_provider)
        
        # Route to appropriate agent pool
        pool_name = agent.pool_name
        
        if pool_name == 'healthcare':
            return specialized_pools.process_healthcare_task(task.query)
        elif pool_name == 'financial':
            return specialized_pools.process_financial_task(task.query)
        elif pool_name == 'sports':
            return specialized_pools.process_sports_task(task.query)
        elif pool_name == 'business':
            return specialized_pools.process_business_task(task.query)
        else:
            return specialized_pools.process_general_task(task.query)
    
    def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        self.processing_stats['total_processed'] += 1
        
        if success:
            self.processing_stats['successful'] += 1
        else:
            self.processing_stats['failed'] += 1
        
        # Update average processing time
        total = self.processing_stats['total_processed']
        current_avg = self.processing_stats['avg_processing_time']
        self.processing_stats['avg_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'queue_size': self.task_queue.qsize(),
            'running': self.running,
            'max_workers': self.max_workers,
            'stats': self.processing_stats.copy()
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        task = TaskRequest.query.filter_by(task_id=task_id).first()
        if not task:
            return None
        
        return {
            'task_id': task.task_id,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'processing_time': task.processing_time,
            'result': task.result,
            'error_message': task.error_message
        }
