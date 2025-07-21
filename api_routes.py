"""
API routes for external integrations and programmatic access
"""

from flask import request, jsonify
from app import app, db
from models import TaskRequest, AgentInstance, SystemMetrics
from agent_master_controller import master_controller
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# API Authentication (simplified for demo)
def require_api_key():
    """Simple API key authentication"""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != 'demo-api-key':  # In production, use proper authentication
        return False
    return True

@app.route('/api/v1/health')
def api_health():
    """API health check endpoint"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        
        # Get system status
        system_status = master_controller.get_system_status()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'system_status': system_status
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/v1/tasks', methods=['POST'])
def api_submit_task():
    """Submit a task via API"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        # Extract parameters
        query = data['query']
        priority = data.get('priority', 5)
        capabilities = data.get('required_capabilities')
        user_id = data.get('user_id')
        
        # Validate priority
        if not isinstance(priority, int) or priority < 1 or priority > 10:
            return jsonify({'error': 'Priority must be an integer between 1 and 10'}), 400
        
        # Submit task
        task_id = master_controller.submit_task(
            query=query,
            user_id=user_id,
            priority=priority,
            required_capabilities=capabilities
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'timestamp': datetime.utcnow().isoformat(),
            'estimated_completion': (datetime.utcnow() + timedelta(seconds=30)).isoformat()
        }), 201
    
    except Exception as e:
        logger.error(f"API task submission error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tasks/<task_id>')
def api_get_task(task_id):
    """Get task status and results"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    task = db.session.query(TaskRequest).filter_by(task_id=task_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Get agent info if assigned
    agent_info = None
    if task.agent_id:
        agent = db.session.query(AgentInstance).get(task.agent_id)
        if agent:
            agent_info = {
                'agent_id': agent.instance_id,
                'pool': agent.pool_name,
                'type': agent.agent_type
            }
    
    return jsonify({
        'task_id': task.task_id,
        'status': task.status,
        'query': task.query,
        'result': task.result,
        'error_message': task.error_message,
        'priority': task.priority,
        'required_capabilities': task.required_capabilities,
        'created_at': task.created_at.isoformat(),
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'processing_time': task.processing_time,
        'agent': agent_info
    })

@app.route('/api/v1/tasks')
def api_list_tasks():
    """List tasks with filtering and pagination"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get query parameters
    status = request.args.get('status')
    pool = request.args.get('pool')
    limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 per request
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = TaskRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    if pool:
        query = query.join(AgentInstance).filter(AgentInstance.pool_name == pool)
    
    # Apply pagination
    tasks = query.order_by(TaskRequest.created_at.desc()).offset(offset).limit(limit).all()
    total_count = query.count()
    
    # Format results
    task_list = []
    for task in tasks:
        task_data = {
            'task_id': task.task_id,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'processing_time': task.processing_time
        }
        task_list.append(task_data)
    
    return jsonify({
        'tasks': task_list,
        'total_count': total_count,
        'limit': limit,
        'offset': offset,
        'has_more': (offset + limit) < total_count
    })

@app.route('/api/v1/agents')
def api_list_agents():
    """List all agents and their status"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    agents = db.session.query(AgentInstance).all()
    
    agent_list = []
    for agent in agents:
        agent_data = {
            'agent_id': agent.instance_id,
            'pool_name': agent.pool_name,
            'agent_type': agent.agent_type,
            'status': agent.status,
            'current_load': agent.current_load,
            'max_capacity': agent.max_capacity,
            'success_rate': agent.success_rate,
            'avg_response_time': agent.avg_response_time,
            'total_tasks': agent.total_tasks,
            'successful_tasks': agent.successful_tasks,
            'failed_tasks': agent.failed_tasks,
            'created_at': agent.created_at.isoformat(),
            'last_health_check': agent.last_health_check.isoformat() if agent.last_health_check else None
        }
        agent_list.append(agent_data)
    
    return jsonify({
        'agents': agent_list,
        'total_count': len(agent_list)
    })

@app.route('/api/v1/agents/<pool_name>')
def api_get_pool_agents(pool_name):
    """Get agents for a specific pool"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    if pool_name not in ['healthcare', 'financial', 'sports', 'business', 'general']:
        return jsonify({'error': 'Invalid pool name'}), 400
    
    agents = AgentInstance.query.filter_by(pool_name=pool_name).all()
    
    agent_list = []
    for agent in agents:
        agent_data = {
            'agent_id': agent.instance_id,
            'status': agent.status,
            'current_load': agent.current_load,
            'max_capacity': agent.max_capacity,
            'success_rate': agent.success_rate,
            'avg_response_time': agent.avg_response_time,
            'total_tasks': agent.total_tasks,
            'last_health_check': agent.last_health_check.isoformat() if agent.last_health_check else None
        }
        agent_list.append(agent_data)
    
    # Pool statistics
    pool_stats = {
        'total_agents': len(agents),
        'active_agents': len([a for a in agents if a.status in ['idle', 'busy']]),
        'idle_agents': len([a for a in agents if a.status == 'idle']),
        'busy_agents': len([a for a in agents if a.status == 'busy']),
        'failed_agents': len([a for a in agents if a.status == 'failed']),
        'avg_success_rate': sum(a.success_rate for a in agents) / len(agents) if agents else 0,
        'avg_response_time': sum(a.avg_response_time for a in agents) / len(agents) if agents else 0
    }
    
    return jsonify({
        'pool_name': pool_name,
        'agents': agent_list,
        'pool_stats': pool_stats
    })

@app.route('/api/v1/metrics')
def api_get_metrics():
    """Get system metrics and statistics"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get recent metrics
    hours_back = int(request.args.get('hours', 24))
    since = datetime.utcnow() - timedelta(hours=hours_back)
    
    metrics = db.session.query(SystemMetrics).filter(
        SystemMetrics.timestamp >= since
    ).order_by(SystemMetrics.timestamp.desc()).all()
    
    # Current system status
    system_status = master_controller.get_system_status()
    
    # Format metrics
    metrics_data = []
    for metric in metrics:
        metric_data = {
            'timestamp': metric.timestamp.isoformat(),
            'total_agents': metric.total_agents,
            'active_agents': metric.active_agents,
            'idle_agents': metric.idle_agents,
            'failed_agents': metric.failed_agents,
            'total_requests': metric.total_requests,
            'successful_requests': metric.successful_requests,
            'failed_requests': metric.failed_requests,
            'avg_response_time': metric.avg_response_time,
            'peak_concurrent_requests': metric.peak_concurrent_requests
        }
        metrics_data.append(metric_data)
    
    return jsonify({
        'current_status': system_status,
        'historical_metrics': metrics_data,
        'timeframe_hours': hours_back
    })

@app.route('/api/v1/capabilities')
def api_get_capabilities():
    """Get available agent capabilities"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    from agent_pools import SpecializedAgentPools
    from ai_providers import AIProviderManager
    
    ai_provider = AIProviderManager()
    specialized_pools = SpecializedAgentPools(ai_provider)
    
    capabilities = {}
    for pool_name in ['healthcare', 'financial', 'sports', 'business', 'general']:
        capabilities[pool_name] = specialized_pools.get_pool_capabilities(pool_name)
    
    # Get available AI providers
    available_providers = ai_provider.get_available_providers()
    provider_health = ai_provider.health_check()
    
    return jsonify({
        'agent_pools': capabilities,
        'ai_providers': {
            'available': available_providers,
            'health_status': provider_health
        },
        'supported_operations': [
            'task_submission',
            'real_time_monitoring',
            'agent_scaling',
            'health_monitoring',
            'conversation_context',
            'priority_queuing'
        ]
    })

@app.route('/api/v1/system/status')
def api_system_status():
    """Get comprehensive system status"""
    if not require_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        # Get master controller status
        controller_status = master_controller.get_system_status()
        
        # Get database status
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        db_status = 'healthy'
        
        # Get AI provider status
        from ai_providers import AIProviderManager
        ai_manager = AIProviderManager()
        provider_health = ai_manager.health_check()
        
        # Get recent performance metrics
        latest_metric = SystemMetrics.query.order_by(
            SystemMetrics.timestamp.desc()
        ).first()
        
        return jsonify({
            'overall_status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'agent_controller': 'healthy' if controller_status['is_running'] else 'unhealthy',
                'database': db_status,
                'ai_providers': provider_health
            },
            'system_metrics': controller_status,
            'performance': {
                'avg_response_time': latest_metric.avg_response_time if latest_metric else 0,
                'uptime': controller_status['uptime']
            }
        })
    
    except Exception as e:
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Error handlers for API
@app.errorhandler(404)
def api_not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return error

@app.errorhandler(500)
def api_internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return error
