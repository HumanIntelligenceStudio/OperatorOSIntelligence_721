/**
 * OperatorOS Dashboard JavaScript
 * Handles dashboard interactions, real-time updates, and UI enhancements
 */

class OperatorOSDashboard {
    constructor() {
        this.isInitialized = false;
        this.updateInterval = null;
        this.charts = {};
        this.metricsCache = {};
        this.lastUpdate = null;
        
        // Configuration
        this.config = {
            updateIntervalMs: 30000, // 30 seconds
            chartUpdateMs: 60000,    // 1 minute
            animationDuration: 300,
            maxRetries: 3,
            retryDelay: 1000
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupEventListeners();
            this.initializeTooltips();
            this.initializeCharts();
            this.startRealTimeUpdates();
            this.setupErrorHandling();
            
            this.isInitialized = true;
            console.log('OperatorOS Dashboard initialized successfully');
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showErrorMessage('Dashboard initialization failed');
        }
    }
    
    setupEventListeners() {
        // Refresh buttons
        document.querySelectorAll('[data-action="refresh"]').forEach(btn => {
            btn.addEventListener('click', () => this.handleRefresh());
        });
        
        // Pool scaling buttons
        document.querySelectorAll('[data-action="scale-pool"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePoolScaling(e));
        });
        
