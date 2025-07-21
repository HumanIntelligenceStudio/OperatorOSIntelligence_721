"""
Admin routes for system management and monitoring
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import AgentInstance, TaskRequest, UserSession, SystemMetrics, User
from agent_master_controller import master_controller
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard with comprehensive system overview"""
    # System overview metrics
    system_metrics = {
        'total_agents': db.session.query(AgentInstance).count(),
        'active_agents': db.session.query(AgentInstance).filter(
            AgentInstance.status.in_(['idle', 'busy'])
        ).count(),
        'failed_agents': db.session.query(AgentInstance).filter_by(status='failed').count(),
        'total_tasks': db.session.query(TaskRequest).count(),
        'completed_tasks': db.session.query(TaskRequest).filter_by(status='completed').count(),
        'failed_tasks': db.session.query(TaskRequest).filter_by(status='failed').count(),
        'active_sessions': db.session.query(UserSession).filter_by(is_active=True).count()
    }
    
    # Get recent system metrics from database
    recent_metrics = db.session.query(SystemMetrics).order_by(
        SystemMetrics.timestamp.desc()
    ).limit(24).all()  # Last 24 data points
    
    # Agent pool breakdown
    agent_pools = {}
    for pool_name in ['healthcare', 'financial', 'sports', 'business', 'general']:
        agents = db.session.query(AgentInstance).filter_by(pool_name=pool_name).all()
        total_tasks = sum(a.total_tasks for a in agents)
        successful_tasks = sum(a.successful_tasks for a in agents)
        
        agent_pools[pool_name] = {
            'total_agents': len(agents),
            'active_agents': len([a for a in agents if a.status in ['idle', 'busy']]),
            'failed_agents': len([a for a in agents if a.status == 'failed']),
            'total_tasks': total_tasks,
            'success_rate': (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'avg_response_time': sum(a.avg_response_time for a in agents) / len(agents) if agents else 0
        }
    
    # Performance metrics
    performance_metrics = {
        'system_uptime': str(datetime.utcnow() - master_controller.start_time),
        'avg_task_completion_time': 0,
        'tasks_per_hour': 0,
        'error_rate': 0
    }
    
    # Calculate average completion time
    completed_tasks = db.session.query(TaskRequest).filter(
        TaskRequest.status == 'completed',
        TaskRequest.processing_time.isnot(None)
    ).all()
    
    if completed_tasks:
        performance_metrics['avg_task_completion_time'] = sum(
            t.processing_time for t in completed_tasks
        ) / len(completed_tasks)
    
    # Calculate tasks per hour (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_tasks = TaskRequest.query.filter(
        TaskRequest.created_at >= yesterday
    ).count()
    performance_metrics['tasks_per_hour'] = recent_tasks / 24
    
    # Calculate error rate
    if system_metrics['total_tasks'] > 0:
        performance_metrics['error_rate'] = (
            system_metrics['failed_tasks'] / system_metrics['total_tasks'] * 100
        )
    
    return render_template('admin.html',
                         system_metrics=system_metrics,
                         recent_metrics=recent_metrics,
                         agent_pools=agent_pools,
                         performance_metrics=performance_metrics)

@app.route('/admin/agents')
def admin_agents():
    """Admin page for agent management"""
    # Get all agents with detailed information
    agents = AgentInstance.query.order_by(
        AgentInstance.pool_name, 
        AgentInstance.created_at
    ).all()
    
    # Group agents by pool
    agents_by_pool = {}
    for agent in agents:
        if agent.pool_name not in agents_by_pool:
            agents_by_pool[agent.pool_name] = []
        agents_by_pool[agent.pool_name].append(agent)
    
    return render_template('admin_agents.html', 
                         agents_by_pool=agents_by_pool,
                         total_agents=len(agents))

