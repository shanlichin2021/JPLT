// backend/enhanced_server.js - Improved dictionary lookup and segmentation support with Performance Optimization

// --- IMPORTS and SETUP ---
import express from 'express';
import cors from 'cors';
import wanakana from 'wanakana';
import multer from 'multer';
import FormData from 'form-data';
import axios from 'axios';
import sqlite3 from 'sqlite3';

// Performance optimization imports
import PerformanceMonitor from './performance-monitor.js';
import { MultiLevelCache } from './enhanced-cache.js';
import RequestOptimizer from './request-optimizer.js';
import createPerformanceAPI from './performance-api.js';

const app = express();
const port = 3000;
const OCR_SERVICE_URL = 'http://localhost:8000/ocr';
const PARSER_SERVICE_URL = 'http://localhost:8001/analyze';
const VECTOR_SERVICE_URL = 'http://localhost:8001/vector';
const DB_PATH = './dictionary.sqlite';

// Initialize performance optimization systems
const performanceMonitor = new PerformanceMonitor();
const multiLevelCache = new MultiLevelCache();
const requestOptimizer = new RequestOptimizer();

// Database connection with performance monitoring
const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
        console.error("CRITICAL ERROR: Could not connect to the dictionary database.", err.message);
        process.exit(1);
    } else {
        console.log("✅ Successfully connected to the local dictionary database.");
        console.log("🚀 Performance monitoring systems initialized");
    }
});

// Setup middleware with optimizations
const upload = multer({ 
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB limit
    }
});

// Apply performance optimizations
app.use(requestOptimizer.createCompressionMiddleware());
app.use(express.json({ limit: '5mb' }));
app.use(cors());

// Apply rate limiting
const rateLimiters = requestOptimizer.createRateLimiters();
app.use('/api/analyze-image', rateLimiters.ocr);
app.use('/api/full-analysis', rateLimiters.analysis);
app.use('/api/debug-lookup', rateLimiters.dictionary);
app.use(rateLimiters.general);

// Apply request deduplication
app.use(requestOptimizer.createDeduplicationMiddleware());

// Circuit breakers for external services
const parserCircuitBreaker = requestOptimizer.createCircuitBreaker('parser', {
    failureThreshold: 3,
    resetTimeout: 30000
});

const ocrCircuitBreaker = requestOptimizer.createCircuitBreaker('ocr', {
    failureThreshold: 5,
    resetTimeout: 60000
});

// Start cleanup processes
requestOptimizer.startCleanupProcess();

