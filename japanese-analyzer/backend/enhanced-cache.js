// backend/enhanced-cache.js - Advanced LRU Cache with Performance Monitoring

class EnhancedLRUCache {
    constructor(maxSize = 1000, ttl = 3600000) { // 1 hour TTL by default
        this.maxSize = maxSize;
        this.ttl = ttl;
        this.cache = new Map();
        this.accessOrder = new Map(); // Track access order for LRU
        this.stats = {
            hits: 0,
            misses: 0,
            evictions: 0,
            size: 0,
            hitRate: 0,
            averageAccessTime: 0,
            accessTimes: []
        };
        
        // Cleanup expired entries every 10 minutes
        setInterval(() => this.cleanup(), 600000);
    }

    get(key, performanceMonitor = null) {
        const startTime = performance.now();
        
        const item = this.cache.get(key);
        const accessTime = performance.now() - startTime;
        
        // Update access time statistics
        this.stats.accessTimes.push(accessTime);
        if (this.stats.accessTimes.length > 1000) {
            this.stats.accessTimes.shift();
        }
        this.stats.averageAccessTime = this.stats.accessTimes.reduce((a, b) => a + b, 0) / this.stats.accessTimes.length;
        
        if (item && this.isValid(item)) {
            // Cache hit - update access order
            this.stats.hits++;
            this.accessOrder.set(key, Date.now());
            
            if (performanceMonitor) {
                performanceMonitor.recordCacheHit('definition');
            }
            
            this.updateHitRate();
            return item.value;
        } else {
            // Cache miss or expired
            if (item) {
                this.cache.delete(key);
                this.accessOrder.delete(key);
            }
            
            this.stats.misses++;
            
            if (performanceMonitor) {
                performanceMonitor.recordCacheMiss('definition');
            }
            
            this.updateHitRate();
            return null;
        }
    }

    set(key, value, customTTL = null) {
        const ttl = customTTL || this.ttl;
        const expiry = Date.now() + ttl;
        
        // If at max capacity, remove LRU item
        if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
            this.evictLRU();
        }
        
        this.cache.set(key, {
            value: value,
            expiry: expiry,
            created: Date.now(),
            accessed: Date.now()
        });
        
        this.accessOrder.set(key, Date.now());
        this.stats.size = this.cache.size;
    }

    evictLRU() {
        if (this.accessOrder.size === 0) return;
        
        // Find the least recently used item
        let oldestKey = null;
        let oldestTime = Infinity;
        
        for (const [key, time] of this.accessOrder) {
            if (time < oldestTime) {
                oldestTime = time;
                oldestKey = key;
            }
        }
        
        if (oldestKey) {
            this.cache.delete(oldestKey);
            this.accessOrder.delete(oldestKey);
            this.stats.evictions++;
            this.stats.size = this.cache.size;
        }
    }

    isValid(item) {
        return Date.now() < item.expiry;
    }

    cleanup() {
        let cleaned = 0;
        const now = Date.now();
        
        for (const [key, item] of this.cache) {
            if (now >= item.expiry) {
                this.cache.delete(key);
                this.accessOrder.delete(key);
                cleaned++;
            }
        }
        
        this.stats.size = this.cache.size;
        
        if (cleaned > 0) {
            console.log(`🧹 Cache cleanup: removed ${cleaned} expired entries`);
        }
        
        return cleaned;
    }

    updateHitRate() {
        const total = this.stats.hits + this.stats.misses;
        this.stats.hitRate = total > 0 ? (this.stats.hits / total) * 100 : 0;
    }

    clear() {
        this.cache.clear();
        this.accessOrder.clear();
        this.stats.size = 0;
    }

    has(key) {
        const item = this.cache.get(key);
        return item && this.isValid(item);
    }

    delete(key) {
        const deleted = this.cache.delete(key);
        this.accessOrder.delete(key);
        this.stats.size = this.cache.size;
        return deleted;
    }

    // Preload common entries (cache warming)
    preload(entries) {
        let loaded = 0;
        for (const [key, value] of entries) {
            if (!this.has(key)) {
                this.set(key, value);
                loaded++;
            }
        }
        console.log(`🔥 Cache warming: preloaded ${loaded} entries`);
        return loaded;
    }

    // Get cache statistics
    getStats() {
        return {
            ...this.stats,
            hitRate: Math.round(this.stats.hitRate * 100) / 100,
            averageAccessTime: Math.round(this.stats.averageAccessTime * 1000) / 1000, // Round to 3 decimal places
            memoryUsage: this.estimateMemoryUsage(),
            fillRate: (this.stats.size / this.maxSize) * 100
        };
    }

    // Estimate memory usage (rough calculation)
    estimateMemoryUsage() {
        let totalSize = 0;
        
        for (const [key, item] of this.cache) {
            // Rough estimation: key size + value size + metadata
            totalSize += JSON.stringify(key).length;
            totalSize += JSON.stringify(item.value).length;
            totalSize += 50; // Estimated metadata overhead
        }
        
        return {
            bytes: totalSize,
            kb: Math.round(totalSize / 1024 * 100) / 100,
            mb: Math.round(totalSize / 1024 / 1024 * 100) / 100
        };
    }

    // Export cache data for backup/restore
    export() {
        const data = [];
        for (const [key, item] of this.cache) {
            if (this.isValid(item)) {
                data.push({
                    key,
                    value: item.value,
                    expiry: item.expiry,
                    created: item.created
                });
            }
        }
        return data;
    }

    // Import cache data from backup
    import(data) {
        let imported = 0;
        const now = Date.now();
        
        for (const item of data) {
            if (item.expiry > now) {
                this.cache.set(item.key, {
                    value: item.value,
                    expiry: item.expiry,
                    created: item.created,
                    accessed: now
                });
                this.accessOrder.set(item.key, now);
                imported++;
            }
        }
        
        this.stats.size = this.cache.size;
        console.log(`📥 Cache import: loaded ${imported} valid entries`);
        return imported;
    }

    // Get top accessed entries for analysis
    getTopEntries(limit = 10) {
        const entries = Array.from(this.accessOrder.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([key, lastAccessed]) => ({
                key,
                lastAccessed: new Date(lastAccessed),
                item: this.cache.get(key)
            }));
        
        return entries;
    }

    // Optimize cache by removing least valuable entries
    optimize(targetFillRate = 0.8) {
        const targetSize = Math.floor(this.maxSize * targetFillRate);
        let removed = 0;
        
        if (this.cache.size <= targetSize) {
            return removed;
        }
        
        // Remove entries in LRU order until we reach target size
        const sortedEntries = Array.from(this.accessOrder.entries())
            .sort((a, b) => a[1] - b[1]); // Oldest first
        
        const toRemove = this.cache.size - targetSize;
        for (let i = 0; i < toRemove && i < sortedEntries.length; i++) {
            const [key] = sortedEntries[i];
            this.delete(key);
            removed++;
        }
        
        console.log(`⚡ Cache optimization: removed ${removed} entries`);
        return removed;
    }
}

