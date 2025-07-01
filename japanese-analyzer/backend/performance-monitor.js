// backend/performance-monitor.js - Comprehensive Performance Monitoring & Optimization

import EventEmitter from 'events';

class PerformanceMonitor extends EventEmitter {
    constructor() {
        super();
        this.metrics = {
            requests: {
                total: 0,
                success: 0,
                errors: 0,
                averageResponseTime: 0,
                responseTimeHistory: []
            },
            cache: {
                hits: 0,
                misses: 0,
                size: 0,
                hitRate: 0
            },
            memory: {
                used: 0,
                total: 0,
                percentage: 0,
                peak: 0
            },
            parser: {
                totalProcessed: 0,
                averageTokens: 0,
                averageProcessingTime: 0,
                errors: 0
            }
        };
        
        this.startTime = Date.now();
        this.requestTimestamps = [];
        this.slowQueries = [];
        
        // Start monitoring intervals
        this.startMemoryMonitoring();
        this.startHealthCheck();
    }

    // Request performance tracking
    startRequest(requestId, endpoint) {
        const startTime = process.hrtime.bigint();
        return {
            requestId,
            endpoint,
            startTime,
            finish: (success = true, tokenCount = 0) => {
                const endTime = process.hrtime.bigint();
                const duration = Number(endTime - startTime) / 1000000; // Convert to milliseconds
                
                this.recordRequest(duration, success, endpoint, tokenCount);
                
                // Log slow requests
                if (duration > 5000) { // 5 seconds threshold
                    this.slowQueries.push({
                        endpoint,
                        duration,
                        timestamp: new Date(),
                        tokenCount
                    });
                    
                    // Keep only last 50 slow queries
                    if (this.slowQueries.length > 50) {
                        this.slowQueries.shift();
                    }
                }
                
                return duration;
            }
        };
    }

    recordRequest(duration, success, endpoint, tokenCount = 0) {
        this.metrics.requests.total++;
        
        if (success) {
            this.metrics.requests.success++;
        } else {
            this.metrics.requests.errors++;
        }
        
        // Update response time history (keep last 100)
        this.metrics.requests.responseTimeHistory.push(duration);
        if (this.metrics.requests.responseTimeHistory.length > 100) {
            this.metrics.requests.responseTimeHistory.shift();
        }
        
        // Calculate average response time
        const total = this.metrics.requests.responseTimeHistory.reduce((a, b) => a + b, 0);
        this.metrics.requests.averageResponseTime = total / this.metrics.requests.responseTimeHistory.length;
        
        // Parser-specific metrics
        if (endpoint === '/api/full-analysis' && tokenCount > 0) {
            this.metrics.parser.totalProcessed++;
            this.metrics.parser.averageTokens = 
                ((this.metrics.parser.averageTokens * (this.metrics.parser.totalProcessed - 1)) + tokenCount) 
                / this.metrics.parser.totalProcessed;
                
            this.metrics.parser.averageProcessingTime = 
                ((this.metrics.parser.averageProcessingTime * (this.metrics.parser.totalProcessed - 1)) + duration) 
                / this.metrics.parser.totalProcessed;
        }
        
        // Emit performance events for real-time monitoring
        this.emit('requestComplete', {
            duration,
            success,
            endpoint,
            tokenCount,
            timestamp: new Date()
        });
    }

    // Cache performance tracking
    recordCacheHit(cacheType = 'definition') {
        this.metrics.cache.hits++;
        this.updateCacheHitRate();
        this.emit('cacheHit', { type: cacheType, timestamp: new Date() });
    }

    recordCacheMiss(cacheType = 'definition') {
        this.metrics.cache.misses++;
        this.updateCacheHitRate();
        this.emit('cacheMiss', { type: cacheType, timestamp: new Date() });
    }

    updateCacheSize(size) {
        this.metrics.cache.size = size;
    }

    updateCacheHitRate() {
        const total = this.metrics.cache.hits + this.metrics.cache.misses;
        this.metrics.cache.hitRate = total > 0 ? (this.metrics.cache.hits / total) * 100 : 0;
    }

    // Memory monitoring
    startMemoryMonitoring() {
        setInterval(() => {
            const usage = process.memoryUsage();
            const total = usage.heapTotal;
            const used = usage.heapUsed;
            const percentage = (used / total) * 100;
            
            this.metrics.memory = {
                used: Math.round(used / 1024 / 1024), // MB
                total: Math.round(total / 1024 / 1024), // MB
                percentage: Math.round(percentage * 100) / 100,
                peak: Math.max(this.metrics.memory.peak || 0, Math.round(used / 1024 / 1024))
            };
            
            // Emit memory warnings
            if (percentage > 80) {
                this.emit('memoryWarning', {
                    percentage,
                    used: this.metrics.memory.used,
                    timestamp: new Date()
                });
            }
            
        }, 30000); // Every 30 seconds
    }