        // Agent restart buttons
        document.querySelectorAll('[data-action="restart-agent"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleAgentRestart(e));
        });
        
        // Task retry buttons
        document.querySelectorAll('[data-action="retry-task"]').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTaskRetry(e));
        });
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.toggleAutoRefresh(e.target.checked);
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // Page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }
    
    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover',
                delay: { show: 500, hide: 100 }
            });
        });
    }
    
    initializeCharts() {
        try {
            // Performance Chart
            const performanceCanvas = document.getElementById('performanceChart');
            if (performanceCanvas) {
                this.charts.performance = this.createPerformanceChart(performanceCanvas);
            }
            
            // Agent Distribution Chart
            const agentCanvas = document.getElementById('agentChart');
            if (agentCanvas) {
                this.charts.agent = this.createAgentChart(agentCanvas);
            }
            
            // Historical Metrics Chart
            const historicalCanvas = document.getElementById('historicalChart');
            if (historicalCanvas) {
                this.charts.historical = this.createHistoricalChart(historicalCanvas);
            }
            
            // Real-time Metrics Chart
            const realTimeCanvas = document.getElementById('realTimeMetrics');
            if (realTimeCanvas) {
                this.charts.realTime = this.createRealTimeChart(realTimeCanvas);
            }
        } catch (error) {
            console.error('Failed to initialize charts:', error);
        }
    }
    
    createPerformanceChart(canvas) {
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(24),
                datasets: [{
                    label: 'Tasks Completed',
                    data: this.generateSampleData(24, 10, 50),
                    borderColor: 'rgb(40, 167, 69)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Failed Tasks',
                    data: this.generateSampleData(24, 0, 5),
                    borderColor: 'rgb(220, 53, 69)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            color: 'rgba(255, 255, 255, 0.8)'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                },
                animation: {
                    duration: this.config.animationDuration
                }
            }
        });
    }
    
    createAgentChart(canvas) {
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Idle', 'Busy', 'Failed'],
                datasets: [{
                    data: [0, 0, 0, 0], // Will be updated with real data
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(13, 202, 240, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: 'var(--bs-body-bg)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            color: 'rgba(255, 255, 255, 0.8)',
                            padding: 15
                        }
                    }
                },
                animation: {
                    duration: this.config.animationDuration
                }
            }
        });
    }
    
    createHistoricalChart(canvas) {
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Successful Requests',
                    data: [],
                    backgroundColor: 'rgba(40, 167, 69, 0.6)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }, {
                    label: 'Failed Requests',
                    data: [],
                    backgroundColor: 'rgba(220, 53, 69, 0.6)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.8)'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        stacked: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
    
    createRealTimeChart(canvas) {
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Active Agents',
                    data: [],
                    borderColor: 'rgb(40, 167, 69)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Total Requests',
                    data: [],
                    borderColor: 'rgb(13, 110, 253)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.8)'
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }
    
    startRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            this.updateDashboardData();
        }, this.config.updateIntervalMs);
        
        // Initial update
        this.updateDashboardData();
    }
    
    async updateDashboardData() {
        try {
            const response = await this.fetchWithRetry('/admin/api/metrics');
            if (response.ok) {
                const data = await response.json();
                this.updateMetrics(data);
                this.updateCharts(data);
                this.lastUpdate = new Date();
                this.updateLastUpdateTime();
            }
        } catch (error) {
            console.error('Failed to update dashboard data:', error);
            this.showErrorMessage('Failed to fetch latest metrics');
        }
    }
    
    updateMetrics(data) {
        // Update agent statistics
        this.updateElement('total-agents', data.agent_stats?.total || 0);
        this.updateElement('active-agents', data.agent_stats?.active || 0);
        this.updateElement('idle-agents', data.agent_stats?.idle || 0);
        this.updateElement('busy-agents', data.agent_stats?.busy || 0);
        this.updateElement('failed-agents', data.agent_stats?.failed || 0);
        
        // Update task statistics
        this.updateElement('pending-tasks', data.task_stats?.pending || 0);
        this.updateElement('processing-tasks', data.task_stats?.processing || 0);
        this.updateElement('completed-tasks', data.task_stats?.completed || 0);
        this.updateElement('failed-tasks', data.task_stats?.failed || 0);
        
        // Update system metrics
        if (data.system_metrics) {
            this.updateElement('avg-response-time', 
                `${(data.system_metrics.avg_response_time || 0).toFixed(2)}s`);
            this.updateElement('success-rate', 
                `${(data.system_metrics.success_rate || 0).toFixed(1)}%`);
        }
        
        // Update progress bars
        this.updateProgressBars(data);
        
        // Update status badges
        this.updateStatusBadges(data);
    }
    
    updateCharts(data) {
        // Update agent distribution chart
        if (this.charts.agent && data.agent_stats) {
            this.charts.agent.data.datasets[0].data = [
                data.agent_stats.active || 0,
                data.agent_stats.idle || 0,
                data.agent_stats.busy || 0,
                data.agent_stats.failed || 0
            ];
            this.charts.agent.update('none');
        }
        
        // Update real-time chart with new data point
        if (this.charts.realTime && data.timestamp) {
            const timeLabel = new Date(data.timestamp).toLocaleTimeString();
            const chart = this.charts.realTime;
            
            // Add new data point
            chart.data.labels.push(timeLabel);
            chart.data.datasets[0].data.push(data.agent_stats?.active || 0);
            chart.data.datasets[1].data.push(
                (data.task_stats?.completed || 0) + (data.task_stats?.failed || 0)
            );
            
            // Keep only last 20 data points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
            }
            
            chart.update('none');
        }
    }
    
    updateProgressBars(data) {
        document.querySelectorAll('.progress-bar[data-metric]').forEach(bar => {
            const metric = bar.dataset.metric;
            let value = 0;
            
            switch (metric) {
                case 'agent-health':
                    const total = data.agent_stats?.total || 1;
                    const healthy = (data.agent_stats?.active || 0) + (data.agent_stats?.idle || 0);
                    value = (healthy / total) * 100;
                    break;
                case 'success-rate':
                    value = data.system_metrics?.success_rate || 0;
                    break;
                default:
                    value = parseFloat(bar.dataset.value || 0);
            }
            
            bar.style.width = `${Math.min(100, Math.max(0, value))}%`;
            bar.setAttribute('aria-valuenow', value);
        });
    }
    
    updateStatusBadges(data) {
        document.querySelectorAll('.status-badge[data-status]').forEach(badge => {
            const status = badge.dataset.status;
            const count = data.agent_stats?.[status] || data.task_stats?.[status] || 0;
            
            const countElement = badge.querySelector('.status-count');
            if (countElement) {
                countElement.textContent = count;
            }
            
            // Update badge class based on count
            badge.classList.remove('bg-success', 'bg-warning', 'bg-danger', 'bg-secondary');
            if (count === 0) {
                badge.classList.add('bg-secondary');
            } else if (status.includes('failed') || status.includes('error')) {
                badge.classList.add('bg-danger');
            } else if (status.includes('warning') || status.includes('busy')) {
                badge.classList.add('bg-warning');
            } else {
                badge.classList.add('bg-success');
            }
        });
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            const currentValue = element.textContent;
            if (currentValue !== String(value)) {
                element.textContent = value;
                element.classList.add('fade-in');
                setTimeout(() => {
                    element.classList.remove('fade-in');
                }, this.config.animationDuration);
            }
        }
    }
    
    updateLastUpdateTime() {
        const updateElement = document.getElementById('last-update');
        if (updateElement && this.lastUpdate) {
            updateElement.textContent = `Last updated: ${this.lastUpdate.toLocaleTimeString()}`;
        }
    }
    
    async fetchWithRetry(url, options = {}, retries = 0) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok && retries < this.config.maxRetries) {
                await this.delay(this.config.retryDelay * Math.pow(2, retries));
                return this.fetchWithRetry(url, options, retries + 1);
            }
            
            return response;
        } catch (error) {
            if (retries < this.config.maxRetries) {
                await this.delay(this.config.retryDelay * Math.pow(2, retries));
                return this.fetchWithRetry(url, options, retries + 1);
            }
            throw error;
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    handleRefresh() {
        this.showLoadingState();
        this.updateDashboardData().finally(() => {
            this.hideLoadingState();
        });
    }
    
    handlePoolScaling(event) {
        const button = event.target.closest('button');
        const poolName = button.dataset.pool;
        const action = button.dataset.scaleAction;
        
        if (confirm(`Are you sure you want to ${action} the ${poolName} pool?`)) {
            this.scalePool(poolName, action);
        }
    }
    
    async scalePool(poolName, action) {
        try {
            const response = await this.fetchWithRetry(`/admin/pools/${poolName}/scale`, {
                method: 'POST',
                body: new FormData(Object.assign(document.createElement('form'), {
                    action: { value: action.replace('-', '_') }
                }))
            });
            
            if (response.ok) {
                this.showSuccessMessage(`${poolName} pool ${action} successful`);
                this.updateDashboardData();
            } else {
                throw new Error(`Failed to ${action} pool`);
            }
        } catch (error) {
            console.error('Pool scaling error:', error);
            this.showErrorMessage(`Failed to ${action} ${poolName} pool`);
        }
    }
    
    handleAgentRestart(event) {
        const button = event.target.closest('button');
        const agentId = button.dataset.agentId;
        
        if (confirm('Are you sure you want to restart this agent?')) {
            this.restartAgent(agentId);
        }
    }
    
    async restartAgent(agentId) {
        try {
            const response = await this.fetchWithRetry(`/admin/agents/${agentId}/restart`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccessMessage('Agent restarted successfully');
                this.updateDashboardData();
            } else {
                throw new Error('Failed to restart agent');
            }
        } catch (error) {
            console.error('Agent restart error:', error);
            this.showErrorMessage('Failed to restart agent');
        }
    }
    
    handleTaskRetry(event) {
        const button = event.target.closest('button');
        const taskId = button.dataset.taskId;
        
        if (confirm('Are you sure you want to retry this task?')) {
            this.retryTask(taskId);
        }
    }
    
    async retryTask(taskId) {
        try {
            const response = await this.fetchWithRetry(`/admin/tasks/${taskId}/retry`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccessMessage('Task queued for retry');
                this.updateDashboardData();
            } else {
                throw new Error('Failed to retry task');
            }
        } catch (error) {
            console.error('Task retry error:', error);
            this.showErrorMessage('Failed to retry task');
        }
    }
    
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + R: Refresh
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            this.handleRefresh();
        }
        
        // Ctrl/Cmd + Shift + A: Go to admin
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'A') {
            event.preventDefault();
            window.location.href = '/admin';
        }
    }
    
    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.startRealTimeUpdates();
            this.showSuccessMessage('Auto-refresh enabled');
        } else {
            this.pauseUpdates();
            this.showInfoMessage('Auto-refresh disabled');
        }
    }
    
    pauseUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    resumeUpdates() {
        if (!this.updateInterval) {
            this.startRealTimeUpdates();
        }
    }
    
    showLoadingState() {
        document.querySelectorAll('.loading-indicator').forEach(indicator => {
            indicator.style.display = 'block';
        });
    }
    
    hideLoadingState() {
        document.querySelectorAll('.loading-indicator').forEach(indicator => {
            indicator.style.display = 'none';
        });
    }
    
    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showToast(message, 'error');
    }
    
    showInfoMessage(message) {
        this.showToast(message, 'info');
    }
    
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: type === 'error' ? 5000 : 3000
        });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showErrorMessage('An unexpected error occurred');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showErrorMessage('Network error occurred');
        });
    }
    
    generateTimeLabels(hours) {
        const labels = [];
        for (let i = 0; i < hours; i++) {
            labels.push(`${i}:00`);
        }
        return labels;
    }
    
    generateSampleData(length, min, max) {
        const data = [];
        for (let i = 0; i < length; i++) {
            data.push(Math.floor(Math.random() * (max - min + 1)) + min);
        }
        return data;
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.isInitialized = false;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.operatorOSDashboard = new OperatorOSDashboard();
});

// Global utility functions
window.refreshDashboard = function() {
    if (window.operatorOSDashboard) {
        window.operatorOSDashboard.handleRefresh();
    }
};

window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        if (window.operatorOSDashboard) {
            window.operatorOSDashboard.showSuccessMessage('Copied to clipboard');
        }
    }).catch(() => {
        if (window.operatorOSDashboard) {
            window.operatorOSDashboard.showErrorMessage('Failed to copy to clipboard');
        }
    });
};

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OperatorOSDashboard;
}