@app.route('/admin/agents/<int:agent_id>/restart', methods=['POST'])
def admin_restart_agent(agent_id):
    """Restart a specific agent"""
    agent = AgentInstance.query.get_or_404(agent_id)
    
    try:
        with db.session.begin():
            agent.status = 'idle'
            agent.current_load = 0
            agent.last_health_check = datetime.utcnow()
        
        flash(f'Agent {agent.instance_id} restarted successfully', 'success')
        logger.info(f"Admin restarted agent: {agent.instance_id}")
    
    except Exception as e:
        flash(f'Error restarting agent: {str(e)}', 'error')
        logger.error(f"Error restarting agent {agent.instance_id}: {e}")
    
    return redirect(url_for('admin_agents'))

@app.route('/admin/agents/<int:agent_id>/delete', methods=['POST'])
def admin_delete_agent(agent_id):
    """Delete a specific agent"""
    agent = AgentInstance.query.get_or_404(agent_id)
    
    try:
        with db.session.begin():
            db.session.delete(agent)
        
        flash(f'Agent {agent.instance_id} deleted successfully', 'success')
        logger.info(f"Admin deleted agent: {agent.instance_id}")
    
    except Exception as e:
        flash(f'Error deleting agent: {str(e)}', 'error')
        logger.error(f"Error deleting agent {agent.instance_id}: {e}")
    
    return redirect(url_for('admin_agents'))

@app.route('/admin/pools/<pool_name>/scale', methods=['POST'])
def admin_scale_pool(pool_name):
    """Scale an agent pool up or down"""
    action = request.form.get('action')  # 'scale_up' or 'scale_down'
    
    if pool_name not in ['healthcare', 'financial', 'sports', 'business', 'general']:
        flash('Invalid pool name', 'error')
        return redirect(url_for('admin_agents'))
    
    try:
        if action == 'scale_up':
            # Create new agent
            new_agent = master_controller._create_agent_instance(pool_name)
            with db.session.begin():
                db.session.add(new_agent)
            
            flash(f'Scaled up {pool_name} pool: added {new_agent.instance_id}', 'success')
            logger.info(f"Admin scaled up {pool_name} pool")
        
        elif action == 'scale_down':
            # Remove an idle agent
            idle_agent = db.session.query(AgentInstance).filter_by(
                pool_name=pool_name,
                status='idle'
            ).first()
            
            if idle_agent:
                with db.session.begin():
                    db.session.delete(idle_agent)
                
                flash(f'Scaled down {pool_name} pool: removed {idle_agent.instance_id}', 'success')
                logger.info(f"Admin scaled down {pool_name} pool")
            else:
                flash(f'No idle agents available to remove from {pool_name} pool', 'warning')
    
    except Exception as e:
        flash(f'Error scaling {pool_name} pool: {str(e)}', 'error')
        logger.error(f"Error scaling {pool_name} pool: {e}")
    
    return redirect(url_for('admin_agents'))

