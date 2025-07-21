"""
Main application routes for the OperatorOS web interface
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import TaskRequest, AgentInstance, UserSession, SystemMetrics
from agent_master_controller import get_master_controller
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    # Get system status
    system_status = get_master_controller().get_system_status()
    
    # Get recent tasks
    recent_tasks = db.session.query(TaskRequest).order_by(
        TaskRequest.created_at.desc()
    ).limit(5).all()
    
    # Get agent pool statistics
    agent_pools = {}
    for pool_name in ['healthcare', 'financial', 'sports', 'business', 'general']:
        agents = db.session.query(AgentInstance).filter_by(pool_name=pool_name).all()
        agent_pools[pool_name] = {
            'total': len(agents),
            'active': len([a for a in agents if a.status in ['idle', 'busy']]),
            'idle': len([a for a in agents if a.status == 'idle']),
            'busy': len([a for a in agents if a.status == 'busy']),
            'failed': len([a for a in agents if a.status == 'failed'])
        }
    
    return render_template('index.html', 
                         system_status=system_status,
                         recent_tasks=recent_tasks,
                         agent_pools=agent_pools)

@app.route('/dashboard')
def dashboard():
    """System dashboard with metrics"""
    # Get recent metrics
    recent_metrics = db.session.query(SystemMetrics).order_by(
        SystemMetrics.timestamp.desc()
    ).limit(20).all()
    
    # Get task statistics
    total_tasks = db.session.query(TaskRequest).count()
    completed_tasks = db.session.query(TaskRequest).filter_by(status='completed').count()
    failed_tasks = db.session.query(TaskRequest).filter_by(status='failed').count()
    pending_tasks = db.session.query(TaskRequest).filter_by(status='pending').count()
    
    # Get agent statistics
    agents = db.session.query(AgentInstance).all()
    agent_stats = {
        'total': len(agents),
        'active': len([a for a in agents if a.status in ['idle', 'busy']]),
        'idle': len([a for a in agents if a.status == 'idle']),
        'busy': len([a for a in agents if a.status == 'busy']),
        'failed': len([a for a in agents if a.status == 'failed'])
    }
    
    # Calculate success rate
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('dashboard.html',
                         recent_metrics=recent_metrics,
                         task_stats={
                             'total': total_tasks,
                             'completed': completed_tasks,
                             'failed': failed_tasks,
                             'pending': pending_tasks,
                             'success_rate': success_rate
                         },
                         agent_stats=agent_stats)

@app.route('/agent-pools')
def agent_pools():
    """Agent pools management page"""
    pools = {}
    
    for pool_name in ['healthcare', 'financial', 'sports', 'business', 'general']:
        agents = db.session.query(AgentInstance).filter_by(pool_name=pool_name).all()
        pools[pool_name] = {
            'agents': agents,
            'total': len(agents),
            'active': len([a for a in agents if a.status in ['idle', 'busy']]),
            'idle': len([a for a in agents if a.status == 'idle']),
            'busy': len([a for a in agents if a.status == 'busy']),
            'failed': len([a for a in agents if a.status == 'failed'])
        }
    
    return render_template('agent_pools.html', pools=pools)

@app.route('/submit-task', methods=['GET', 'POST'])
def submit_task():
    """Submit a new task for processing"""
    if request.method == 'POST':
        query = request.form.get('query')
        priority = int(request.form.get('priority', 5))
        
        if not query:
            flash('Please enter a query', 'error')
            return redirect(url_for('submit_task'))
        
        try:
            # Submit task to master controller
            task_id = get_master_controller().submit_task(
                query=query,
                priority=priority
            )
            
            flash(f'Task submitted successfully! Task ID: {task_id}', 'success')
            return redirect(url_for('task_status', task_id=task_id))
        
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            flash(f'Error submitting task: {str(e)}', 'error')
    
    return render_template('submit_task.html')

@app.route('/task/<task_id>')
def task_status(task_id):
    """View task status and results"""
    task = db.session.query(TaskRequest).filter_by(task_id=task_id).first()
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    # Get agent info if assigned
    agent = None
    if task.agent_id:
        agent = db.session.query(AgentInstance).get(task.agent_id)
    
    return render_template('task_status.html', task=task, agent=agent)

@app.route('/tasks')
def task_monitor():
    """Task monitoring page"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    pool_filter = request.args.get('pool', 'all')
    
    # Build query
    query = db.session.query(TaskRequest)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if pool_filter != 'all':
        query = query.join(AgentInstance).filter(
            AgentInstance.pool_name == pool_filter
        )
    
    # Get tasks with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    tasks_list = query.order_by(TaskRequest.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    total = query.count()
    
    # Create pagination object manually
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    tasks = Pagination(tasks_list, page, per_page, total)
    
    return render_template('task_monitor.html', 
                         tasks=tasks,
                         status_filter=status_filter,
                         pool_filter=pool_filter)

@app.route('/sessions')
def sessions():
    """User sessions management"""
    user_sessions = db.session.query(UserSession).filter_by(is_active=True).order_by(
        UserSession.last_activity.desc()
    ).all()
    
    return render_template('sessions.html', sessions=user_sessions)

@app.route('/health')
def health_check():
    """System health check endpoint"""
    try:
        # Check database
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        
        # Get system status
        system_status = get_master_controller().get_system_status()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system_status': system_status
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/demo/<demo_type>')
def demo_showcase(demo_type):
    """Showcase different agent capabilities"""
    demos = {
        'healthcare': {
            'title': 'Healthcare AI Assistant',
            'description': 'Advanced medical analysis and healthcare guidance',
            'examples': [
                'Analyze symptoms for potential conditions',
                'Medication interaction checking',
                'Insurance coverage navigation',
                'Wellness and lifestyle recommendations'
            ]
        },
        'financial': {
            'title': 'Financial AI Advisor',
            'description': 'Comprehensive financial analysis and planning',
            'examples': [
                'Investment portfolio optimization',
                'Market analysis and predictions',
                'Debt consolidation strategies',
                'Retirement planning guidance'
            ]
        },
        'sports': {
            'title': 'Sports Analytics Engine',
            'description': 'Advanced sports analysis and betting insights',
            'examples': [
                'Game outcome predictions',
                'Sports arbitrage opportunities',
                'Fantasy sports optimization',
                'Performance analytics'
            ]
        },
        'business': {
            'title': 'Business Automation Suite',
            'description': 'Enterprise workflow optimization and automation',
            'examples': [
                'Process automation design',
                'Workflow optimization',
                'Project management assistance',
                'Strategic planning support'
            ]
        }
    }
    
    if demo_type not in demos:
        flash('Demo type not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('demo_showcase.html', 
                         demo=demos[demo_type],
                         demo_type=demo_type)

@app.route('/api/submit', methods=['POST'])
def simple_api_submit():
    """Simple API endpoint for task submission (no auth required)"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        task_id = get_master_controller().submit_task(
            query=data['query'],
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"API task submission error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>')
def simple_api_task_status(task_id):
    """Simple API endpoint for task status"""
    task = db.session.query(TaskRequest).filter_by(task_id=task_id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'task_id': task.task_id,
        'status': task.status,
        'result': task.result,
        'error_message': task.error_message,
        'created_at': task.created_at.isoformat(),
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'processing_time': task.processing_time
    })

# Initialize the master controller when the app starts
def initialize_system():
    """Initialize the system on first request"""
    try:
        get_master_controller().start()
        logger.info("OperatorOS system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")

# Initialize system when module is imported
with app.app_context():
    initialize_system()
