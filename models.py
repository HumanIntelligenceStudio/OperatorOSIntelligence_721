from app import db
from datetime import datetime
from sqlalchemy import Text, JSON
import uuid

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    sessions = db.relationship('UserSession', backref='user', lazy=True)
    tasks = db.relationship('TaskRequest', backref='user', lazy=True)

class AgentInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    agent_type = db.Column(db.String(32), nullable=False)
    pool_name = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(16), nullable=False, default='idle')  # idle, busy, failed, initializing
    current_load = db.Column(db.Integer, default=0)
    max_capacity = db.Column(db.Integer, default=3)
    success_rate = db.Column(db.Float, default=100.0)
    avg_response_time = db.Column(db.Float, default=0.0)
    last_health_check = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_tasks = db.Column(db.Integer, default=0)
    successful_tasks = db.Column(db.Integer, default=0)
    failed_tasks = db.Column(db.Integer, default=0)
    
    # Relationships
    tasks = db.relationship('TaskRequest', backref='agent', lazy=True)

class TaskRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    query = db.Column(Text, nullable=False)
    required_capabilities = db.Column(JSON)
    priority = db.Column(db.Integer, default=5)
    status = db.Column(db.String(16), default='pending')  # pending, processing, completed, failed
    result = db.Column(Text)
    error_message = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    processing_time = db.Column(db.Float)
    timeout = db.Column(db.Integer, default=30)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('user_session.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent_instance.id'))

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    conversation_context = db.Column(JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    tasks = db.relationship('TaskRequest', backref='session', lazy=True)

class SystemMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_agents = db.Column(db.Integer, default=0)
    active_agents = db.Column(db.Integer, default=0)
    idle_agents = db.Column(db.Integer, default=0)
    failed_agents = db.Column(db.Integer, default=0)
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float, default=0.0)
    peak_concurrent_requests = db.Column(db.Integer, default=0)
    api_usage = db.Column(JSON, default=dict)
    user_satisfaction = db.Column(db.Float, default=0.0)

class AgentPool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pool_name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(Text)
    capabilities = db.Column(JSON)
    max_agents = db.Column(db.Integer, default=10)
    current_agents = db.Column(db.Integer, default=0)
    auto_scale_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
