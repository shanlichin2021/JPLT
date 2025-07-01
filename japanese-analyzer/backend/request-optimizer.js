// backend/request-optimizer.js - Request Optimization and Rate Limiting

import rateLimit from 'express-rate-limit';
import compression from 'compression';

class RequestOptimizer {
    constructor() {
        this.requestQueue = new Map();
        this.batchProcessor = new BatchProcessor();
        this.circuitBreakers = new Map();
    }

    // Compression middleware for response optimization
    createCompressionMiddleware() {
        return compression({
            filter: (req, res) => {
                // Don't compress if explicitly disabled
                if (req.headers['x-no-compression']) {
                    return false;
                }
                
                // Compress JSON responses and text
                return compression.filter(req, res);
            },
            level: 6, // Good balance between compression and speed
            threshold: 1024, // Only compress responses > 1KB
            memLevel: 8 // Memory usage for compression
        });
    }

    // Smart rate limiting based on request type
    createRateLimiters() {
        return {
            // General API rate limiting
            general: rateLimit({
                windowMs: 60 * 1000, // 1 minute
                max: 100, // 100 requests per minute
                message: {
                    error: 'Too many requests, please try again later.',
                    retryAfter: 60
                },
                standardHeaders: true,
                legacyHeaders: false,
                handler: (req, res) => {
                    res.status(429).json({
                        error: 'Rate limit exceeded',
                        retryAfter: Math.ceil(req.rateLimit.resetTime / 1000)
                    });
                }
            }),

            // OCR/Image processing (more restrictive)
            ocr: rateLimit({
                windowMs: 60 * 1000,
                max: 20, // 20 image requests per minute
                message: {
                    error: 'Too many image processing requests, please try again later.',
                    retryAfter: 60
                }
            }),

            // Analysis requests (moderate restriction)
            analysis: rateLimit({
                windowMs: 60 * 1000,
                max: 50, // 50 analysis requests per minute
                message: {
                    error: 'Too many analysis requests, please try again later.',
                    retryAfter: 60
                }
            }),

            // Dictionary lookups (less restrictive)
            dictionary: rateLimit({
                windowMs: 60 * 1000,
                max: 200, // 200 dictionary requests per minute
                message: {
                    error: 'Too many dictionary requests, please try again later.',
                    retryAfter: 60
                }
            })
        };
    }

    // Request deduplication middleware
    createDeduplicationMiddleware() {
        return (req, res, next) => {
            const key = this.generateRequestKey(req);
            const existingRequest = this.requestQueue.get(key);
            
            if (existingRequest) {
                // If same request is already processing, wait for it
                existingRequest.promise.then(result => {
                    res.json(result);
                }).catch(error => {
                    res.status(500).json({ error: error.message });
                });
                return;
            }
            
            // Create new request promise
            const requestPromise = new Promise((resolve, reject) => {
                req.resolve = resolve;
                req.reject = reject;
            });
            
            this.requestQueue.set(key, {
                promise: requestPromise,
                timestamp: Date.now()
            });
            
            // Clean up after request completes
            const originalEnd = res.end;
            res.end = function(chunk, encoding) {
                this.requestQueue.delete(key);
                originalEnd.call(res, chunk, encoding);
            }.bind(this);
            
            next();
        };
    }

    generateRequestKey(req) {
        // Generate key based on method, path, and critical body parameters
        const criticalParams = this.extractCriticalParams(req);
        return `${req.method}:${req.path}:${JSON.stringify(criticalParams)}`;
    }

    extractCriticalParams(req) {
        // Extract only parameters that affect the response
        switch (req.path) {
            case '/api/full-analysis':
                return { text: req.body?.text };
            case '/api/debug-lookup':
                return { word: req.body?.word };
            default:
                return {};
        }
    }

    // Circuit breaker for external services
    createCircuitBreaker(serviceName, options = {}) {
        const config = {
            failureThreshold: options.failureThreshold || 5,
            resetTimeout: options.resetTimeout || 30000,
            monitoringPeriod: options.monitoringPeriod || 60000,
            ...options
        };

        const breaker = {
            state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
            failures: 0,
            lastFailureTime: null,
            nextAttempt: null,
            config
        };

        this.circuitBreakers.set(serviceName, breaker);
        return breaker;
    }