@app.route('/admin/tasks')
def admin_tasks():
    """Admin task management page"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    pool_filter = request.args.get('pool', 'all')
    date_filter = request.args.get('date', 'all')
    
    # Build query
    query = db.session.query(TaskRequest)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if pool_filter != 'all':
        query = query.join(AgentInstance).filter(
            AgentInstance.pool_name == pool_filter
        )
    
    if date_filter == 'today':
        today = datetime.utcnow().date()
        query = query.filter(
            TaskRequest.created_at >= today
        )
    elif date_filter == 'week':
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(
            TaskRequest.created_at >= week_ago
        )
    
    # Get tasks with pagination
    page = request.args.get('page', 1, type=int)
    tasks = query.order_by(TaskRequest.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Task statistics
    task_stats = {
        'total': db.session.query(TaskRequest).count(),
        'pending': db.session.query(TaskRequest).filter_by(status='pending').count(),
        'processing': db.session.query(TaskRequest).filter_by(status='processing').count(),
        'completed': db.session.query(TaskRequest).filter_by(status='completed').count(),
        'failed': db.session.query(TaskRequest).filter_by(status='failed').count()
    }
    
    return render_template('admin_tasks.html',
                         tasks=tasks,
                         task_stats=task_stats,
                         status_filter=status_filter,
                         pool_filter=pool_filter,
                         date_filter=date_filter)

@app.route('/admin/tasks/<task_id>/retry', methods=['POST'])
def admin_retry_task(task_id):
    """Retry a failed task"""
    task = db.session.query(TaskRequest).filter_by(task_id=task_id).first()
    
    if task.status != 'failed':
        flash('Only failed tasks can be retried', 'warning')
        return redirect(url_for('admin_tasks'))
    
    try:
        # Reset task status and resubmit
        with db.session.begin():
            task.status = 'pending'
            task.error_message = None
            task.agent_id = None
        
        # Resubmit to master controller
        master_controller.task_queue.put((task.priority, datetime.utcnow().timestamp(), task.task_id))
        
        flash(f'Task {task_id} resubmitted for processing', 'success')
        logger.info(f"Admin retried task: {task_id}")
    
    except Exception as e:
        flash(f'Error retrying task: {str(e)}', 'error')
        logger.error(f"Error retrying task {task_id}: {e}")
    
    return redirect(url_for('admin_tasks'))

@app.route('/admin/system')
def admin_system():
    """System configuration and settings"""
    # Get master controller status
    controller_status = master_controller.get_system_status()
    
    # Get configuration settings
    system_config = {
        'max_agents_per_pool': master_controller.max_agents_per_pool,
        'health_check_interval': master_controller.health_check_interval,
        'auto_scaling_enabled': True,  # TODO: Make this configurable
        'recovery_enabled': True
    }
    
    # Get AI provider status
    from ai_providers import AIProviderManager
    ai_manager = AIProviderManager()
    provider_status = ai_manager.health_check()
    provider_usage = ai_manager.get_usage_stats()
    
    return render_template('admin_system.html',
                         controller_status=controller_status,
                         system_config=system_config,
                         provider_status=provider_status,
                         provider_usage=provider_usage)

@app.route('/admin/logs')
def admin_logs():
    """System logs viewer"""
    # In a real implementation, you'd read from log files
    # For now, we'll show a placeholder
    logs = [
        {
            'timestamp': datetime.utcnow(),
            'level': 'INFO',
            'message': 'System initialized successfully',
            'component': 'AgentMasterController'
        },
        {
            'timestamp': datetime.utcnow(),
            'level': 'INFO',
            'message': 'Health monitor started',
            'component': 'HealthMonitor'
        }
    ]
    
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/api/metrics')
def admin_api_metrics():
    """API endpoint for real-time metrics"""
    # Get latest system metrics
    latest_metric = db.session.query(SystemMetrics).order_by(
        SystemMetrics.timestamp.desc()
    ).first()
    
    # Get agent statistics
    agents = db.session.query(AgentInstance).all()
    agent_stats = {
        'total': len(agents),
        'active': len([a for a in agents if a.status in ['idle', 'busy']]),
        'idle': len([a for a in agents if a.status == 'idle']),
        'busy': len([a for a in agents if a.status == 'busy']),
        'failed': len([a for a in agents if a.status == 'failed'])
    }
    
    # Get task statistics
    task_stats = {
        'pending': db.session.query(TaskRequest).filter_by(status='pending').count(),
        'processing': db.session.query(TaskRequest).filter_by(status='processing').count(),
        'completed': db.session.query(TaskRequest).filter_by(status='completed').count(),
        'failed': db.session.query(TaskRequest).filter_by(status='failed').count()
    }
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'agent_stats': agent_stats,
        'task_stats': task_stats,
        'system_metrics': {
            'avg_response_time': latest_metric.avg_response_time if latest_metric else 0,
            'success_rate': (
                (task_stats['completed'] / 
                 (task_stats['completed'] + task_stats['failed']) * 100)
                if (task_stats['completed'] + task_stats['failed']) > 0 else 100
            )
        }
    })