    // Health check monitoring
    startHealthCheck() {
        setInterval(() => {
            const uptime = Date.now() - this.startTime;
            const recentRequests = this.requestTimestamps.filter(
                timestamp => Date.now() - timestamp < 60000 // Last minute
            ).length;
            
            const health = {
                status: this.getHealthStatus(),
                uptime: Math.round(uptime / 1000), // seconds
                requestsPerMinute: recentRequests,
                cacheHitRate: this.metrics.cache.hitRate,
                memoryUsage: this.metrics.memory.percentage,
                averageResponseTime: this.metrics.requests.averageResponseTime,
                errorRate: this.getErrorRate(),
                timestamp: new Date()
            };
            
            this.emit('healthCheck', health);
            
        }, 60000); // Every minute
    }

    getHealthStatus() {
        const errorRate = this.getErrorRate();
        const memoryUsage = this.metrics.memory.percentage;
        const avgResponseTime = this.metrics.requests.averageResponseTime;
        
        if (errorRate > 10 || memoryUsage > 90 || avgResponseTime > 10000) {
            return 'critical';
        } else if (errorRate > 5 || memoryUsage > 80 || avgResponseTime > 5000) {
            return 'warning';
        } else {
            return 'healthy';
        }
    }

    getErrorRate() {
        const total = this.metrics.requests.total;
        return total > 0 ? (this.metrics.requests.errors / total) * 100 : 0;
    }

    // Performance recommendations
    getPerformanceRecommendations() {
        const recommendations = [];
        
        if (this.metrics.cache.hitRate < 70) {
            recommendations.push({
                type: 'cache',
                priority: 'high',
                message: `Cache hit rate is low (${this.metrics.cache.hitRate.toFixed(1)}%). Consider increasing cache size or improving cache strategy.`
            });
        }
        
        if (this.metrics.memory.percentage > 80) {
            recommendations.push({
                type: 'memory',
                priority: 'high',
                message: `Memory usage is high (${this.metrics.memory.percentage}%). Consider optimizing memory usage or increasing available memory.`
            });
        }
        
        if (this.metrics.requests.averageResponseTime > 3000) {
            recommendations.push({
                type: 'performance',
                priority: 'medium',
                message: `Average response time is ${this.metrics.requests.averageResponseTime.toFixed(0)}ms. Consider optimizing slow operations.`
            });
        }
        
        if (this.getErrorRate() > 5) {
            recommendations.push({
                type: 'reliability',
                priority: 'high',
                message: `Error rate is ${this.getErrorRate().toFixed(1)}%. Review error logs and improve error handling.`
            });
        }
        
        return recommendations;
    }

    // Generate performance report
    getPerformanceReport() {
        const uptime = Date.now() - this.startTime;
        const recentRequests = this.requestTimestamps.filter(
            timestamp => Date.now() - timestamp < 60000
        ).length;
        
        return {
            summary: {
                status: this.getHealthStatus(),
                uptime: Math.round(uptime / 1000),
                requestsPerMinute: recentRequests,
                totalRequests: this.metrics.requests.total,
                successRate: ((this.metrics.requests.success / this.metrics.requests.total) * 100).toFixed(1),
                errorRate: this.getErrorRate().toFixed(1)
            },
            performance: {
                averageResponseTime: Math.round(this.metrics.requests.averageResponseTime),
                cacheHitRate: this.metrics.cache.hitRate.toFixed(1),
                memoryUsage: this.metrics.memory,
                parserStats: this.metrics.parser
            },
            slowQueries: this.slowQueries.slice(-10), // Last 10 slow queries
            recommendations: this.getPerformanceRecommendations(),
            timestamp: new Date()
        };
    }

    // Reset metrics (useful for testing)
    reset() {
        this.metrics = {
            requests: { total: 0, success: 0, errors: 0, averageResponseTime: 0, responseTimeHistory: [] },
            cache: { hits: 0, misses: 0, size: 0, hitRate: 0 },
            memory: { used: 0, total: 0, percentage: 0, peak: 0 },
            parser: { totalProcessed: 0, averageTokens: 0, averageProcessingTime: 0, errors: 0 }
        };
        this.requestTimestamps = [];
        this.slowQueries = [];
        this.startTime = Date.now();
    }
}

export default PerformanceMonitor;