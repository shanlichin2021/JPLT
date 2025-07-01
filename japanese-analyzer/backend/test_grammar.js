// Test script for enhanced grammar analysis
import express from 'express';
import cors from 'cors';

const app = express();
const port = 3001;

app.use(express.json());
app.use(cors());

// Copy the enhanced grammar analysis logic
function getCharType(char) {
    if (/[\u4e00-\u9faf]/.test(char)) return 'kanji';
    if (/[\u3040-\u309f]/.test(char)) return 'hiragana';
    if (/[\u30a0-\u30ff]/.test(char)) return 'katakana';
    if (/[a-zA-Z]/.test(char)) return 'latin';
    if (/[0-9]/.test(char)) return 'number';
    if (/\s/.test(char)) return 'space';
    return 'punctuation';
}

function estimateGrammar(text, charType) {
    const grammarPatterns = {
        particles: ['は', 'が', 'を', 'に', 'で', 'と', 'や', 'の', 'から', 'まで', 'より', 'も', 'だけ', 'しか', 'ほど', 'くらい', 'ぐらい', 'など', 'なんか', 'って', 'という', 'といった', 'による', 'について', 'に対して', 'か', 'かな', 'かしら', 'よ', 'ね', 'な', 'わ', 'ぞ', 'ぜ', 'さ'],
        verbs: ['する', 'いる', 'ある', 'なる', 'くる', 'いく', 'みる', 'きく', 'いう', 'おもう', 'かんがえる', 'わかる', 'しる', 'できる', 'たべる', 'のむ'],
        adjectives: ['いい', 'わるい', 'おおきい', 'ちいさい', 'あたらしい', 'ふるい', 'たかい', 'やすい', 'きれい', 'すごい', 'おもしろい', 'つまらない'],
        adverbs: ['とても', 'すごく', 'ちょっと', 'すこし', 'たくさん', 'いっぱい', 'ずっと', 'きっと', 'もっと', 'やっぱり', 'やはり', 'もちろん', 'たぶん', 'きっと'],
        numbers: /^[0-9]+$|^[一二三四五六七八九十百千万億兆]+$/,
        demonstratives: ['これ', 'それ', 'あれ', 'どれ', 'ここ', 'そこ', 'あそこ', 'どこ', 'こう', 'そう', 'ああ', 'どう', 'この', 'その', 'あの', 'どの']
    };
    
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
    
    if (grammarPatterns.numbers.test(text)) {
        return { pos: 'Number', confidence: 0.9, rule: 'number_pattern' };
    }
    
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
    
    if (text.endsWith('い') && charType === 'hiragana' && text.length > 1) {
        return { pos: 'Adjective', confidence: 0.6, rule: 'i_adjective_ending' };
    }
    if (text.endsWith('な')) {
        return { pos: 'Adjective', confidence: 0.6, rule: 'na_adjective_ending' };
    }
    
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

function enhancedTokenize(text) {
    const chunks = [];
    let currentChunk = '';
    let currentType = '';
    
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const charType = getCharType(char);
        
        if (charType === 'space') {
            if (currentChunk) {
                const grammarEstimate = estimateGrammar(currentChunk, currentType);
                chunks.push({
                    text: currentChunk,
                    grammar: {
                        pos: grammarEstimate.pos,
                        lemma: currentChunk,
                        features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                        role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
                    }
                });
                currentChunk = '';
                currentType = '';
            }
            continue;
        }
        
        if (currentType === '' || currentType === charType || 
            (currentType === 'kanji' && charType === 'hiragana') ||
            (currentType === 'hiragana' && charType === 'kanji')) {
            currentChunk += char;
            if (currentType === '') currentType = charType;
        } else {
            if (currentChunk) {
                const grammarEstimate = estimateGrammar(currentChunk, currentType);
                chunks.push({
                    text: currentChunk,
                    grammar: {
                        pos: grammarEstimate.pos,
                        lemma: currentChunk,
                        features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                        role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
                    }
                });
            }
            currentChunk = char;
            currentType = charType;
        }
    }
    
    if (currentChunk) {
        const grammarEstimate = estimateGrammar(currentChunk, currentType);
        chunks.push({
            text: currentChunk,
            grammar: {
                pos: grammarEstimate.pos,
                lemma: currentChunk,
                features: [`Enhanced-fallback-${grammarEstimate.rule}`, `Confidence-${Math.round(grammarEstimate.confidence * 100)}%`],
                role: `Enhanced fallback analysis - ${grammarEstimate.rule}`
            }
        });
    }
    
    return chunks;
}

app.post('/test-grammar', (req, res) => {
    const { text } = req.body;
    console.log(`Testing enhanced grammar analysis for: "${text}"`);
    
    const tokens = enhancedTokenize(text);
    
    res.json({
        input: text,
        tokens: tokens,
        summary: {
            tokenCount: tokens.length,
            grammarBreakdown: tokens.reduce((acc, token) => {
                acc[token.grammar.pos] = (acc[token.grammar.pos] || 0) + 1;
                return acc;
            }, {})
        }
    });
});

app.listen(port, () => {
    console.log(`🧪 Grammar test server running at http://localhost:${port}`);
    console.log('Test with: POST /test-grammar {"text": "これは日本語です"}');
});