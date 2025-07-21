/**
 * OperatorOS Real-time Communication Handler
 * Manages WebSocket connections, real-time updates, and live data synchronization
 */

class OperatorOSRealTime {
    constructor(options = {}) {
        this.options = {
            reconnectInterval: 5000,
            maxReconnectAttempts: 10,
            heartbeatInterval: 30000,
            updateThrottle: 1000,
            ...options
        };
        
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.lastHeartbeat = null;
        this.heartbeatTimer = null;
        this.updateQueue = [];
        this.updateTimer = null;
        this.listeners = {};
        
        this.init();
    }
    
    init() {
        try {
            this.setupEventListeners();
            this.startPollingFallback();
            console.log('OperatorOS Real-time system initialized');
        } catch (error) {
            console.error('Failed to initialize real-time system:', error);
            this.startPollingFallback();
        }
    }
    
    setupEventListeners() {
        // Page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });
        
        // Network status changes
        window.addEventListener('online', () => {
            this.handleNetworkOnline();
        });
        
        window.addEventListener('offline', () => {
            this.handleNetworkOffline();
        });
        
        // Window unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    connect() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            try {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/realtime`;
                
                this.websocket = new WebSocket(wsUrl);
                
                this.websocket.onopen = (event) => {
                    this.handleWebSocketOpen(event);
                    resolve();
                };
                
                this.websocket.onmessage = (event) => {
                    this.handleWebSocketMessage(event);
                };
                
                this.websocket.onclose = (event) => {
                    this.handleWebSocketClose(event);
                };
                
                this.websocket.onerror = (event) => {
                    this.handleWebSocketError(event);
                    reject(event);
                };
                
                // Connection timeout
                setTimeout(() => {
                    if (this.websocket.readyState !== WebSocket.OPEN) {
                        this.websocket.close();
                        reject(new Error('WebSocket connection timeout'));
                    }
                }, 5000);
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    handleWebSocketOpen(event) {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.emit('connected');
        
        // Update connection status indicator
        this.updateConnectionStatus('connected');
    }
    
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            this.processRealTimeUpdate(data);
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }
    
    handleWebSocketClose(event) {
        console.log('WebSocket connection closed:', event.code, event.reason);
        this.isConnected = false;
        this.stopHeartbeat();
        this.emit('disconnected');
        
        // Update connection status indicator
        this.updateConnectionStatus('disconnected');
        
        // Attempt to reconnect if not a clean close
        if (event.code !== 1000 && this.reconnectAttempts < this.options.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            console.log('WebSocket reconnection disabled, falling back to polling');
            this.startPollingFallback();
        }
    }
    