// Enhanced fallback tokenization function
function basicTokenize(text) {
    const chunks = [];
    let currentChunk = '';
    let currentType = '';
    
    // Helper function to determine character type and better grammar estimation
    function getCharType(char) {
        if (/[\u4e00-\u9faf]/.test(char)) return 'kanji';
        if (/[\u3040-\u309f]/.test(char)) return 'hiragana';
        if (/[\u30a0-\u30ff]/.test(char)) return 'katakana';
        if (/[a-zA-Z]/.test(char)) return 'latin';
        if (/[0-9]/.test(char)) return 'number';
        if (/\s/.test(char)) return 'space';
        return 'punctuation';
    }
    
    // Enhanced grammar estimation based on text patterns
    function estimateGrammar(text, charType) {
        // Common Japanese grammar patterns for better POS estimation
        const grammarPatterns = {
            // Particles
            particles: ['は', 'が', 'を', 'に', 'で', 'と', 'や', 'の', 'から', 'まで', 'より', 'も', 'だけ', 'しか', 'ほど', 'くらい', 'ぐらい', 'など', 'なんか', 'って', 'という', 'といった', 'による', 'について', 'に対して', 'か', 'かな', 'かしら', 'よ', 'ね', 'な', 'わ', 'ぞ', 'ぜ', 'さ'],
            
            // Common verbs
            verbs: ['する', 'いる', 'ある', 'なる', 'くる', 'いく', 'みる', 'きく', 'いう', 'おもう', 'かんがえる', 'わかる', 'しる', 'できる', 'たべる', 'のむ'],
            
            // Common adjectives
            adjectives: ['いい', 'わるい', 'おおきい', 'ちいさい', 'あたらしい', 'ふるい', 'たかい', 'やすい', 'きれい', 'すごい', 'おもしろい', 'つまらない'],
            
            // Adverbs
            adverbs: ['とても', 'すごく', 'ちょっと', 'すこし', 'たくさん', 'いっぱい', 'ずっと', 'きっと', 'もっと', 'やっぱり', 'やはり', 'もちろん', 'たぶん', 'きっと'],
            
            // Numbers and counters
            numbers: /^[0-9]+$|^[一二三四五六七八九十百千万億兆]+$/,
            
            // Demonstratives
            demonstratives: ['これ', 'それ', 'あれ', 'どれ', 'ここ', 'そこ', 'あそこ', 'どこ', 'こう', 'そう', 'ああ', 'どう', 'この', 'その', 'あの', 'どの']
        };
        
        // Check for exact matches first
        if (grammarPatterns.particles.includes(text)) {
            return { pos: 'Particle', confidence: 0.9, rule: 'particle_list' };
        }
        if (grammarPatterns.verbs.includes(text)) {
            return { pos: 'Verb', confidence: 0.8, rule: 'verb_list' };
        }
        if (grammarPatterns.adjectives.includes(text)) {
            return { pos: 'Adjective', confidence: 0.8, rule: 'adjective_list' };
        }
        if (grammarPatterns.adverbs.includes(text)) {
            return { pos: 'Adverb', confidence: 0.8, rule: 'adverb_list' };
        }
        if (grammarPatterns.demonstratives.includes(text)) {
            return { pos: 'Pronoun', confidence: 0.8, rule: 'demonstrative_list' };
        }
        
        // Pattern-based rules
        if (grammarPatterns.numbers.test(text)) {
            return { pos: 'Number', confidence: 0.9, rule: 'number_pattern' };
        }
        
        // Verb ending patterns
        if (text.endsWith('る') && text.length > 1) {
            return { pos: 'Verb', confidence: 0.6, rule: 'ru_verb_ending' };
        }
        if (text.endsWith('た') || text.endsWith('だ')) {
            return { pos: 'Verb', confidence: 0.7, rule: 'past_verb_ending' };
        }
        if (text.endsWith('て') || text.endsWith('で')) {
            return { pos: 'Verb', confidence: 0.7, rule: 'te_form_ending' };
        }
        if (text.endsWith('ます') || text.endsWith('です')) {
            return { pos: 'Auxiliary', confidence: 0.8, rule: 'polite_ending' };
        }
        
        // Adjective patterns
        if (text.endsWith('い') && charType === 'hiragana' && text.length > 1) {
            return { pos: 'Adjective', confidence: 0.6, rule: 'i_adjective_ending' };
        }
        if (text.endsWith('な')) {
            return { pos: 'Adjective', confidence: 0.6, rule: 'na_adjective_ending' };
        }
        
        // Character type based fallback
        switch (charType) {
            case 'kanji':
                return { pos: 'Noun', confidence: 0.5, rule: 'kanji_default' };
            case 'katakana':
                return { pos: 'Noun', confidence: 0.6, rule: 'katakana_default' };
            case 'hiragana':
                return { pos: 'Particle', confidence: 0.4, rule: 'hiragana_default' };
            case 'latin':
                return { pos: 'Noun', confidence: 0.7, rule: 'latin_default' };
            case 'number':
                return { pos: 'Number', confidence: 0.9, rule: 'number_default' };
            default:
                return { pos: 'Unknown', confidence: 0.1, rule: 'fallback_default' };
        }
    }
    
    // Group characters by type for better segmentation
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const charType = getCharType(char);
        
        // Skip spaces
        if (charType === 'space') {
            if (currentChunk) {
                const grammarEstimate = estimateGrammar(currentChunk, currentType);
                chunks.push({
                    text: currentChunk,
                    reading: currentChunk,
                    lemma_to_lookup: currentChunk,
                    grammar: {
                        pos: grammarEstimate.pos,
                        lemma: currentChunk,
                        features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                        role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
                    },
                    context: null,
                    dependency: null
                });
                currentChunk = '';
                currentType = '';
            }
            continue;
        }
        
        // Start new chunk or continue current one
        if (currentType === '' || currentType === charType || 
            (currentType === 'kanji' && charType === 'hiragana') ||
            (currentType === 'hiragana' && charType === 'kanji')) {
            currentChunk += char;
            if (currentType === '') currentType = charType;
        } else {
            // Different type, finish current chunk and start new one
            if (currentChunk) {
                const grammarEstimate = estimateGrammar(currentChunk, currentType);
                chunks.push({
                    text: currentChunk,
                    reading: currentChunk,
                    lemma_to_lookup: currentChunk,
                    grammar: {
                        pos: grammarEstimate.pos,
                        lemma: currentChunk,
                        features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                        role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
                    },
                    context: null,
                    dependency: null
                });
            }
            currentChunk = char;
            currentType = charType;
        }
    }
    
    // Don't forget the last chunk
    if (currentChunk) {
        const grammarEstimate = estimateGrammar(currentChunk, currentType);
        chunks.push({
            text: currentChunk,
            reading: currentChunk,
            lemma_to_lookup: currentChunk,
            grammar: {
                pos: grammarEstimate.pos,
                lemma: currentChunk,
                features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
            },
            context: null,
            dependency: null
        });
    }
    
    // If no chunks were created (shouldn't happen), fall back to character-by-character
    if (chunks.length === 0) {
        return text.split('').map((char, index) => {
            const charType = getCharType(char);
            const grammarEstimate = estimateGrammar(char, charType);
            return {
                text: char,
                reading: char,
                lemma_to_lookup: char,
                grammar: {
                    pos: grammarEstimate.pos,
                    lemma: char,
                    features: [`Emergency-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                    role: `Emergency fallback - character ${index + 1}`
                },
                context: null,
                dependency: null
            };
        });
    }
    
    return chunks;
}

// --- ENHANCED DICTIONARY LOOKUP SYSTEM ---

// Comprehensive mapping for orthographic variations
const comprehensiveVariantMappings = new Map([
    // Core demonstrative expressions (the main issue from your examples)
    ['なんて', ['なんて', '何て', 'なん', 'て']],
    ['なんで', ['なんで', '何で', 'なん', 'で']],
    ['なんか', ['なんか', '何か', 'なん', 'か']],
    ['なんだか', ['なんだか', '何だか', 'なん', 'だか']],
    ['なんと', ['なんと', '何と', 'なん', 'と']],
    ['なんの', ['なんの', '何の', 'なん', 'の']],
    
    ['どんな', ['どんな', 'どの様な', 'どん', 'な']],
    ['そんな', ['そんな', 'その様な', 'そん', 'な']],
    ['こんな', ['こんな', 'この様な', 'こん', 'な']],
    ['あんな', ['あんな', 'あの様な', 'あん', 'な']],
    ['いろんな', ['いろんな', '色んな', '色々な', 'いろ', 'んな']],
    
    // Compound adverbs
    ['やっぱり', ['やっぱり', 'やはり', 'やっぱ', 'り']],
    ['ちょっと', ['ちょっと', '一寸', 'ちょっ', 'と']],
    ['ずっと', ['ずっと', 'ずー', 'っと']],
    ['きっと', ['きっと', '屹度', 'きー', 'っと']],
    ['もっと', ['もっと', 'もー', 'っと']],
    
    // Quantity expressions
    ['たくさん', ['沢山', 'たくさん', 'たく', 'さん']],
    ['いっぱい', ['一杯', 'いっぱい', 'いっ', 'ぱい']],
    ['すこし', ['少し', 'すこし', 'すこ', 'し']],
    ['かなり', ['可成り', 'かなり', 'かな', 'り']],
    
    // Common verbs with inflection patterns
    ['取り除く', ['取り除く', '取り除いて', '取り除い', 'て', '取り除か', '取り除け']],
    ['取り除いて', ['取り除いて', '取り除く', '取り除い', 'て']],
    ['やる', ['やる', '遣る', 'やっ', 'やら', 'やり', 'やれ']],
    ['する', ['する', '為る', 'し', 'さ', 'せ', 'すれ']],
    ['いる', ['いる', '居る', 'い', 'いれ', 'いら']],
    ['ある', ['ある', '有る', '在る', 'あっ', 'あら', 'あり', 'あれ']],
    ['くる', ['来る', 'くる', 'き', 'こ', 'くれ']],
    ['いく', ['行く', 'いく', 'いっ', 'いか', 'いけ']],
    
    // Adjectives
    ['きれい', ['綺麗', 'きれい', '奇麗', 'きれ']],
    ['すごい', ['凄い', 'すごい', 'すご', 'すげー']],
    ['下品', ['下品', 'げひん']],
    ['装備', ['装備', 'そうび']],
    
    // Particles and function words
    ['も', ['も']],
    ['すぐ', ['すぐ', '直ぐ']],
    ['リンク', ['リンク', 'link']],
    
    // Complex expressions from your examples
    ['縦書き', ['縦書き', 'たてがき']],
    ['前提', ['前提', 'ぜんてい']],
    ['横書き', ['横書き', 'よこがき']],
    ['不能', ['不能', 'ふのう']],
    ['書体', ['書体', 'しょたい']],
    ['存在', ['存在', 'そんざい']],
    ['漢字', ['漢字', 'かんじ']],
    ['仮名', ['仮名', 'かな']],
    ['筆順', ['筆順', 'ひつじゅん']],
    ['表記', ['表記', 'ひょうき']],
    ['行う', ['行う', 'おこなう', '行っ', '行い', '行え']],
    ['行って', ['行って', 'おこなって', '行う']],
    ['行っていた', ['行っていた', 'おこなっていた', '行う']],
    
    // More inflection patterns
    ['倣い', ['倣い', 'ならい', '倣う']],
    ['進めて', ['進めて', 'すすめて', '進める']],
    ['として', ['として', 'と', 'して']],
    ['おり', ['おり', '居り', '居る']],
]);

// Generate comprehensive reverse mappings
const reverseVariantMappings = new Map();
comprehensiveVariantMappings.forEach((variants, base) => {
    variants.forEach(variant => {
        if (!reverseVariantMappings.has(variant)) {
            reverseVariantMappings.set(variant, new Set());
        }
        // Add all variants as potential matches
        variants.forEach(v => reverseVariantMappings.get(variant).add(v));
        // Also add the base form
        reverseVariantMappings.get(variant).add(base);
    });
});

// Convert sets to arrays for easier processing
reverseVariantMappings.forEach((variantSet, key) => {
    reverseVariantMappings.set(key, Array.from(variantSet));
});

// Enhanced variant generation with inflection analysis
function generateComprehensiveVariants(word) {
    const variants = new Set([word]);
    
    // 1. Direct mappings from our comprehensive list
    if (comprehensiveVariantMappings.has(word)) {
        comprehensiveVariantMappings.get(word).forEach(variant => variants.add(variant));
    }
    
    if (reverseVariantMappings.has(word)) {
        reverseVariantMappings.get(word).forEach(variant => variants.add(variant));
    }
    
    // 2. Hiragana/Katakana conversion
    if (wanakana.isHiragana(word)) {
        variants.add(wanakana.toKatakana(word));
    }
    if (wanakana.isKatakana(word)) {
        variants.add(wanakana.toHiragana(word));
    }
    
    // 3. Handle verb inflection patterns more systematically
    if (word.length > 2) {
        // て-form variations
        if (word.endsWith('て')) {
            const stem = word.slice(0, -1);
            variants.add(stem + 'で');
            variants.add(stem); // just the stem
            // Try u-form (dictionary form)
            if (stem.endsWith('い')) {
                variants.add(stem.slice(0, -1) + 'く');
            }
            // Try other common endings
            ['る', 'た', 'ない', 'ます'].forEach(ending => {
                variants.add(stem + ending);
            });
        }
        
        if (word.endsWith('で')) {
            const stem = word.slice(0, -1);
            variants.add(stem + 'て');
            variants.add(stem);
        }
        
        // Past tense variations
        if (word.endsWith('た')) {
            const stem = word.slice(0, -1);
            variants.add(stem + 'て');
            variants.add(stem + 'る');
            variants.add(stem);
        }
        
        // い-adjective variations
        if (word.endsWith('い') && word.length > 2) {
            const stem = word.slice(0, -1);
            variants.add(stem + 'く');
            variants.add(stem + 'かった');
            variants.add(stem + 'くない');
        }
        
        // Compound word splitting (for words like 取り除いて)
        const compoundPatterns = [
            /^(.+り)(.+)$/,  // -ri + something
            /^(.+)して$/,    // something + shite
            /^(.+)いて$/,    // something + ite
            /^(.+)って$/,    // something + tte
        ];
        
        compoundPatterns.forEach(pattern => {
            const match = word.match(pattern);
            if (match) {
                variants.add(match[1]); // first part
                if (match[2]) variants.add(match[2]); // second part
            }
        });
    }
    
    // 4. Handle specific particle combinations
    const particleCombinations = ['も', 'は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで'];
    particleCombinations.forEach(particle => {
        if (word.endsWith(particle) && word.length > particle.length) {
            variants.add(word.slice(0, -particle.length));
        }
        // Also try adding particles to the word
        variants.add(word + particle);
    });
    
    // 5. Handle なん- prefix variations
    if (word.startsWith('なん')) {
        const suffix = word.slice(2);
        variants.add('何' + suffix);
        // Also try splitting
        variants.add('なん');
        if (suffix) variants.add(suffix);
    }
    
    // 6. Handle -んな suffix variations  
    if (word.endsWith('んな')) {
        const prefix = word.slice(0, -2);
        variants.add(prefix + 'な');
        variants.add(prefix);
        variants.add('んな');
    }
    
    return Array.from(variants).filter(v => v.length > 0);
}

async function getDefinitionAdvanced(word) {
    // Check enhanced cache first
    const cachedResult = multiLevelCache.get(word, 'definition', performanceMonitor);
    if (cachedResult) return cachedResult;
    
    const queryDb = (sql, params) => new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
    });
    
    const queryDbAll = (sql, params) => new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => err ? reject(err) : resolve(rows));
    });
    
    try {
        // Handle common particles and grammatical words first
        const particleDefinitions = {
            'は': {
                slug: 'は',
                japanese: [{ word: 'は', reading: 'は' }],
                senses: [{
                    english_definitions: ['topic marker particle', 'as for', 'regarding'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_wa' }
            },
            'が': {
                slug: 'が',
                japanese: [{ word: 'が', reading: 'が' }],
                senses: [{
                    english_definitions: ['subject marker particle', 'nominative particle'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_ga' }
            },
            'を': {
                slug: 'を',
                japanese: [{ word: 'を', reading: 'を' }],
                senses: [{
                    english_definitions: ['direct object marker particle', 'accusative particle'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_wo' }
            },
            'に': {
                slug: 'に',
                japanese: [{ word: 'に', reading: 'に' }],
                senses: [{
                    english_definitions: ['location/direction particle', 'at', 'in', 'to'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_ni' }
            },
            'で': {
                slug: 'で',
                japanese: [{ word: 'で', reading: 'で' }],
                senses: [{
                    english_definitions: ['location/method particle', 'at', 'in', 'with', 'by'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_de' }
            },
            'と': {
                slug: 'と',
                japanese: [{ word: 'と', reading: 'と' }],
                senses: [{
                    english_definitions: ['conjunction particle', 'and', 'with'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_to' }
            },
            'も': {
                slug: 'も',
                japanese: [{ word: 'も', reading: 'も' }],
                senses: [{
                    english_definitions: ['inclusive particle', 'also', 'too', 'even'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_mo' }
            },
            'から': {
                slug: 'から',
                japanese: [{ word: 'から', reading: 'から' }],
                senses: [{
                    english_definitions: ['from', 'since', 'because'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_kara' }
            },
            'まで': {
                slug: 'まで',
                japanese: [{ word: 'まで', reading: 'まで' }],
                senses: [{
                    english_definitions: ['until', 'to', 'up to'],
                    parts_of_speech: ['particle']
                }],
                searchInfo: { originalQuery: word, foundVia: 'particle_handling', entryId: 'particle_made' }
            },
            '。': {
                slug: '。',
                japanese: [{ word: '。', reading: '。' }],
                senses: [{
                    english_definitions: ['period', 'full stop'],
                    parts_of_speech: ['punctuation']
                }],
                searchInfo: { originalQuery: word, foundVia: 'punctuation_handling', entryId: 'punct_period' }
            },
            '、': {
                slug: '、',
                japanese: [{ word: '、', reading: '、' }],
                senses: [{
                    english_definitions: ['comma'],
                    parts_of_speech: ['punctuation']
                }],
                searchInfo: { originalQuery: word, foundVia: 'punctuation_handling', entryId: 'punct_comma' }
            },
            '？': {
                slug: '？',
                japanese: [{ word: '？', reading: '？' }],
                senses: [{
                    english_definitions: ['question mark'],
                    parts_of_speech: ['punctuation']
                }],
                searchInfo: { originalQuery: word, foundVia: 'punctuation_handling', entryId: 'punct_question' }
            },
            '！': {
                slug: '！',
                japanese: [{ word: '！', reading: '！' }],
                senses: [{
                    english_definitions: ['exclamation mark'],
                    parts_of_speech: ['punctuation']
                }],
                searchInfo: { originalQuery: word, foundVia: 'punctuation_handling', entryId: 'punct_exclamation' }
            }
        };
        
        if (particleDefinitions[word]) {
            console.log(`✅ Found particle definition for "${word}"`);
            const definition = particleDefinitions[word];
            multiLevelCache.set(word, definition, 'definition');
            return definition;
        }
        
        const searchVariants = generateComprehensiveVariants(word);
        console.log(`🔍 Advanced search for "${word}" with ${searchVariants.length} variants:`, searchVariants.slice(0, 10));
        
        // Try exact matches first
        for (const variant of [word, ...searchVariants.slice(0, 5)]) {
            const exactQuery = `
                SELECT DISTINCT e.entry_id,
                       (SELECT k.value FROM kanji k WHERE k.entry_id = e.entry_id LIMIT 1) as kanji_spelling,
                       (SELECT r.value FROM reading r WHERE r.entry_id = e.entry_id LIMIT 1) as reading
                FROM (
                    SELECT k.entry_id FROM kanji k WHERE k.value = ?
                    UNION 
                    SELECT r.entry_id FROM reading r WHERE r.value = ?
                ) e
                LIMIT 1
            `;
            
            const exactResult = await queryDb(exactQuery, [variant, variant]);
            if (exactResult) {
                console.log(`✅ Exact match found for "${variant}" -> entry_id ${exactResult.entry_id}`);
                const definition = await buildDefinitionFromEntry(exactResult.entry_id, word, variant);
                if (definition) return definition;
            }
        }
        
        // If no exact match, try partial/fuzzy matching
        const fuzzyQuery = `
            SELECT DISTINCT e.entry_id,
                   (SELECT k.value FROM kanji k WHERE k.entry_id = e.entry_id LIMIT 1) as kanji_spelling,
                   (SELECT r.value FROM reading r WHERE r.entry_id = e.entry_id LIMIT 1) as reading,
                   e.value as matched_value
            FROM (
                SELECT k.entry_id, k.value FROM kanji k WHERE k.value LIKE ? OR k.value LIKE ?
                UNION 
                SELECT r.entry_id, r.value FROM reading r WHERE r.value LIKE ? OR r.value LIKE ?
            ) e
            LIMIT 3
        `;
        
        const fuzzyParams = [
            `%${word}%`, `${word}%`,
            `%${word}%`, `${word}%`
        ];
        
        const fuzzyResults = await queryDbAll(fuzzyQuery, fuzzyParams);
        if (fuzzyResults && fuzzyResults.length > 0) {
            console.log(`🔍 Fuzzy match found for "${word}" -> entry_id ${fuzzyResults[0].entry_id}`);
            const definition = await buildDefinitionFromEntry(fuzzyResults[0].entry_id, word, fuzzyResults[0].matched_value);
            if (definition) return definition;
        }
        
        console.log(`❌ No definition found for "${word}" or its variants`);
        multiLevelCache.set(word, null, 'definition');
        return null;
        
    } catch (error) {
        console.error(`Database error while fetching definition for "${word}":`, error);
        return null;
    }
}

async function buildDefinitionFromEntry(entryId, originalWord, matchedVariant) {
    const queryDb = (sql, params) => new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
    });
    
    try {
        const entryQuery = `
            SELECT 
                (SELECT k.value FROM kanji k WHERE k.entry_id = ? LIMIT 1) as kanji_spelling,
                (SELECT r.value FROM reading r WHERE r.entry_id = ? LIMIT 1) as reading,
                json_group_array(json_object('pos', s.pos, 'gloss', json(s.gloss))) as senses
            FROM sense s
            WHERE s.entry_id = ?
        `;
        
        const entryData = await queryDb(entryQuery, [entryId, entryId, entryId]);
        
        if (!entryData || !entryData.senses) {
            return null;
        }
        
        const sensesArray = JSON.parse(entryData.senses);
        const result = {
            slug: entryData.kanji_spelling || entryData.reading || originalWord,
            japanese: [{
                word: entryData.kanji_spelling,
                reading: entryData.reading
            }],
            senses: sensesArray.map(s => ({
                english_definitions: Array.isArray(s.gloss) ? s.gloss : [s.gloss].filter(Boolean),
                parts_of_speech: s.pos ? s.pos.split(', ').filter(Boolean) : []
            })).filter(sense => sense.english_definitions.length > 0),
            searchInfo: {
                originalQuery: originalWord,
                foundVia: matchedVariant,
                entryId: entryId
            }
        };
        
        // Cache both the original word and the matched variant
        multiLevelCache.set(originalWord, result, 'definition');
        if (matchedVariant !== originalWord) {
            multiLevelCache.set(matchedVariant, result, 'definition');
        }
        
        return result;
        
    } catch (error) {
        console.error(`Error building definition for entry ${entryId}:`, error);
        return null;
    }
}

// --- HELPER FUNCTIONS ---

function createComponentArray(text, reading) {
    if (!wanakana.isJapanese(text) || !reading) {
        return [{ text, furigana: text, isKanji: false }];
    }
    
    // Handle compound expressions specially
    if (comprehensiveVariantMappings.has(text)) {
        return [{ text, furigana: reading, isKanji: wanakana.isKanji(text) }];
    }
    
    const tokenizedText = wanakana.tokenize(text, { detailed: true });
    const components = [];
    let readingIndex = 0;

    for (const token of tokenizedText) {
        const isKanji = wanakana.isKanji(token.value);
        let furigana = token.value;

        if (isKanji && reading !== text) {
            // Try to extract the corresponding reading
            const kanjiInReading = wanakana.tokenize(reading);
            furigana = kanjiInReading[readingIndex] || token.value;
            readingIndex++;
        }
        
        components.push({
            text: token.value,
            furigana: furigana,
            isKanji: isKanji,
        });
    }
    return components;
}

// --- API ENDPOINTS ---

app.post('/api/analyze-image', upload.single('image'), async (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'No image file uploaded.' });
    try {
        const form = new FormData();
        form.append('file', req.file.buffer, { filename: req.file.originalname, contentType: req.file.mimetype });
        const ocrResponse = await axios.post(OCR_SERVICE_URL, form, { headers: { ...form.getHeaders() } });
        res.json({ text: ocrResponse.data.text });
    } catch (error) {
        console.error("Failed to analyze image:", error.response ? error.response.data : error.message);
        res.status(500).json({ error: 'Failed to analyze image.' });
    }
});

// --- PERFORMANCE API ROUTES ---
app.use('/api/performance', createPerformanceAPI(performanceMonitor, multiLevelCache, requestOptimizer));

// Enhanced full-analysis endpoint with improved processing
app.post('/api/full-analysis', async (req, res) => {
    const perfTracker = performanceMonitor.startRequest('full-analysis', '/api/full-analysis');
    try {
        console.log(`📝 Analyzing text: "${req.body.text}"`);
        
        // Use circuit breaker for parser service
        const parserResponse = await requestOptimizer.executeWithCircuitBreaker(
            'parser',
            () => {
                console.log(`🔗 Connecting to parser service at ${PARSER_SERVICE_URL}`);
                return axios.post(PARSER_SERVICE_URL, { text: req.body.text });
            },
            () => {
                console.log(`⚠️ Parser service unavailable, using enhanced fallback tokenization for: "${req.body.text}"`);
                return { data: { chunks: basicTokenize(req.body.text) } };
            }
        );
        const parsedData = parserResponse.data;
        const parsedChunks = parsedData.chunks;

        if (!parsedChunks) {
            return res.json([]);
        }

        console.log(`🔧 Processing ${parsedChunks.length} chunks from enhanced parser`);

        const processedTokens = await Promise.all(
            parsedChunks.map(async (chunk, index) => {
                console.log(`Processing chunk ${index + 1}: "${chunk.text}" (lookup: "${chunk.lemma_to_lookup}")`);
                
                // Use advanced lookup with comprehensive variant matching
                let definition = await getDefinitionAdvanced(chunk.lemma_to_lookup);
                
                // Multi-step fallback strategy
                if (!definition && chunk.lemma_to_lookup !== chunk.text) {
                    console.log(`  Fallback 1: Trying surface form "${chunk.text}"`);
                    definition = await getDefinitionAdvanced(chunk.text);
                }
                
                // If still no definition and it's a compound, try splitting
                if (!definition && chunk.text.length > 2) {
                    const variants = generateComprehensiveVariants(chunk.text);
                    for (const variant of variants.slice(0, 3)) {
                        if (variant !== chunk.text && variant !== chunk.lemma_to_lookup) {
                            console.log(`  Fallback 2: Trying variant "${variant}"`);
                            definition = await getDefinitionAdvanced(variant);
                            if (definition) break;
                        }
                    }
                }
                
                // Use the best available reading, but only if it's actually needed
                let reading = null;
                const hasKanji = /[\u4e00-\u9faf]/.test(chunk.text);
                
                if (hasKanji) {
                    // Only provide reading for kanji-containing text
                    reading = definition?.japanese[0]?.reading || chunk.reading;
                    // Don't use text as fallback reading if it's the same as the surface
                    if (reading === chunk.text) {
                        reading = null;
                    }
                }
                
                console.log(`  Result: ${definition ? '✅ Found' : '❌ No'} definition, reading: "${reading || 'none'}"`);

                return {
                    surface: chunk.text,
                    isKanji: hasKanji,
                    furigana: reading,
                    definition: definition,
                    grammar: chunk.grammar || null,
                    context: chunk.context || null,
                    dependency: chunk.dependency || null,
                    components: createComponentArray(chunk.text, reading || chunk.text),
                };
            })
        );
        
        console.log(`✅ Successfully processed ${processedTokens.length} tokens`);
        
        // Prepare enhanced response with dependency parsing data
        const enhancedResponse = {
            chunks: processedTokens,
            syntactic_patterns: parsedData.syntactic_patterns || [],
            parse_validation: parsedData.parse_validation || null,
            dependency_tree: parsedData.dependency_tree || null,
            parsing_insights: parsedData.parsing_insights || null
        };
        
        // Complete performance tracking
        perfTracker.finish(true, processedTokens.length);
        
        res.json(enhancedResponse);
        
    } catch (error) {
        console.error("Error in full-analysis:", error.response ? error.response.data : error.message);
        
        // Complete performance tracking for error case
        perfTracker.finish(false, 0);
        
        res.status(500).json({ error: 'Failed to analyze text.' });
    }
});

// Enhanced debug endpoint
app.post('/api/debug-lookup', async (req, res) => {
    try {
        const { word } = req.body;
        if (!word) {
            return res.status(400).json({ error: 'No word provided' });
        }
        
        console.log(`🔍 Debug lookup for: "${word}"`);
        
        const variants = generateComprehensiveVariants(word);
        const definition = await getDefinitionAdvanced(word);
        
        // Also test the parser
        let parserResult = null;
        try {
            const parserResponse = await axios.post(PARSER_SERVICE_URL.replace('/analyze', '/debug'), { text: word });
            parserResult = parserResponse.data;
        } catch (parserError) {
            console.log("Parser debug not available:", parserError.message);
        }
        
        const debugInfo = {
            originalWord: word,
            searchVariants: variants.slice(0, 20), // Limit for readability
            totalVariants: variants.length,
            definition: definition,
            definitionFound: !!definition,
            cacheSize: multiLevelCache.getAllStats().total.size,
            parserAnalysis: parserResult,
            mappingInfo: {
                hasDirectMapping: comprehensiveVariantMappings.has(word),
                hasReverseMapping: reverseVariantMappings.has(word),
                directMappings: comprehensiveVariantMappings.get(word) || [],
                reverseMappings: reverseVariantMappings.get(word) || []
            }
        };
        
        res.json(debugInfo);
    } catch (error) {
        console.error("Error in debug lookup:", error);
        res.status(500).json({ error: 'Failed to debug lookup' });
    }
});

// Test segmentation endpoint
app.post('/api/test-segmentation', async (req, res) => {
    try {
        const { text } = req.body;
        if (!text) {
            return res.status(400).json({ error: 'No text provided' });
        }
        
        // Get both parser results
        const enhancedResponse = await axios.post(PARSER_SERVICE_URL, { text });
        const debugResponse = await axios.post(PARSER_SERVICE_URL.replace('/analyze', '/debug'), { text });
        
        res.json({
            originalText: text,
            enhancedSegmentation: enhancedResponse.data,
            segmentationAnalysis: debugResponse.data,
            summary: {
                chunkCount: enhancedResponse.data.chunks.length,
                compoundExpressionsFound: debugResponse.data.compound_expressions_found?.length || 0,
                segmentationImproved: debugResponse.data.segmentation_improvements?.length > 0
            }
        });
    } catch (error) {
        console.error("Error testing segmentation:", error);
        res.status(500).json({ error: 'Failed to test segmentation' });
    }
});

// Enhanced semantic search endpoint
app.post('/api/semantic-search', async (req, res) => {
    const perfTracker = performanceMonitor.startRequest('semantic-search', '/api/semantic-search');
    try {
        const { query, top_k = 10, similarity_threshold = 0.6, pos_filter } = req.body;
        
        if (!query) {
            return res.status(400).json({ error: 'No query provided' });
        }
        
        console.log(`🔍 Semantic search for: "${query}"`);
        
        // Try semantic search via vector service
        try {
            const vectorResponse = await axios.post(`${VECTOR_SERVICE_URL}/search`, {
                query: query,
                top_k: top_k,
                similarity_threshold: similarity_threshold,
                pos_filter: pos_filter
            });
            
            console.log(`🎯 Found ${vectorResponse.data.results.length} semantic results`);
            
            // Enhance results with additional dictionary data if needed
            const enhancedResults = await Promise.all(
                vectorResponse.data.results.map(async (result) => {
                    try {
                        // Get full dictionary definition for enhanced result
                        const fullDefinition = await getDefinitionAdvanced(result.word);
                        
                        return {
                            ...result,
                            fullDefinition: fullDefinition,
                            searchType: 'semantic',
                            enhancedScore: result.similarity
                        };
                    } catch (err) {
                        console.warn(`Failed to enhance result for ${result.word}: ${err.message}`);
                        return {
                            ...result,
                            searchType: 'semantic',
                            enhancedScore: result.similarity
                        };
                    }
                })
            );
            
            perfTracker.finish(true, enhancedResults.length);
            
            res.json({
                query: query,
                results: enhancedResults,
                searchType: 'semantic',
                totalResults: enhancedResults.length,
                searchTime: vectorResponse.data.search_time_ms,
                parameters: {
                    top_k: top_k,
                    similarity_threshold: similarity_threshold,
                    pos_filter: pos_filter
                }
            });
            
        } catch (vectorError) {
            console.warn(`Vector search failed, falling back to traditional search: ${vectorError.message}`);
            
            // Fallback to traditional dictionary search
            const fallbackResults = [];
            const definition = await getDefinitionAdvanced(query);
            
            if (definition) {
                fallbackResults.push({
                    word: query,
                    reading: definition.japanese[0]?.reading || query,
                    definitions: definition.senses[0]?.english_definitions || [],
                    pos: definition.senses[0]?.parts_of_speech || [],
                    similarity: 1.0,
                    confidence: 1.0,
                    source: 'exact_match',
                    searchType: 'fallback'
                });
            }
            
            perfTracker.finish(true, fallbackResults.length);
            
            res.json({
                query: query,
                results: fallbackResults,
                searchType: 'fallback',
                totalResults: fallbackResults.length,
                fallbackReason: 'Vector search unavailable',
                parameters: {
                    top_k: top_k,
                    similarity_threshold: similarity_threshold
                }
            });
        }
        
    } catch (error) {
        console.error("Error in semantic search:", error);
        perfTracker.finish(false, 0);
        res.status(500).json({ 
            error: 'Failed to perform semantic search',
            details: error.message 
        });
    }
});

// Related words endpoint
app.post('/api/related-words', async (req, res) => {
    const perfTracker = performanceMonitor.startRequest('related-words', '/api/related-words');
    try {
        const { word, top_k = 5, exclude_exact = true } = req.body;
        
        if (!word) {
            return res.status(400).json({ error: 'No word provided' });
        }
        
        console.log(`🔗 Finding related words for: "${word}"`);
        
        try {
            const vectorResponse = await axios.post(`${VECTOR_SERVICE_URL}/related-words`, {
                word: word,
                top_k: top_k,
                exclude_exact: exclude_exact
            });
            
            console.log(`🎯 Found ${vectorResponse.data.length} related words`);
            
            perfTracker.finish(true, vectorResponse.data.length);
            
            res.json({
                word: word,
                relatedWords: vectorResponse.data,
                totalResults: vectorResponse.data.length,
                searchType: 'semantic_similarity'
            });
            
        } catch (vectorError) {
            console.warn(`Related words search failed: ${vectorError.message}`);
            
            perfTracker.finish(false, 0);
            
            res.status(503).json({
                error: 'Related words service unavailable',
                word: word,
                relatedWords: [],
                totalResults: 0,
                searchType: 'unavailable'
            });
        }
        
    } catch (error) {
        console.error("Error finding related words:", error);
        perfTracker.finish(false, 0);
        res.status(500).json({ 
            error: 'Failed to find related words',
            details: error.message 
        });
    }
});

// --- SERVER INITIALIZATION ---
app.listen(port, () => {
    console.log(`✅ Enhanced Backend analyzer is running at http://localhost:${port}`);
    console.log("   🚀 Advanced dictionary lookup system enabled");
    console.log("   🔍 Comprehensive variant matching implemented");
    console.log("   📊 Enhanced segmentation support ready");
    console.log("   🎯 Compound expression handling optimized");
    console.log("   ⚡ Performance monitoring & optimization active");
    console.log("   🛡️ Circuit breakers & rate limiting enabled");
    console.log("   🧠 Multi-level caching system online");
    console.log("\n   🎮 Core API Endpoints:");
    console.log("   - POST /api/full-analysis (main analysis)");
    console.log("   - POST /api/debug-lookup (debug dictionary lookup)");
    console.log("   - POST /api/test-segmentation (test enhanced segmentation)");
    console.log("   - POST /api/analyze-image (OCR processing)");
    console.log("\n   🧠 Semantic Search Endpoints:");
    console.log("   - POST /api/semantic-search (intelligent word search)");
    console.log("   - POST /api/related-words (find semantically similar words)");
    console.log("\n   📊 Performance API Endpoints:");
    console.log("   - GET /api/performance/dashboard (real-time performance dashboard)");
    console.log("   - GET /api/performance/metrics (detailed metrics)");
    console.log("   - GET /api/performance/health (health check)");
    console.log("   - POST /api/performance/cache/warm (cache warming)");
    console.log("   - POST /api/performance/cache/optimize (cache optimization)");
    console.log("\n   💡 Performance Dashboard: http://localhost:3000/api/performance/dashboard");
    console.log("\n   🔧 Dependencies:");
    console.log("   - Python Parser Service: http://localhost:8001");
    console.log("   - OCR Service: http://localhost:8000");
});

process.on('SIGINT', () => {
    console.log("\nShutting down enhanced server...");
    db.close((err) => {
        if (err) console.error(err.message);
        console.log("Database connection closed.");
        process.exit(0);
    });
});