// Multi-level cache system for different data types
class MultiLevelCache {
    constructor() {
        this.definitionCache = new EnhancedLRUCache(1000, 3600000); // 1 hour
        this.analysisCache = new EnhancedLRUCache(500, 1800000);    // 30 minutes
        this.imageCache = new EnhancedLRUCache(100, 7200000);       // 2 hours
        this.frequentWordsCache = new EnhancedLRUCache(2000, 86400000); // 24 hours
    }

    // Get appropriate cache based on data type
    getCache(type) {
        switch (type) {
            case 'definition': return this.definitionCache;
            case 'analysis': return this.analysisCache;
            case 'image': return this.imageCache;
            case 'frequent': return this.frequentWordsCache;
            default: return this.definitionCache;
        }
    }

    get(key, type = 'definition', performanceMonitor = null) {
        return this.getCache(type).get(key, performanceMonitor);
    }

    set(key, value, type = 'definition', customTTL = null) {
        return this.getCache(type).set(key, value, customTTL);
    }

    // Warm up cache with common words
    warmUp(commonWords) {
        return this.frequentWordsCache.preload(commonWords);
    }

    // Get comprehensive stats
    getAllStats() {
        return {
            definition: this.definitionCache.getStats(),
            analysis: this.analysisCache.getStats(),
            image: this.imageCache.getStats(),
            frequent: this.frequentWordsCache.getStats(),
            total: {
                size: this.definitionCache.stats.size + 
                      this.analysisCache.stats.size + 
                      this.imageCache.stats.size + 
                      this.frequentWordsCache.stats.size,
                hits: this.definitionCache.stats.hits + 
                      this.analysisCache.stats.hits + 
                      this.imageCache.stats.hits + 
                      this.frequentWordsCache.stats.hits,
                misses: this.definitionCache.stats.misses + 
                        this.analysisCache.stats.misses + 
                        this.imageCache.stats.misses + 
                        this.frequentWordsCache.stats.misses
            }
        };
    }

    // Clear all caches
    clearAll() {
        this.definitionCache.clear();
        this.analysisCache.clear();
        this.imageCache.clear();
        this.frequentWordsCache.clear();
    }

    // Optimize all caches
    optimizeAll() {
        const results = {
            definition: this.definitionCache.optimize(),
            analysis: this.analysisCache.optimize(),
            image: this.imageCache.optimize(),
            frequent: this.frequentWordsCache.optimize()
        };
        
        const totalRemoved = Object.values(results).reduce((a, b) => a + b, 0);
        console.log(`🚀 Multi-level cache optimization: removed ${totalRemoved} total entries`);
        
        return results;
    }
}

export { EnhancedLRUCache, MultiLevelCache };