    handleWebSocketError(event) {
        console.error('WebSocket error:', event);
        this.emit('error', event);
        this.updateConnectionStatus('error');
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.options.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`Attempting to reconnect WebSocket in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect().catch(() => {
                    // Reconnection failed, will try again or fall back to polling
                });
            }
        }, delay);
    }
    
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({ type: 'ping' }));
                this.lastHeartbeat = Date.now();
            }
        }, this.options.heartbeatInterval);
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    processRealTimeUpdate(data) {
        switch (data.type) {
            case 'pong':
                // Heartbeat response
                break;
                
            case 'metrics_update':
                this.handleMetricsUpdate(data.payload);
                break;
                
            case 'agent_status_change':
                this.handleAgentStatusChange(data.payload);
                break;
                
            case 'task_status_change':
                this.handleTaskStatusChange(data.payload);
                break;
                
            case 'system_alert':
                this.handleSystemAlert(data.payload);
                break;
                
            case 'pool_scaling':
                this.handlePoolScaling(data.payload);
                break;
                
            default:
                console.log('Unknown real-time update type:', data.type);
        }
        
        this.emit('update', data);
    }
    
    handleMetricsUpdate(payload) {
        this.queueUpdate(() => {
            if (window.operatorOSDashboard) {
                window.operatorOSDashboard.updateMetrics(payload);
                window.operatorOSDashboard.updateCharts(payload);
            }
        });
        
        this.emit('metrics_update', payload);
    }
    
    handleAgentStatusChange(payload) {
        const { agent_id, old_status, new_status, pool_name } = payload;
        
        // Update agent status in UI
        this.updateAgentStatusInUI(agent_id, new_status);
        
        // Show notification for critical status changes
        if (new_status === 'failed') {
            this.showNotification(
                `Agent ${agent_id} has failed`,
                'warning',
                { icon: 'alert-triangle' }
            );
        } else if (old_status === 'failed' && new_status === 'idle') {
            this.showNotification(
                `Agent ${agent_id} has recovered`,
                'success',
                { icon: 'check-circle' }
            );
        }
        
        this.emit('agent_status_change', payload);
    }
    
    handleTaskStatusChange(payload) {
        const { task_id, old_status, new_status, processing_time } = payload;
        
        // Update task status in UI
        this.updateTaskStatusInUI(task_id, new_status);
        
        // Show notification for completed/failed tasks if user is watching
        if (this.isUserWatchingTask(task_id)) {
            if (new_status === 'completed') {
                this.showNotification(
                    `Task ${task_id.slice(0, 8)} completed successfully`,
                    'success',
                    { icon: 'check-circle', duration: 5000 }
                );
            } else if (new_status === 'failed') {
                this.showNotification(
                    `Task ${task_id.slice(0, 8)} failed`,
                    'error',
                    { icon: 'x-circle', duration: 7000 }
                );
            }
        }
        
        this.emit('task_status_change', payload);
    }
    
    handleSystemAlert(payload) {
        const { level, message, component, details } = payload;
        
        let notificationType = 'info';
        if (level === 'error' || level === 'critical') {
            notificationType = 'error';
        } else if (level === 'warning') {
            notificationType = 'warning';
        }
        
        this.showNotification(
            `System Alert: ${message}`,
            notificationType,
            { 
                icon: 'alert-triangle',
                duration: level === 'critical' ? 0 : 8000, // Critical alerts don't auto-hide
                details: details
            }
        );
        
        this.emit('system_alert', payload);
    }
    
    handlePoolScaling(payload) {
        const { pool_name, action, agent_count } = payload;
        
        this.showNotification(
            `${pool_name} pool ${action}: now ${agent_count} agents`,
            'info',
            { icon: 'users' }
        );
        
        // Refresh pool display
        this.queueUpdate(() => {
            if (window.operatorOSDashboard) {
                window.operatorOSDashboard.updateDashboardData();
            }
        });
        
        this.emit('pool_scaling', payload);
    }
    
    updateAgentStatusInUI(agentId, newStatus) {
        // Update agent status badges
        document.querySelectorAll(`[data-agent-id="${agentId}"]`).forEach(element => {
            const statusBadge = element.querySelector('.agent-status-badge');
            if (statusBadge) {
                statusBadge.className = `badge agent-status-badge bg-${this.getStatusColor(newStatus)}`;
                statusBadge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
            }
            
            // Add visual feedback
            element.classList.add('status-updated');
            setTimeout(() => {
                element.classList.remove('status-updated');
            }, 2000);
        });
    }
    
    updateTaskStatusInUI(taskId, newStatus) {
        // Update task status in tables and cards
        document.querySelectorAll(`[data-task-id="${taskId}"]`).forEach(element => {
            const statusBadge = element.querySelector('.task-status-badge');
            if (statusBadge) {
                statusBadge.className = `badge task-status-badge bg-${this.getStatusColor(newStatus)}`;
                statusBadge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                
                // Add appropriate icon
                const icon = this.getStatusIcon(newStatus);
                if (icon) {
                    statusBadge.innerHTML = `<i data-feather="${icon}" class="me-1"></i>${statusBadge.textContent}`;
                    feather.replace(); // Re-initialize feather icons
                }
            }
            
            // Add visual feedback
            element.classList.add('status-updated');
            setTimeout(() => {
                element.classList.remove('status-updated');
            }, 2000);
        });
    }
    
    getStatusColor(status) {
        const colorMap = {
            'idle': 'success',
            'busy': 'warning',
            'failed': 'danger',
            'pending': 'secondary',
            'processing': 'primary',
            'completed': 'success',
            'error': 'danger'
        };
        return colorMap[status] || 'secondary';
    }
    
    getStatusIcon(status) {
        const iconMap = {
            'idle': 'pause-circle',
            'busy': 'play-circle',
            'failed': 'x-circle',
            'pending': 'clock',
            'processing': 'play-circle',
            'completed': 'check-circle',
            'error': 'x-circle'
        };
        return iconMap[status];
    }
    
    isUserWatchingTask(taskId) {
        // Check if user is on task detail page or has task in view
        return window.location.pathname.includes(`/task/${taskId}`) ||
               document.querySelector(`[data-task-id="${taskId}"]`) !== null;
    }
    
    queueUpdate(updateFunction) {
        this.updateQueue.push(updateFunction);
        
        if (!this.updateTimer) {
            this.updateTimer = setTimeout(() => {
                this.processUpdateQueue();
            }, this.options.updateThrottle);
        }
    }
    
    processUpdateQueue() {
        try {
            this.updateQueue.forEach(updateFn => {
                if (typeof updateFn === 'function') {
                    updateFn();
                }
            });
        } catch (error) {
            console.error('Error processing update queue:', error);
        } finally {
            this.updateQueue = [];
            this.updateTimer = null;
        }
    }
    
    startPollingFallback() {
        console.log('Starting polling fallback for real-time updates');
        
        // Poll for updates every 15 seconds as fallback
        this.pollingInterval = setInterval(async () => {
            try {
                const response = await fetch('/admin/api/metrics');
                if (response.ok) {
                    const data = await response.json();
                    this.handleMetricsUpdate(data);
                }
            } catch (error) {
                console.error('Polling update failed:', error);
            }
        }, 15000);
        
        this.updateConnectionStatus('polling');
    }
    
    stopPollingFallback() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `connection-status ${status}`;
            
            const statusText = {
                'connected': 'Real-time connected',
                'disconnected': 'Disconnected',
                'error': 'Connection error',
                'polling': 'Polling mode'
            };
            
            indicator.textContent = statusText[status] || status;
            indicator.title = `Connection status: ${status}`;
        }
        
        // Update navbar indicator
        const navIndicator = document.querySelector('.navbar .connection-indicator');
        if (navIndicator) {
            navIndicator.className = `connection-indicator status-${status}`;
        }
    }
    
    showNotification(message, type = 'info', options = {}) {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date(),
            ...options
        };
        
        // Show in dashboard if available
        if (window.operatorOSDashboard) {
            if (type === 'error') {
                window.operatorOSDashboard.showErrorMessage(message);
            } else if (type === 'success') {
                window.operatorOSDashboard.showSuccessMessage(message);
            } else {
                window.operatorOSDashboard.showInfoMessage(message);
            }
        }
        
        // Store notification for notification center
        this.storeNotification(notification);
        
        this.emit('notification', notification);
    }
    
    storeNotification(notification) {
        const stored = JSON.parse(localStorage.getItem('operatorOS_notifications') || '[]');
        stored.unshift(notification);
        
        // Keep only last 50 notifications
        if (stored.length > 50) {
            stored.splice(50);
        }
        
        localStorage.setItem('operatorOS_notifications', JSON.stringify(stored));
        
        // Update notification count in UI
        this.updateNotificationCount(stored.length);
    }
    
    updateNotificationCount(count) {
        const counter = document.querySelector('.notification-count');
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'inline' : 'none';
        }
    }
    
    getStoredNotifications() {
        return JSON.parse(localStorage.getItem('operatorOS_notifications') || '[]');
    }
    
    clearNotifications() {
        localStorage.removeItem('operatorOS_notifications');
        this.updateNotificationCount(0);
    }
    
    handlePageHidden() {
        // Reduce update frequency when page is hidden
        if (this.isConnected) {
            // Send a message to reduce server-side update frequency
            this.send({ type: 'page_hidden' });
        }
    }
    
    handlePageVisible() {
        // Resume normal update frequency
        if (this.isConnected) {
            this.send({ type: 'page_visible' });
        } else {
            // Try to reconnect if disconnected
            this.connect().catch(() => {
                console.log('Failed to reconnect, continuing with polling');
            });
        }
    }
    
    handleNetworkOnline() {
        console.log('Network is back online');
        if (!this.isConnected) {
            this.connect().catch(() => {
                console.log('Failed to reconnect after network recovery');
            });
        }
    }
    
    handleNetworkOffline() {
        console.log('Network is offline');
        this.updateConnectionStatus('offline');
    }
    
    send(data) {
        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(data));
        }
    }
    
    // Event emitter functionality
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }
    
    cleanup() {
        this.stopHeartbeat();
        this.stopPollingFallback();
        
        if (this.websocket) {
            this.websocket.close(1000, 'Page unload');
        }
        
        if (this.updateTimer) {
            clearTimeout(this.updateTimer);
        }
        
        this.listeners = {};
    }
}

// Initialize real-time system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.operatorOSRealTime = new OperatorOSRealTime();
});

// Global utility functions for real-time features
window.initializeRealTimeUpdates = function() {
    if (window.operatorOSRealTime) {
        window.operatorOSRealTime.connect().catch(() => {
            console.log('WebSocket connection failed, using polling fallback');
        });
    }
};

window.subscribeToUpdates = function(eventType, callback) {
    if (window.operatorOSRealTime) {
        window.operatorOSRealTime.on(eventType, callback);
    }
};

window.unsubscribeFromUpdates = function(eventType, callback) {
    if (window.operatorOSRealTime) {
        window.operatorOSRealTime.off(eventType, callback);
    }
};

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OperatorOSRealTime;
}
