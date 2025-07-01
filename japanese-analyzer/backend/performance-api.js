// backend/performance-api.js - Performance Dashboard API Routes

import express from 'express';

function createPerformanceAPI(performanceMonitor, multiLevelCache, requestOptimizer) {
    const router = express.Router();

    // Real-time performance dashboard
    router.get('/dashboard', (req, res) => {
        const performanceReport = performanceMonitor.getPerformanceReport();
        const cacheStats = multiLevelCache.getAllStats();
        const optimizerStats = requestOptimizer.getStats();
        
        res.json({
            timestamp: new Date(),
            system: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                cpu: process.cpuUsage(),
                platform: process.platform,
                nodeVersion: process.version
            },
            performance: performanceReport,
            cache: cacheStats,
            optimizer: optimizerStats,
            recommendations: performanceReport.recommendations
        });
    });

    // Detailed metrics endpoint
    router.get('/metrics', async (req, res) => {
        const timeRange = req.query.timeRange || '1h';
        
        res.json({
            timeRange,
            metrics: performanceMonitor.metrics,
            cache: {
                detailed: multiLevelCache.getAllStats(),
                topEntries: {
                    definition: multiLevelCache.definitionCache.getTopEntries(10),
                    analysis: multiLevelCache.analysisCache.getTopEntries(5),
                    frequent: multiLevelCache.frequentWordsCache.getTopEntries(20)
                }
            },
            system: {
                memory: {
                    usage: process.memoryUsage(),
                    heap: process.memoryUsage().heapUsed / process.memoryUsage().heapTotal * 100
                },
                eventLoop: {
                    delay: await measureEventLoopDelay(),
                    utilization: process.cpuUsage()
                }
            }
        });
    });

    // Cache management endpoints
    router.post('/cache/warm', async (req, res) => {
        try {
            const { type, entries } = req.body;
            let result;
            
            if (type === 'frequent') {
                result = multiLevelCache.warmUp(entries);
            } else {
                result = multiLevelCache.getCache(type).preload(entries);
            }
            
            res.json({
                success: true,
                type,
                entriesLoaded: result,
                timestamp: new Date()
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    router.post('/cache/optimize', (req, res) => {
        try {
            const results = multiLevelCache.optimizeAll();
            res.json({
                success: true,
                results,
                timestamp: new Date()
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    router.delete('/cache/:type', (req, res) => {
        try {
            const type = req.params.type;
            
            if (type && type !== 'all') {
                multiLevelCache.getCache(type).clear();
                res.json({
                    success: true,
                    cleared: type,
                    timestamp: new Date()
                });
            } else {
                multiLevelCache.clearAll();
                res.json({
                    success: true,
                    cleared: 'all',
                    timestamp: new Date()
                });
            }
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // Clear all caches
    router.delete('/cache', (req, res) => {
        try {
            multiLevelCache.clearAll();
            res.json({
                success: true,
                cleared: 'all',
                timestamp: new Date()
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // Performance analysis endpoints
    router.get('/analysis/slow-queries', (req, res) => {
        const limit = parseInt(req.query.limit) || 50;
        const slowQueries = performanceMonitor.slowQueries.slice(-limit);
        
        res.json({
            slowQueries,
            summary: {
                total: slowQueries.length,
                averageDuration: slowQueries.length > 0 
                    ? slowQueries.reduce((sum, q) => sum + q.duration, 0) / slowQueries.length 
                    : 0,
                endpoints: [...new Set(slowQueries.map(q => q.endpoint))]
            }
        });
    });

    router.get('/analysis/memory-usage', (req, res) => {
        const memUsage = process.memoryUsage();
        const cacheMemory = multiLevelCache.getAllStats();
        
        res.json({
            system: {
                total: memUsage.heapTotal,
                used: memUsage.heapUsed,
                external: memUsage.external,
                rss: memUsage.rss,
                percentage: (memUsage.heapUsed / memUsage.heapTotal) * 100
            },
            cache: {
                definition: cacheMemory.definition.memoryUsage,
                analysis: cacheMemory.analysis.memoryUsage,
                image: cacheMemory.image.memoryUsage,
                frequent: cacheMemory.frequent.memoryUsage
            },
            recommendations: generateMemoryRecommendations(memUsage, cacheMemory)
        });
    });

    // Health check with performance context
    router.get('/health', (req, res) => {
        const health = performanceMonitor.getHealthStatus();
        const uptime = process.uptime();
        const memUsage = process.memoryUsage();
        
        const status = {
            status: health,
            uptime,
            memory: {
                used: Math.round(memUsage.heapUsed / 1024 / 1024),
                total: Math.round(memUsage.heapTotal / 1024 / 1024),
                percentage: Math.round((memUsage.heapUsed / memUsage.heapTotal) * 100)
            },
            cache: {
                hitRate: multiLevelCache.getAllStats().definition.hitRate,
                size: multiLevelCache.getAllStats().total.size
            },
            timestamp: new Date()
        };
        
        const httpStatus = health === 'healthy' ? 200 : health === 'warning' ? 200 : 503;
        res.status(httpStatus).json(status);
    });

    // Export performance data
    router.get('/export', (req, res) => {
        const format = req.query.format || 'json';
        const performanceData = {
            timestamp: new Date(),
            performance: performanceMonitor.getPerformanceReport(),
            cache: multiLevelCache.getAllStats(),
            system: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                platform: process.platform,
                nodeVersion: process.version
            }
        };
        
        if (format === 'csv') {
            const csv = convertToCSV(performanceData);
            res.setHeader('Content-Type', 'text/csv');
            res.setHeader('Content-Disposition', `attachment; filename=performance-${Date.now()}.csv`);
            res.send(csv);
        } else {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Content-Disposition', `attachment; filename=performance-${Date.now()}.json`);
            res.json(performanceData);
        }
    });

    // Reset performance statistics (for testing)
    router.post('/reset', (req, res) => {
        if (process.env.NODE_ENV !== 'development') {
            return res.status(403).json({
                error: 'Reset is only available in development mode'
            });
        }
        
        performanceMonitor.reset();
        multiLevelCache.clearAll();
        
        res.json({
            success: true,
            message: 'Performance statistics reset',
            timestamp: new Date()
        });
    });

    return router;
}

// Helper functions
async function measureEventLoopDelay() {
    return new Promise((resolve) => {
        const start = process.hrtime.bigint();
        setImmediate(() => {
            const delay = Number(process.hrtime.bigint() - start) / 1000000; // Convert to ms
            resolve(delay);
        });
    });
}

function generateMemoryRecommendations(memUsage, cacheStats) {
    const recommendations = [];
    const heapUsagePercentage = (memUsage.heapUsed / memUsage.heapTotal) * 100;
    
    if (heapUsagePercentage > 80) {
        recommendations.push({
            type: 'memory',
            priority: 'high',
            message: 'Heap usage is high. Consider increasing available memory or optimizing cache sizes.'
        });
    }
    
    if (memUsage.external > memUsage.heapUsed) {
        recommendations.push({
            type: 'memory',
            priority: 'medium',
            message: 'External memory usage is high. Check for memory leaks in native modules.'
        });
    }
    
    // Cache-specific recommendations
    const totalCacheMemory = Object.values(cacheStats)
        .filter(stat => stat.memoryUsage)
        .reduce((total, stat) => total + stat.memoryUsage.bytes, 0);
    
    if (totalCacheMemory > memUsage.heapUsed * 0.3) {
        recommendations.push({
            type: 'cache',
            priority: 'medium',
            message: 'Cache is using significant memory. Consider reducing cache sizes or TTL values.'
        });
    }
    
    return recommendations;
}

function convertToCSV(data) {
    // Simple CSV conversion for basic metrics
    const rows = [
        ['Metric', 'Value', 'Timestamp'],
        ['Total Requests', data.performance.summary.totalRequests, data.timestamp],
        ['Success Rate', data.performance.summary.successRate + '%', data.timestamp],
        ['Error Rate', data.performance.summary.errorRate + '%', data.timestamp],
        ['Avg Response Time', data.performance.performance.averageResponseTime + 'ms', data.timestamp],
        ['Cache Hit Rate', data.performance.performance.cacheHitRate + '%', data.timestamp],
        ['Memory Usage', data.performance.performance.memoryUsage.percentage + '%', data.timestamp],
        ['Uptime', data.system.uptime + 's', data.timestamp]
    ];
    
    return rows.map(row => row.join(',')).join('\n');
}

export default createPerformanceAPI;