    async executeWithCircuitBreaker(serviceName, operation, fallback = null) {
        const breaker = this.circuitBreakers.get(serviceName);
        if (!breaker) {
            throw new Error(`Circuit breaker not found for service: ${serviceName}`);
        }

        // Check circuit breaker state
        const now = Date.now();
        
        if (breaker.state === 'OPEN') {
            if (now < breaker.nextAttempt) {
                console.log(`🔴 Circuit breaker OPEN for ${serviceName}, using fallback`);
                if (fallback) return await fallback();
                throw new Error(`Service ${serviceName} is temporarily unavailable`);
            } else {
                breaker.state = 'HALF_OPEN';
                console.log(`🟡 Circuit breaker HALF_OPEN for ${serviceName}, trying request`);
            }
        }

        try {
            const result = await operation();
            
            // Success - reset circuit breaker
            if (breaker.state === 'HALF_OPEN') {
                breaker.state = 'CLOSED';
                breaker.failures = 0;
                console.log(`🟢 Circuit breaker CLOSED for ${serviceName}, service recovered`);
            }
            
            return result;
        } catch (error) {
            breaker.failures++;
            breaker.lastFailureTime = now;
            
            if (breaker.failures >= breaker.config.failureThreshold) {
                breaker.state = 'OPEN';
                breaker.nextAttempt = now + breaker.config.resetTimeout;
                console.log(`🔴 Circuit breaker OPEN for ${serviceName} after ${breaker.failures} failures`);
            }
            
            if (fallback) {
                console.log(`Using fallback for ${serviceName} due to error:`, error.message);
                return await fallback();
            }
            
            throw error;
        }
    }

    // Cleanup old requests from queue
    startCleanupProcess() {
        setInterval(() => {
            const now = Date.now();
            const maxAge = 5 * 60 * 1000; // 5 minutes
            
            for (const [key, request] of this.requestQueue) {
                if (now - request.timestamp > maxAge) {
                    this.requestQueue.delete(key);
                }
            }
        }, 60000); // Cleanup every minute
    }

    // Get optimization statistics
    getStats() {
        return {
            requestQueue: {
                size: this.requestQueue.size,
                oldestRequest: this.getOldestRequestAge()
            },
            circuitBreakers: this.getCircuitBreakerStats(),
            batchProcessor: this.batchProcessor.getStats()
        };
    }

    getOldestRequestAge() {
        if (this.requestQueue.size === 0) return 0;
        
        const now = Date.now();
        let oldest = now;
        
        for (const request of this.requestQueue.values()) {
            oldest = Math.min(oldest, request.timestamp);
        }
        
        return now - oldest;
    }

    getCircuitBreakerStats() {
        const stats = {};
        for (const [name, breaker] of this.circuitBreakers) {
            stats[name] = {
                state: breaker.state,
                failures: breaker.failures,
                lastFailureTime: breaker.lastFailureTime,
                nextAttempt: breaker.nextAttempt
            };
        }
        return stats;
    }
}

// Batch processing for similar requests
class BatchProcessor {
    constructor() {
        this.batches = new Map();
        this.batchTimeout = 100; // ms
        this.maxBatchSize = 10;
        this.stats = {
            batchesProcessed: 0,
            itemsProcessed: 0,
            averageBatchSize: 0
        };
    }

    addToBatch(type, item, processor) {
        if (!this.batches.has(type)) {
            this.batches.set(type, {
                items: [],
                processor,
                timeout: null
            });
        }

        const batch = this.batches.get(type);
        batch.items.push(item);

        // Clear existing timeout
        if (batch.timeout) {
            clearTimeout(batch.timeout);
        }

        // Process immediately if batch is full
        if (batch.items.length >= this.maxBatchSize) {
            this.processBatch(type);
        } else {
            // Set timeout to process batch
            batch.timeout = setTimeout(() => {
                this.processBatch(type);
            }, this.batchTimeout);
        }

        return new Promise((resolve, reject) => {
            item.resolve = resolve;
            item.reject = reject;
        });
    }

    async processBatch(type) {
        const batch = this.batches.get(type);
        if (!batch || batch.items.length === 0) return;

        const items = batch.items.splice(0);
        if (batch.timeout) {
            clearTimeout(batch.timeout);
            batch.timeout = null;
        }

        try {
            const results = await batch.processor(items);
            
            // Resolve individual promises
            items.forEach((item, index) => {
                if (item.resolve) {
                    item.resolve(results[index]);
                }
            });

            // Update stats
            this.stats.batchesProcessed++;
            this.stats.itemsProcessed += items.length;
            this.stats.averageBatchSize = this.stats.itemsProcessed / this.stats.batchesProcessed;
            
        } catch (error) {
            // Reject all promises in batch
            items.forEach(item => {
                if (item.reject) {
                    item.reject(error);
                }
            });
        }
    }

    getStats() {
        return { ...this.stats };
    }
}

export default RequestOptimizer;