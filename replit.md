# OperatorOS - Enterprise AI Agent Orchestration Platform

## Overview
OperatorOS is a sophisticated enterprise-grade multi-agent AI orchestration system designed to manage and coordinate specialized AI agents across different domains. The platform provides intelligent routing, auto-scaling, health monitoring, and real-time analytics for AI agent pools in healthcare, financial, sports, business, and general-purpose domains.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### High-Level Architecture
The system follows a microservices-inspired architecture with centralized orchestration:

- **Flask Web Application**: Main web interface and API endpoints
- **Agent Master Controller**: Core orchestration engine with enterprise-grade features
- **Specialized Agent Pools**: Domain-specific AI agents with tailored capabilities
- **Task Processing Engine**: Priority-based queue management and load balancing
- **Health Monitoring System**: Real-time health checks and automatic recovery
- **Multi-Provider AI Integration**: Support for OpenAI, Anthropic, and other AI providers

### Key Design Decisions
1. **Centralized Orchestration**: Single master controller manages all agent pools for consistent resource allocation and monitoring
2. **Domain Specialization**: Separate agent pools for different domains (healthcare, financial, sports, business, general) to ensure optimal performance
3. **Database-First Approach**: All system state, metrics, and task history stored in relational database for persistence and analytics
4. **Multi-Provider AI Support**: Abstraction layer for multiple AI providers to ensure reliability and cost optimization

## Key Components

### 1. Flask Web Application (app.py)
- **Purpose**: Main application entry point and configuration
- **Technologies**: Flask, SQLAlchemy, ProxyFix for production deployment
- **Features**: Database connection pooling, security configurations, automatic table creation

### 2. Agent Master Controller (agent_master_controller.py)
- **Purpose**: Enterprise-grade agent coordination and management
- **Features**: Auto-scaling, intelligent routing, real-time monitoring, task queue management
- **Architecture**: Thread-safe with concurrent task processing using ThreadPoolExecutor

### 3. Database Models (models.py)
- **User Management**: User accounts with admin capabilities
- **Agent Tracking**: AgentInstance model for monitoring agent health and performance
- **Task Management**: TaskRequest model with priority queuing and status tracking
- **System Metrics**: SystemMetrics for historical performance data
- **Session Management**: UserSession for conversation context and user activity

### 4. Specialized Agent Pools (agent_pools.py)
- **Healthcare**: Medical analysis, symptom assessment, medication guidance
- **Financial**: Market analysis, investment insights, financial planning
- **Sports**: Sports analytics, betting education, performance analysis
- **Business**: Process automation, workflow optimization, business intelligence
- **General**: Catch-all for queries not matching specialized domains

### 5. AI Provider Management (ai_providers.py)
- **Multi-Provider Support**: OpenAI (GPT-4o), Anthropic (Claude Sonnet 4)
- **Intelligent Routing**: Automatic provider selection based on availability and cost
- **Usage Tracking**: Request and token usage monitoring per provider

### 6. Task Processing System (task_processor.py)
- **Priority Queue**: Priority-based task scheduling with load balancing
- **Concurrent Processing**: ThreadPoolExecutor for parallel task execution
- **Performance Metrics**: Processing time tracking and success rate monitoring

### 7. Health Monitoring (health_monitor.py)
- **Real-time Monitoring**: Continuous health checks for agents and system resources
- **Automatic Recovery**: Failed agent detection and restart capabilities
- **Alert System**: Threshold-based alerting for system issues

## Data Flow

### Task Submission Flow
1. User submits task via web interface or API
2. Task stored in database with priority and metadata
3. Agent Master Controller analyzes task and determines optimal agent pool
4. Task routed to appropriate specialized agent pool
5. AI provider called with domain-specific prompts
6. Response processed and stored in database
7. User notified of completion with results

### Health Monitoring Flow
1. Health Monitor continuously checks agent status
2. System metrics collected (CPU, memory, response times)
3. Failed agents automatically flagged and restarted
4. Performance data stored for analytics and trending
5. Admin alerts triggered for critical issues

### Real-time Updates Flow
1. Frontend JavaScript polls for updates
2. WebSocket fallback for real-time communication
3. Dashboard charts updated with latest metrics
4. Agent pool status reflected in real-time

## External Dependencies

### AI Providers
- **OpenAI API**: GPT-4o for general-purpose and business tasks
- **Anthropic API**: Claude Sonnet 4 for healthcare and financial analysis

### Financial Integrations
- **Plaid API**: Banking and financial account integration
- **Alpha Vantage API**: Stock market data and analysis
- **Polygon API**: Real-time financial market data

### Sports Data
- **Sports API**: Live sports scores and statistics
- **Odds API**: Sports betting odds and analytics

### System Monitoring
- **psutil**: System resource monitoring (CPU, memory)
- **Database**: PostgreSQL for production, SQLite for development

## Deployment Strategy

### Production Configuration
- **WSGI Server**: Configured with ProxyFix for reverse proxy deployment
- **Database Pooling**: Connection pooling with automatic reconnection
- **Security**: Session cookies with secure flags, CSRF protection
- **Environment Variables**: All sensitive configuration externalized

### Scalability Considerations
- **Agent Auto-scaling**: Automatic scaling of agent pools based on demand
- **Database Optimization**: Indexed queries and connection pooling
- **Caching**: Metrics caching to reduce database load
- **Load Balancing**: Thread-based concurrent processing

### Monitoring and Observability
- **Comprehensive Logging**: Structured logging throughout the application
- **Metrics Collection**: Performance metrics stored for historical analysis
- **Health Checks**: API endpoints for monitoring system health
- **Admin Dashboard**: Real-time system monitoring and management interface

### Security Features
- **API Authentication**: API key-based authentication for external access
- **Session Management**: Secure session handling with proper cookie settings
- **Input Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Graceful error handling without information disclosure