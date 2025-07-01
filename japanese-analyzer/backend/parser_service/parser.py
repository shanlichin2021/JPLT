# backend/parser_service/enhanced_parser.py - Advanced Japanese NLP with Research Improvements
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import spacy
import ginza
import re
import asyncio
import time
from typing import List, Tuple, Optional, Dict, Set, Any
from contextlib import asynccontextmanager

# Import dependency parsing validation
from dependency_parser import DependencyValidator, DependencyTree, SyntacticPattern

# Import new advanced modules with error handling
try:
    from uncertainty_quantifier import (
        MonteCarloDropoutUncertainty, EnsembleUncertainty, 
        UncertaintyResult, AdaptiveUncertaintyThreshold
    )
    UNCERTAINTY_AVAILABLE = True
    print("✅ Uncertainty quantification modules loaded")
except ImportError as e:
    print(f"⚠️  Uncertainty quantification unavailable: {e}")
    UNCERTAINTY_AVAILABLE = False
    # Create dummy classes for type hints
    class MonteCarloDropoutUncertainty: pass
    class EnsembleUncertainty: pass
    class UncertaintyResult: pass
    class AdaptiveUncertaintyThreshold: pass

try:
    from compound_verb_analyzer import (
        AspectualConstructionHandler, VerbConjugationAnalyzer, 
        CompoundWordAnalyzer, SegmentationDecision
    )
    COMPOUND_ANALYSIS_AVAILABLE = True
    print("✅ Compound verb analysis modules loaded")
except ImportError as e:
    print(f"⚠️  Compound verb analysis unavailable: {e}")
    COMPOUND_ANALYSIS_AVAILABLE = False
    # Create dummy classes
    class AspectualConstructionHandler: pass
    class VerbConjugationAnalyzer: pass
    class CompoundWordAnalyzer: pass
    class SegmentationDecision: pass

try:
    from stacked_consensus import (
        StackedGeneralizationConsensus, TokenizerResult, ConsensusResult,
        MetaFeatureExtractor, TrainingExample
    )
    STACKED_CONSENSUS_AVAILABLE = True
    print("✅ Stacked consensus modules loaded")
except ImportError as e:
    print(f"⚠️  Stacked consensus unavailable: {e}")
    STACKED_CONSENSUS_AVAILABLE = False
    # Create dummy classes
    class StackedGeneralizationConsensus: pass
    class TokenizerResult: pass
    class ConsensusResult: pass
    class MetaFeatureExtractor: pass
    class TrainingExample: pass

try:
    from advanced_transformer_integration import (
        AdvancedJapaneseTransformer, TransformerConfig, TransformerModelPool,
        create_advanced_transformer, DynamicBatchProcessor
    )
    TRANSFORMER_AVAILABLE = True
    print("✅ Advanced transformer modules loaded")
except ImportError as e:
    print(f"⚠️  Advanced transformers unavailable: {e}")
    TRANSFORMER_AVAILABLE = False
    # Create dummy classes
    class AdvancedJapaneseTransformer: pass
    class TransformerConfig: pass
    class TransformerModelPool: pass
    def create_advanced_transformer(*args, **kwargs): return None
    class DynamicBatchProcessor: pass

# Import helper functions for advanced analysis with error handling
try:
    from advanced_parser_helpers import (
        _get_base_model_predictions, _analyze_with_compound_specialization,
        _basic_chunk_analysis, _add_uncertainty_information, _create_parse_validation,
        SimpleDynamicBatchProcessor, batch_processor
    )
    ADVANCED_HELPERS_AVAILABLE = True
    print("✅ Advanced parser helpers loaded")
except ImportError as e:
    print(f"⚠️  Advanced parser helpers unavailable: {e}")
    ADVANCED_HELPERS_AVAILABLE = False
    # Create dummy functions
    async def _get_base_model_predictions(text): return {}
    async def _analyze_with_compound_specialization(result, text): return []
    async def _basic_chunk_analysis(result, text): return []
    async def _add_uncertainty_information(chunks, text): return chunks
    def _create_parse_validation(tree): return {'is_valid': False, 'errors': [], 'confidence': 0.0}
    class SimpleDynamicBatchProcessor: 
        async def process_batch(self, texts, func): return [await func(t) for t in texts]
    batch_processor = SimpleDynamicBatchProcessor()

# Import vector database capabilities
try:
    from embedding_service import initialize_embedding_service, shutdown_embedding_service, embedding_service
    from vector_database import vector_db_manager
    from vector_api import vector_router
    VECTOR_DB_AVAILABLE = True
    print("✅ Vector database modules loaded")
except ImportError as e:
    print(f"⚠️  Vector database unavailable: {e}")
    VECTOR_DB_AVAILABLE = False
    # Create dummy objects
    embedding_service = None
    vector_db_manager = None
    vector_router = None
    def initialize_embedding_service(): pass
    def shutdown_embedding_service(): pass

# Global variables for advanced features (initialized during startup)
NLP_MODEL = None
dependency_validator = None
uncertainty_quantifier = None
compound_verb_analyzer = None
stacked_consensus = None
transformer_pool = None
adaptive_threshold = None

# Initialize core NLP model at module level for immediate availability
try:
    import spacy
    import ginza
    NLP_MODEL = spacy.load("ja_ginza")
    print("✅ Core NLP model loaded at module level")
    
    # Initialize dependency validator
    from dependency_parser import DependencyValidator
    dependency_validator = DependencyValidator(NLP_MODEL)
    print("✅ Dependency validator initialized at module level")
    
    # Initialize compound verb analyzer if available
    if COMPOUND_ANALYSIS_AVAILABLE:
        compound_verb_analyzer = {
            'aspectual_handler': AspectualConstructionHandler(),
            'verb_analyzer': VerbConjugationAnalyzer(),
            'compound_analyzer': CompoundWordAnalyzer()
        }
        print("✅ Compound verb analyzer initialized at module level")
    
except Exception as e:
    print(f"⚠️  Could not initialize core NLP at module level: {e}")
    NLP_MODEL = None
    dependency_validator = None

# --- LIFESPAN CONTEXT MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global NLP_MODEL, dependency_validator, uncertainty_quantifier, compound_verb_analyzer
    global stacked_consensus, transformer_pool, adaptive_threshold
    
    # Startup
    print("SUCCESS: Advanced Japanese Parser service starting up...")
    
    try:
        # Core NLP model should already be loaded at module level
        if NLP_MODEL is None:
            # Fallback initialization if module-level loading failed
            import spacy
            import ginza
            NLP_MODEL = spacy.load("ja_ginza")
            print("SUCCESS: Fallback - loaded the GiNZA model ('ja_ginza').")
            
            if dependency_validator is None:
                dependency_validator = DependencyValidator(NLP_MODEL)
                print("SUCCESS: Fallback - dependency parsing validation system initialized.")
        else:
            print("SUCCESS: Using module-level initialized GiNZA model.")
        
        # Initialize uncertainty quantification (if available)
        global uncertainty_quantifier
        if UNCERTAINTY_AVAILABLE:
            uncertainty_quantifier = MonteCarloDropoutUncertainty(NLP_MODEL, n_samples=30)
            print("SUCCESS: Monte Carlo uncertainty quantification initialized.")
        else:
            uncertainty_quantifier = None
            print("INFO: Uncertainty quantification unavailable (missing dependencies)")
        
        # Initialize compound verb analyzer with specialized handlers (if available)
        global compound_verb_analyzer
        if COMPOUND_ANALYSIS_AVAILABLE:
            compound_verb_analyzer = {
                'aspectual_handler': AspectualConstructionHandler(),
                'verb_analyzer': VerbConjugationAnalyzer(),
                'compound_analyzer': CompoundWordAnalyzer()
            }
            print("SUCCESS: Specialized compound verb analyzers initialized.")
        else:
            compound_verb_analyzer = None
            print("INFO: Compound verb analysis unavailable")
        
        # Initialize stacked generalization consensus (if available)
        global stacked_consensus
        if STACKED_CONSENSUS_AVAILABLE:
            stacked_consensus = StackedGeneralizationConsensus()
            print("SUCCESS: Stacked generalization consensus system initialized.")
        else:
            stacked_consensus = None
            print("INFO: Stacked consensus unavailable (missing dependencies)")
        
        # Initialize adaptive uncertainty threshold (if available)
        global adaptive_threshold
        if UNCERTAINTY_AVAILABLE:
            adaptive_threshold = AdaptiveUncertaintyThreshold(initial_threshold=0.6)
            print("SUCCESS: Adaptive uncertainty threshold initialized.")
        else:
            adaptive_threshold = None
        
        # Initialize transformer model pool (only if available and GPU present)
        global transformer_pool
        if TRANSFORMER_AVAILABLE:
            try:
                import torch
                if torch.cuda.is_available():
                    transformer_configs = [
                        TransformerConfig(
                            model_name="llm-jp/llm-jp-modernbert-base",
                            max_length=8192,
                            batch_size=8,
                            device="cuda",
                            dtype=torch.float16
                        )
                    ]
                    transformer_pool = TransformerModelPool(transformer_configs)
                    await transformer_pool.initialize_pool()
                    print("SUCCESS: Advanced transformer model pool initialized.")
                else:
                    print("INFO: GPU not available, skipping transformer model pool initialization.")
                    transformer_pool = None
            except Exception as e:
                print(f"WARNING: Could not initialize transformer models: {e}")
                transformer_pool = None
        else:
            transformer_pool = None
            print("INFO: Transformer models unavailable (missing dependencies)")
        
        # Initialize vector database services if available
        if VECTOR_DB_AVAILABLE:
            try:
                await initialize_embedding_service()
                print("SUCCESS: Vector database and embedding service initialized.")
            except Exception as e:
                print(f"WARNING: Could not initialize vector database: {e}")
        
        print("🚀 All advanced Japanese NLP systems initialized successfully!")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize advanced systems: {e}")
        # Set fallback values
        if NLP_MODEL is None:
            print("CRITICAL: spaCy model not loaded - service will have limited functionality")
    
    yield
    
    # Shutdown
    if VECTOR_DB_AVAILABLE:
        try:
            await shutdown_embedding_service()
            print("SUCCESS: Vector database service shut down cleanly.")
        except Exception as e:
            print(f"WARNING: Error shutting down vector database: {e}")
    
    print("SUCCESS: Advanced Japanese Parser service shutting down cleanly.")

# --- SETUP ---
app = FastAPI(
    title="Advanced Japanese Parser with Research Enhancements", 
    version="5.0.0",
    description="Enhanced Japanese NLP with uncertainty quantification, stacked consensus, and transformer integration",
    lifespan=lifespan
)

# Include vector API router if available
if VECTOR_DB_AVAILABLE and vector_router:
    app.include_router(vector_router)
    print("✅ Vector API routes enabled")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Advanced health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Advanced Japanese Parser with Research Enhancements",
        "version": "5.0.0",
        "port": 8001,
        "nlp_model": "ja_ginza" if NLP_MODEL else "not_loaded",
        "dependency_validator": "initialized" if dependency_validator else "not_initialized",
        "uncertainty_quantifier": "initialized" if uncertainty_quantifier else "not_initialized",
        "compound_verb_analyzer": "initialized" if compound_verb_analyzer else "not_initialized",
        "stacked_consensus": "initialized" if stacked_consensus else "not_initialized",
        "transformer_pool": "initialized" if transformer_pool else "not_initialized",
        "vector_database": "initialized" if VECTOR_DB_AVAILABLE and embedding_service else "not_initialized",
        "advanced_features": {
            "monte_carlo_uncertainty": UNCERTAINTY_AVAILABLE and uncertainty_quantifier is not None,
            "aspectual_constructions": COMPOUND_ANALYSIS_AVAILABLE and compound_verb_analyzer is not None,
            "stacked_generalization": STACKED_CONSENSUS_AVAILABLE and stacked_consensus is not None,
            "transformer_models": TRANSFORMER_AVAILABLE and transformer_pool is not None,
            "vector_semantic_search": VECTOR_DB_AVAILABLE and embedding_service is not None
        },
        "feature_availability": {
            "uncertainty_modules": UNCERTAINTY_AVAILABLE,
            "compound_analysis_modules": COMPOUND_ANALYSIS_AVAILABLE,
            "stacked_consensus_modules": STACKED_CONSENSUS_AVAILABLE,
            "transformer_modules": TRANSFORMER_AVAILABLE,
            "advanced_helpers": ADVANCED_HELPERS_AVAILABLE,
            "vector_database_modules": VECTOR_DB_AVAILABLE
        }
    }

# Event handlers replaced with lifespan context manager above

# --- ENHANCED DATA MODELS ---
class AnalyzeRequest(BaseModel):
    text: str
    use_advanced_features: bool = True
    uncertainty_estimation: bool = True
    compound_verb_analysis: bool = True
    transformer_mode: str = "auto"  # "auto", "fast", "accurate", "context"

class GrammarInfo(BaseModel):
    pos: str
    lemma: str
    features: List[str]
    inflectionType: Optional[str] = None
    inflectionForm: Optional[str] = None
    role: Optional[str] = None

class ContextInfo(BaseModel):
    formality: Optional[str] = None
    nuance: Optional[str] = None
    usage: Optional[str] = None

class DependencyInfo(BaseModel):
    head_id: int
    relation: str
    children: List[int]
    depth: int
    semantic_role: Optional[str] = None

class SyntacticPatternInfo(BaseModel):
    pattern_type: str
    description: str
    confidence: float
    explanation: str

class ParseValidation(BaseModel):
    is_valid: bool
    errors: List[str]
    confidence: float
    complexity_score: float

class UncertaintyInfo(BaseModel):
    """Enhanced uncertainty information for tokens"""
    overall_uncertainty: float
    boundary_confidence: float
    pos_uncertainty: float
    reading_uncertainty: float
    compound_verb_confidence: Optional[float] = None
    consensus_method: str

class Chunk(BaseModel):
    text: str
    lemma_to_lookup: str
    reading: str
    grammar: Optional[GrammarInfo] = None
    context: Optional[ContextInfo] = None
    dependency: Optional[DependencyInfo] = None
    uncertainty: Optional[UncertaintyInfo] = None
    compound_analysis: Optional[Dict[str, Any]] = None
    
class SemanticSuggestion(BaseModel):
    word: str
    reading: str
    similarity: float
    definitions: List[str]
    pos: List[str]

class AnalysisResponse(BaseModel):
    chunks: List[Chunk]
    dependency_tree: Optional[Dict] = None
    syntactic_patterns: List[SyntacticPatternInfo] = []
    parse_validation: Optional[ParseValidation] = None
    parsing_insights: Optional[Dict] = None
    semantic_suggestions: List[SemanticSuggestion] = []

# --- ENHANCED SEGMENTATION RULES ---

# Expressions that should ALWAYS be kept together
COMPOUND_EXPRESSIONS = {
    # Demonstrative + な patterns
    'なんて', 'なんで', 'なんか', 'なんだか', 'なんと', 'なんの', 'なんに',
    'どんな', 'どんなに', 'どんだけ', 'どんより',
    'そんな', 'そんなに', 'そんじゃ', 'そんで',
    'こんな', 'こんなに', 'こんにちは', 'こんばんは', 'こんど',
    'あんな', 'あんなに', 'あんまり',
    'いろんな', 'いろいろ',
    
    # Compound particles and sentence-ending expressions
    'なの', 'なんの', 'だの', 'との', 'のに', 'のは', 'のが', 'ので', 'から',
    'けど', 'けれど', 'けれども', 'でも', 'ても', 'だって', 'って',
    'かな', 'かしら', 'でしょ', 'よね', 'わね', 'のね', 'かね',
    
    # Adverbial expressions
    'やっぱり', 'やっぱ', 'やはり',
    'ちょっと', 'ちょっとした',
    'ずっと', 'きっと', 'もっと', 'ほっと',
    'すごく', 'すっごく', 'めっちゃ',
    'ちゃんと', 'きちんと', 'しっかり',
    'だんだん', 'どんどん', 'ばんばん',
    'ぐるぐる', 'ぴかぴか', 'わくわく',
    
    # Greetings and expressions
    'ありがとう', 'おめでとう', 'すみません', 'ごめんなさい',
    'いらっしゃい', 'お疲れさま', 'よろしく',
    
    # Modal expressions
    'かもしれない', 'かもしれません', 'に違いない',
    'はずです', 'はずだ', 'わけです', 'わけだ',
    
    # Conjunctive expressions
    'それでは', 'それなら', 'だったら', 'だとしたら',
    'ところで', 'ちなみに', 'つまり', 'まあ',
    
    # Time expressions
    'いつも', 'ときどき', 'たまに', 'いつか',
    'さっき', 'いまさら', 'これから', 'さきほど',
    
    # Quantity expressions
    'たくさん', 'いっぱい', 'すこし', 'ぜんぜん',
    'みんな', 'だれも', 'なにも', 'どこも',
}

# Verb endings that should be kept with their stems
VERB_ENDINGS = {
    # Te-form and related
    'て', 'で', 'ても', 'でも', 'ては', 'では',
    'ており', 'でおり', 'ている', 'でいる',
    'てある', 'である', 'てみる', 'でみる',
    'てくる', 'でくる', 'ていく', 'でいく',
    'てしまう', 'でしまう', 'ちゃう', 'じゃう',
    
    # Other inflected forms
    'た', 'だ', 'たり', 'だり',
    'ば', 'れば', 'なら', 'たら', 'だら',
    'ず', 'ない', 'ません', 'まして',
    'ながら', 'つつ', 'がら',
    
    # Potential and passive
    'れる', 'られる', 'せる', 'させる',
    'える', 'られ', 'せ', 'させ',
    
    # Auxiliary verbs
    'です', 'ます', 'だろう', 'でしょう',
    'である', 'であり', 'であっ',
}

# Particles that can attach to various words
ATTACHABLE_PARTICLES = {
    'は', 'が', 'を', 'に', 'で', 'と', 'や', 'の', 'から', 'まで', 'より',
    'も', 'だけ', 'しか', 'ほど', 'くらい', 'ぐらい', 'など', 'なんか',
    'って', 'という', 'といった', 'による', 'について', 'に対して',
    'か', 'かな', 'かしら', 'よ', 'ね', 'な', 'わ', 'ぞ', 'ぜ', 'さ',
}

class EnhancedSegmenter:
    def __init__(self):
        self.compound_patterns = self._build_compound_patterns()
        self.verb_patterns = self._build_verb_patterns()
    
    def _build_compound_patterns(self) -> List[re.Pattern]:
        """Build regex patterns for compound expressions."""
        patterns = []
        
        # Direct compound expressions
        for expr in COMPOUND_EXPRESSIONS:
            patterns.append(re.compile(f'^{re.escape(expr)}$'))
        
        # Pattern-based compounds
        pattern_rules = [
            r'なん[でてかだとの]',  # なんで, なんて, etc.
            r'[どそこあ]んな',      # どんな, そんな, etc.
            r'いろ[んー]な',        # いろんな, いろーな
            r'やっぱ[りー]?',       # やっぱり, やっぱー
            r'ちょっと[した]?',     # ちょっと, ちょっとした
            r'[ずきも]っと',        # ずっと, きっと, もっと
            r'すご[くっ]+',         # すごく, すごっく
            r'めっちゃ[あー]?',     # めっちゃ, めっちゃー
            r'だん[だん]+',         # だんだん
            r'どん[どん]+',         # どんどん
            r'[いたくし]っぱい',    # いっぱい, たくさん variant
        ]
        
        for pattern in pattern_rules:
            patterns.append(re.compile(pattern))
        
        return patterns
    
    def _build_verb_patterns(self) -> List[re.Pattern]:
        """Build patterns for verb inflections."""
        patterns = []
        
        # Common verb stem + ending patterns
        stem_ending_patterns = [
            r'.+[いきしちにひみりえけせてねへめれげぜでべぺ][てで](?:も|は|ば|おり|いる|ある|みる|くる|いく|しまう)?',
            r'.+[あいうえお][ずないませんしたろうでしょう]+',
            r'.+[かがきぎくぐけげこご][ながらつつ]',
            r'.+[らりるれろ][れられせさせ][るられ]?',
        ]
        
        for pattern in stem_ending_patterns:
            patterns.append(re.compile(pattern))
        
        return patterns
    
    def should_merge_tokens(self, tokens: List) -> Optional[List[Tuple[List, str]]]:
        """Determine if tokens should be merged into compounds."""
        if len(tokens) < 2:
            return None
        
        merged_results = []
        combined_text = ''.join([t.text for t in tokens])
        
        # Check for direct compound expressions
        if combined_text in COMPOUND_EXPRESSIONS:
            return [(tokens, combined_text)]
        
        # Check compound patterns
        for pattern in self.compound_patterns:
            if pattern.match(combined_text):
                return [(tokens, combined_text)]
        
        # Check verb inflection patterns
        for pattern in self.verb_patterns:
            if pattern.match(combined_text):
                return [(tokens, combined_text)]
        
        # Special logic for specific patterns
        merged_results.extend(self._check_special_patterns(tokens))
        
        return merged_results if merged_results else None
    
    def _check_special_patterns(self, tokens: List) -> List[Tuple[List, str]]:
        """Check for special merging patterns."""
        results = []
        
        # Pattern 1: Verb stem + te/de form + auxiliary
        if len(tokens) >= 2:
            # Check for verb + て/で + も pattern
            if (len(tokens) >= 3 and 
                tokens[-2].text in ['て', 'で'] and 
                tokens[-1].text == 'も' and
                tokens[-3].pos_ == 'VERB'):
                # Keep verb + て/で together, separate も
                verb_te_tokens = tokens[:-1]
                mo_token = [tokens[-1]]
                verb_te_text = ''.join([t.text for t in verb_te_tokens])
                results.append((verb_te_tokens, verb_te_text))
                results.append((mo_token, 'も'))
                return results
        
        # Pattern 2: Demonstrative + な combinations
        if len(tokens) == 2:
            first, second = tokens[0].text, tokens[1].text
            if first in ['なん', 'どん', 'そん', 'こん', 'あん'] and second in ['て', 'で', 'な', 'か']:
                combined = first + second
                if combined in COMPOUND_EXPRESSIONS or any(p.match(combined) for p in self.compound_patterns):
                    results.append((tokens, combined))
        
        # Pattern 3: Adverb + っと patterns
        if len(tokens) == 2:
            if tokens[0].text in ['ずー', 'きー', 'もー'] and tokens[1].text == 'っと':
                results.append((tokens, tokens[0].text + tokens[1].text))
        
        return results
    
    def segment_enhanced(self, doc) -> List[List]:
        """Enhanced segmentation that respects Japanese compound patterns."""
        # Start with ginza bunsetsu spans as base
        original_spans = list(ginza.bunsetu_spans(doc))
        enhanced_spans = []
        
        for span in original_spans:
            tokens = list(span)
            if not tokens:
                continue
            
            # Try to merge tokens within this span
            merge_result = self.should_merge_tokens(tokens)
            
            if merge_result:
                # Use merged results
                for merged_tokens, _ in merge_result:
                    enhanced_spans.append(merged_tokens)
            else:
                # Process tokens individually or in smaller groups
                enhanced_spans.extend(self._process_span_tokens(tokens))
        
        return enhanced_spans
    
    def _process_span_tokens(self, tokens: List) -> List[List]:
        """Process tokens within a span, looking for smaller merge opportunities."""
        if len(tokens) <= 1:
            return [tokens] if tokens else []
        
        # Check if this span should be kept together (verb inflections, etc.)
        if self._should_keep_span_together(tokens):
            return [tokens]
        
        result_spans = []
        i = 0
        
        while i < len(tokens):
            merged = False
            
            # Check for verb inflection patterns that should stay together
            # First check for 3-token patterns (verb + ませ + ん/た) 
            if i + 2 < len(tokens):
                first_token = tokens[i]
                second_token = tokens[i + 1]
                third_token = tokens[i + 2]
                
                # Pattern: Verb + ませ + ん = polite negative (できません, わかりません)
                if (first_token.pos_ == 'VERB' and 
                    second_token.pos_ == 'AUX' and second_token.text == 'ませ' and
                    third_token.pos_ == 'AUX' and third_token.text == 'ん'):
                    result_spans.append([first_token, second_token, third_token])
                    i += 3
                    merged = True
                # Pattern: Verb + ませ + んでした = polite negative past
                elif (first_token.pos_ == 'VERB' and 
                      second_token.pos_ == 'AUX' and second_token.text == 'ませ' and
                      third_token.pos_ == 'AUX' and third_token.text in ['んでした', 'した']):
                    result_spans.append([first_token, second_token, third_token])
                    i += 3
                    merged = True
            
            # Check for 2-token patterns
            if not merged and i + 1 < len(tokens):
                current_token = tokens[i]
                next_token = tokens[i + 1]
                
                # Keep auxiliary verb combinations together (だっ + た = だった)
                if (current_token.pos_ == 'AUX' and next_token.pos_ == 'AUX' and
                    current_token.text in ['だっ', 'であっ', 'って'] and 
                    next_token.text in ['た', 'て']):
                    result_spans.append([current_token, next_token])
                    i += 2
                    merged = True
                # Keep verb stem + inflection together
                elif (current_token.pos_ == 'VERB' and 
                      next_token.pos_ == 'AUX' and 
                      next_token.text in ['た', 'だ', 'て', 'で', 'ます', 'ない', 'ませ']):
                    result_spans.append([current_token, next_token])
                    i += 2
                    merged = True
                # Keep auxiliary + auxiliary combinations (ませ + ん)
                elif (current_token.pos_ == 'AUX' and next_token.pos_ == 'AUX' and
                      current_token.text == 'ませ' and next_token.text == 'ん'):
                    result_spans.append([current_token, next_token])
                    i += 2
                    merged = True
                elif (current_token.pos_ in ['VERB', 'ADJ'] and 
                      next_token.text in ['た', 'て', 'で']):
                    result_spans.append([current_token, next_token])
                    i += 2
                    merged = True
            
            if not merged:
                # Try merging with next 1-3 tokens for compound expressions
                for window_size in [3, 2]:
                    if i + window_size <= len(tokens):
                        window_tokens = tokens[i:i + window_size]
                        merge_result = self.should_merge_tokens(window_tokens)
                        
                        if merge_result:
                            # Add all merged groups from this window
                            for merged_tokens, _ in merge_result:
                                result_spans.append(merged_tokens)
                            i += window_size
                            merged = True
                            break
            
            if not merged:
                # No merge found, add single token
                result_spans.append([tokens[i]])
                i += 1
        
        return result_spans
    
    def _should_keep_span_together(self, tokens: List) -> bool:
        """Determine if a span should be kept together without further segmentation."""
        if len(tokens) <= 1:
            return True
        
        # Check for verb inflection patterns
        for i in range(len(tokens) - 1):
            current = tokens[i]
            next_token = tokens[i + 1]
            
            # Verb + auxiliary patterns that should stay together
            if (current.pos_ == 'VERB' and next_token.pos_ == 'AUX'):
                # Common verb inflection patterns
                if next_token.text in ['た', 'だ', 'ます', 'ない', 'ぬ']:
                    return True
                
                # Check for common verb endings
                combined_text = current.text + next_token.text
                if any(pattern in combined_text for pattern in ['あった', 'いった', 'った', 'した', 'だった']):
                    return True
        
        # Check for known compound expressions that shouldn't be split
        combined_text = ''.join([t.text for t in tokens])
        if combined_text in COMPOUND_EXPRESSIONS:
            return True
        
        return False

# Global segmenter instance
segmenter = EnhancedSegmenter()

# --- HELPER FUNCTIONS ---
def get_token_reading(token):
    """Get the reading for a token with enhanced fallback logic."""
    # Check if token contains kanji (only kanji tokens need furigana)
    def contains_kanji(text):
        return bool(re.search(r'[\u4e00-\u9faf]', text))
    
    # If token is purely hiragana/katakana/punctuation, don't provide reading
    if not contains_kanji(token.text):
        return None
    
    # Priority 1: GiNZA morph features (most accurate)
    if token.morph:
        morph_dict = token.morph.to_dict()
        if 'Reading' in morph_dict:
            reading = morph_dict['Reading']
            # Convert katakana reading to hiragana for furigana display
            reading_hiragana = convert_katakana_to_hiragana(reading)
            # Only return reading if it's different from the original text
            if reading_hiragana != token.text:
                return reading_hiragana
    
    # Priority 2: Check legacy reading attribute
    if hasattr(token._, "reading") and token._.reading:
        # Only return reading if it's different from the original text
        if token._.reading != token.text:
            return token._.reading
    
    # Priority 3: For compound expressions with kanji, try to construct reading
    if token.text in COMPOUND_EXPRESSIONS and contains_kanji(token.text):
        compound_readings = {
            # Only include compounds that actually contain kanji
            '何て': 'なんて',
            '何だか': 'なんだか',
            '何処': 'どこ',
            '沢山': 'たくさん',
            '一杯': 'いっぱい',
            '全然': 'ぜんぜん',
            '皆': 'みんな',
            '誰': 'だれ',
            '何': 'なに',
        }
        if token.text in compound_readings:
            return compound_readings[token.text]
    
    # Priority 4: For kanji tokens, use lemma reading if available and different from text
    if contains_kanji(token.text):
        if token.lemma_ and token.lemma_ != token.text:
            return token.lemma_
    
    # No reading needed or available
    return None

def convert_katakana_to_hiragana(katakana_text):
    """Convert katakana to hiragana for furigana display."""
    if not katakana_text:
        return katakana_text
    
    # Katakana to Hiragana conversion
    hiragana = ""
    for char in katakana_text:
        # Check if character is in katakana range
        if '\u30A1' <= char <= '\u30F6':
            # Convert katakana to hiragana (offset of 96)
            hiragana += chr(ord(char) - 96)
        else:
            # Keep non-katakana characters as is
            hiragana += char
    
    return hiragana

def get_pos_description(pos_tag: str) -> str:
    """Enhanced POS tag descriptions."""
    pos_map = {
        "NOUN": "Noun",
        "VERB": "Verb", 
        "ADJ": "Adjective",
        "ADV": "Adverb",
        "ADP": "Particle",
        "PART": "Particle",
        "AUX": "Auxiliary",
        "PRON": "Pronoun",
        "DET": "Determiner",
        "NUM": "Number",
        "CONJ": "Conjunction",
        "SCONJ": "Subordinating Conjunction",
        "INTJ": "Interjection",
        "PUNCT": "Punctuation",
        "SYM": "Symbol",
        "X": "Other"
    }
    return pos_map.get(pos_tag, pos_tag)

def analyze_compound_expression(text: str) -> Tuple[str, List[str]]:
    """Analyze compound expressions for POS and features."""
    if text in COMPOUND_EXPRESSIONS:
        # Categorize compound expressions
        if text in ['なんて', 'なんで', 'なんか', 'なんだか']:
            return "Exclamatory Particle", ["Expressive", "Colloquial"]
        elif text in ['どんな', 'そんな', 'こんな', 'あんな']:
            return "Demonstrative Determiner", ["Adjectival", "Demonstrative"]
        elif text == 'いろんな':
            return "Determiner", ["Variety expression", "Colloquial"]
        elif text in ['やっぱり', 'やはり']:
            return "Adverb", ["Confirmation", "As expected"]
        elif text in ['ちょっと']:
            return "Adverb", ["Quantity", "Casual", "A little"]
        elif text in ['ずっと', 'きっと', 'もっと']:
            return "Adverb", ["Temporal/Degree"]
        elif text in ['ありがとう', 'すみません', 'ごめんなさい']:
            return "Interjection", ["Polite expression", "Social formula"]
        elif text in ['かもしれない', 'かもしれません']:
            return "Modal Expression", ["Possibility", "Uncertainty"]
        elif text == 'なの':
            return "Sentence-ending Particle", ["Explanatory", "Confirmatory", "That's how it is"]
        elif text in ['だの', 'との']:
            return "Particle", ["Listing", "Citing"]
        elif text in ['のに', 'ので', 'のは', 'のが']:
            return "Conjunctive Particle", ["Nominalization", "Connection"]
        elif text in ['けど', 'けれど', 'けれども']:
            return "Conjunctive Particle", ["But", "However", "Although"]
        elif text in ['かな', 'かしら', 'よね', 'でしょ']:
            return "Sentence-ending Particle", ["Question", "Uncertainty", "Confirmation"]
    
    return "Expression", ["Compound"]

def determine_lemma_for_lookup(tokens: List, combined_text: str) -> str:
    """Determine the best lemma for dictionary lookup."""
    # For compound expressions, use the compound itself
    if combined_text in COMPOUND_EXPRESSIONS:
        return combined_text
    
    # For verb inflections, try to find the verb stem
    if len(tokens) == 1:
        token = tokens[0]
        if token.pos_ in ["VERB", "ADJ"]:
            return token.lemma_
        else:
            return combined_text
    
    # For multi-token compounds, look for the main content word
    main_token = None
    for token in tokens:
        if token.pos_ in ["NOUN", "VERB", "ADJ"]:
            main_token = token
            break
    
    if main_token:
        return main_token.lemma_
    else:
        return combined_text

# --- API ENDPOINTS ---
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalyzeRequest):
    """Advanced text analysis with uncertainty quantification and specialized compound handling."""
    if NLP_MODEL is None:
        raise HTTPException(status_code=500, detail="GiNZA NLP model not available")
    
    start_time = time.time()
    
    # For now, use basic analysis to avoid advanced feature errors
    # TODO: Fix advanced features integration
    return await _analyze_basic(request)

async def _analyze_with_advanced_features(request: AnalyzeRequest):
    """Perform advanced analysis with all research enhancements"""
    
    # Step 1: Multi-model tokenization with uncertainty
    base_predictions = await _get_base_model_predictions(request.text)
    
    # Step 2: Stacked generalization consensus
    if stacked_consensus and stacked_consensus.is_trained:
        consensus_result = stacked_consensus.generate_consensus(base_predictions, request.text)
    else:
        # Fallback to ensemble uncertainty
        ensemble_uncertainty = EnsembleUncertainty([NLP_MODEL])
        consensus_result = ensemble_uncertainty.estimate_ensemble_uncertainty(request.text)
    
    # Step 3: Specialized compound verb analysis
    enhanced_chunks = []
    if request.compound_verb_analysis and compound_verb_analyzer:
        enhanced_chunks = await _analyze_with_compound_specialization(
            consensus_result, request.text
        )
    else:
        enhanced_chunks = await _basic_chunk_analysis(consensus_result, request.text)
    
    # Step 4: Uncertainty quantification
    if request.uncertainty_estimation and uncertainty_quantifier:
        enhanced_chunks = await _add_uncertainty_information(enhanced_chunks, request.text)
    
    # Step 5: Dependency parsing and validation
    dependency_tree = None
    syntactic_patterns = []
    parsing_insights = None
    
    if dependency_validator:
        dependency_tree = dependency_validator.parse_and_validate(request.text)
        syntactic_patterns = dependency_validator.detect_syntactic_patterns(dependency_tree)
        parsing_insights = dependency_validator.get_parsing_insights(dependency_tree)
    
    return AnalysisResponse(
        chunks=enhanced_chunks,
        dependency_tree=dependency_tree.to_dict() if dependency_tree else None,
        syntactic_patterns=syntactic_patterns,
        parse_validation=_create_parse_validation(dependency_tree) if dependency_tree else None,
        parsing_insights=parsing_insights
    )

async def _analyze_basic(request: AnalyzeRequest):
    """Basic analysis without advanced features (fallback)"""
    if dependency_validator is None:
        raise HTTPException(status_code=500, detail="Dependency validator not available")

    doc = NLP_MODEL(request.text)
    chunks: List[Chunk] = []
    
    # PHASE 3: Perform dependency parsing validation
    dependency_tree = dependency_validator.parse_and_validate(request.text)
    syntactic_patterns = dependency_validator.detect_syntactic_patterns(dependency_tree)
    parsing_insights = dependency_validator.get_parsing_insights(dependency_tree)
    
    # Map semantic roles to token indices
    semantic_role_map = {}
    for role, token_indices in dependency_tree.semantic_roles.items():
        for idx in token_indices:
            semantic_role_map[idx] = role
    
    # Use enhanced segmentation
    enhanced_spans = segmenter.segment_enhanced(doc)
    
    for token_group in enhanced_spans:
        if not token_group:
            continue
        
        # Handle merged expressions
        if len(token_group) > 1:
            combined_text = ''.join([t.text for t in token_group])
            combined_reading = ''.join([get_token_reading(t) or t.text for t in token_group])
            
            # Determine POS and features for compound
            if combined_text in COMPOUND_EXPRESSIONS:
                pos_tag, features = analyze_compound_expression(combined_text)
            else:
                # Use the main token's POS
                main_token = token_group[0]
                pos_tag = get_pos_description(main_token.pos_)
                features = ["Compound expression"]
            
            lemma_to_lookup = determine_lemma_for_lookup(token_group, combined_text)
            
            # Enhanced grammar info with dependency information
            main_token = token_group[0]
            dependency_info = DependencyInfo(
                head_id=main_token.head.i if main_token.head != main_token else -1,
                relation=main_token.dep_,
                children=[child.i for child in main_token.children],
                depth=dependency_tree.nodes[main_token.i].depth if main_token.i < len(dependency_tree.nodes) else 0,
                semantic_role=semantic_role_map.get(main_token.i)
            )
            
            grammar_info = GrammarInfo(
                pos=pos_tag,
                lemma=lemma_to_lookup,
                features=features,
                role="Compound Expression"
            )
            
            # Context analysis for compounds
            context_info = None
            if combined_text in ['なんて', 'なんで']:
                context_info = ContextInfo(
                    formality="Casual",
                    nuance="Expresses surprise, dismissal, or strong emotion",
                    usage="Often used to emphasize disbelief or strong reaction"
                )
            elif combined_text in ['どんな', 'そんな', 'こんな']:
                context_info = ContextInfo(
                    formality="Neutral",
                    nuance="Demonstrative determiner specifying type or kind",
                    usage="Used to specify or ask about the nature/type of something"
                )
            
            chunks.append(Chunk(
                text=combined_text,
                lemma_to_lookup=lemma_to_lookup,
                reading=combined_reading if combined_reading else combined_text,
                grammar=grammar_info,
                context=context_info,
                dependency=dependency_info
            ))
        
        # Handle single tokens
        else:
            token = token_group[0]
            reading = get_token_reading(token)
            
            # Enhanced features for single tokens
            features = []
            if token.morph:
                for key, value in token.morph.to_dict().items():
                    if value:
                        features.append(f"{key}: {value}")
            
            # Determine lookup lemma
            if token.pos_ in ["VERB", "ADJ"]:
                lemma_to_lookup = token.lemma_
            else:
                lemma_to_lookup = token.text
            
            # Enhanced dependency information
            dependency_info = DependencyInfo(
                head_id=token.head.i if token.head != token else -1,
                relation=token.dep_,
                children=[child.i for child in token.children],
                depth=dependency_tree.nodes[token.i].depth if token.i < len(dependency_tree.nodes) else 0,
                semantic_role=semantic_role_map.get(token.i)
            )
            
            grammar_info = GrammarInfo(
                pos=get_pos_description(token.pos_),
                lemma=token.lemma_,
                features=features,
                role=f"Dependent ({token.dep_})"
            )
            
            chunks.append(Chunk(
                text=token.text,
                lemma_to_lookup=lemma_to_lookup,
                reading=reading if reading is not None else token.text,
                grammar=grammar_info,
                context=None,
                dependency=dependency_info
            ))
    
    # Prepare syntactic patterns for response
    pattern_infos = [
        SyntacticPatternInfo(
            pattern_type=pattern.pattern_type,
            description=pattern.description,
            confidence=pattern.confidence,
            explanation=pattern.explanation
        )
        for pattern in syntactic_patterns
    ]
    
    # Prepare validation info
    parse_validation = ParseValidation(
        is_valid=dependency_tree.is_valid,
        errors=dependency_tree.validation_errors,
        confidence=parsing_insights["parsing_confidence"],
        complexity_score=parsing_insights["sentence_complexity"]["complexity_score"]
    )
    
    # Prepare dependency tree for response (simplified)
    dependency_tree_dict = {
        "nodes": [
            {
                "id": node.token_id,
                "text": node.text,
                "pos": node.pos,
                "head_id": node.head_id,
                "relation": node.relation,
                "depth": node.depth
            }
            for node in dependency_tree.nodes
        ],
        "root_id": dependency_tree.root_id,
        "semantic_roles": dependency_tree.semantic_roles
    }
    
    # PHASE 4: Generate semantic suggestions (if vector service is available)
    semantic_suggestions = []
    try:
        if embedding_service.model and embedding_service.collection:
            # Extract unique words from chunks for semantic suggestions
            unique_words = set()
            for chunk in chunks:
                if chunk.text and len(chunk.text) > 1:  # Skip single characters and particles
                    unique_words.add(chunk.text)
            
            # Get semantic suggestions for key words (limit to avoid overwhelming)
            for word in list(unique_words)[:3]:  # Limit to 3 words for performance
                try:
                    related_words = await vector_db_manager.find_related_words(
                        word=word,
                        top_k=2,  # Keep it limited
                        exclude_exact=True
                    )
                    
                    for related in related_words:
                        semantic_suggestions.append(SemanticSuggestion(
                            word=related['word'],
                            reading=related['reading'],
                            similarity=related['similarity'],
                            definitions=related['definitions'][:2],  # Limit definitions
                            pos=related['pos']
                        ))
                        
                except Exception as e:
                    print(f"Failed to get semantic suggestions for {word}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Semantic suggestions unavailable: {e}")
    
    return AnalysisResponse(
        chunks=chunks,
        dependency_tree=dependency_tree_dict,
        syntactic_patterns=pattern_infos,
        parse_validation=parse_validation,
        parsing_insights=parsing_insights,
        semantic_suggestions=semantic_suggestions
    )

# New advanced endpoints for research improvements

class BatchAnalyzeRequest(BaseModel):
    texts: List[str]
    use_advanced_features: bool = True
    uncertainty_estimation: bool = True
    compound_verb_analysis: bool = True
    transformer_mode: str = "auto"

class BatchAnalysisResponse(BaseModel):
    results: List[AnalysisResponse]
    batch_processing_time: float
    average_processing_time: float
    total_texts: int

@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalyzeRequest, background_tasks: BackgroundTasks):
    """Advanced batch text analysis with dynamic batching optimization"""
    
    if not request.texts:
        raise HTTPException(status_code=400, detail="No texts provided for analysis")
    
    if len(request.texts) > 100:
        raise HTTPException(status_code=400, detail="Batch size too large (max 100 texts)")
    
    start_time = time.time()
    
    # Use dynamic batch processor for optimal performance
    async def analyze_single_text(text: str) -> AnalysisResponse:
        try:
            analyze_request = AnalyzeRequest(
                text=text,
                use_advanced_features=request.use_advanced_features,
                uncertainty_estimation=request.uncertainty_estimation,
                compound_verb_analysis=request.compound_verb_analysis,
                transformer_mode=request.transformer_mode
            )
            result = await analyze_text(analyze_request)
            return result
        except Exception as e:
            print(f"Error analyzing text '{text[:50]}...': {e}")
            return None
    
    # Process batch with dynamic optimization - simplified approach
    results = []
    for text in request.texts:
        try:
            result = await analyze_single_text(text)
            if result:
                results.append(result)
        except Exception as e:
            print(f"Batch processing error for text '{text[:50]}...': {e}")
            # Continue with other texts
    
    # Filter out any None results from errors
    valid_results = [r for r in results if r is not None]
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(request.texts) if request.texts else 0.0
    
    return BatchAnalysisResponse(
        results=valid_results,
        batch_processing_time=total_time,
        average_processing_time=avg_time,
        total_texts=len(request.texts)
    )

class UncertaintyAnalysisRequest(BaseModel):
    text: str
    n_samples: int = 50
    threshold: float = 0.5

class UncertaintyAnalysisResponse(BaseModel):
    text: str
    overall_uncertainty: float
    token_uncertainties: List[Dict[str, Any]]
    high_uncertainty_tokens: List[Dict[str, Any]]
    confidence: float
    method: str

@app.post("/analyze/uncertainty", response_model=UncertaintyAnalysisResponse)
async def analyze_uncertainty(request: UncertaintyAnalysisRequest):
    """Dedicated uncertainty analysis endpoint"""
    
    if not uncertainty_quantifier:
        raise HTTPException(status_code=503, detail="Uncertainty quantifier not available")
    
    # Set number of samples for Monte Carlo dropout
    uncertainty_quantifier.n_samples = request.n_samples
    
    # Get uncertainty estimation
    uncertainty_result = uncertainty_quantifier.estimate_uncertainty(request.text)
    
    # Format token-level uncertainties
    token_uncertainties = []
    high_uncertainty_tokens = []
    
    for i, (token, uncertainty) in enumerate(zip(uncertainty_result.segmentation, uncertainty_result.token_uncertainties)):
        token_info = {
            'token': token,
            'position': i,
            'uncertainty': uncertainty,
            'boundary_confidence': uncertainty_result.boundary_confidence[i] if i < len(uncertainty_result.boundary_confidence) else 0.5
        }
        
        token_uncertainties.append(token_info)
        
        if uncertainty > request.threshold:
            high_uncertainty_tokens.append(token_info)
    
    return UncertaintyAnalysisResponse(
        text=request.text,
        overall_uncertainty=uncertainty_result.uncertainty_score,
        token_uncertainties=token_uncertainties,
        high_uncertainty_tokens=high_uncertainty_tokens,
        confidence=uncertainty_result.confidence,
        method=uncertainty_result.method
    )

class CompoundAnalysisRequest(BaseModel):
    text: str
    focus_token: Optional[str] = None

class CompoundAnalysisResponse(BaseModel):
    text: str
    compound_constructions: List[Dict[str, Any]]
    aspectual_patterns: List[Dict[str, Any]]
    verb_complexes: List[Dict[str, Any]]

@app.post("/analyze/compound", response_model=CompoundAnalysisResponse)
async def analyze_compound_constructions(request: CompoundAnalysisRequest):
    """Dedicated compound verb and aspectual construction analysis"""
    
    if not compound_verb_analyzer:
        raise HTTPException(status_code=503, detail="Compound verb analyzer not available")
    
    aspectual_handler = compound_verb_analyzer['aspectual_handler']
    verb_analyzer = compound_verb_analyzer['verb_analyzer']
    
    # Tokenize text first
    if not NLP_MODEL:
        raise HTTPException(status_code=503, detail="NLP model not available")
    
    doc = NLP_MODEL(request.text)
    
    compound_constructions = []
    aspectual_patterns = []
    verb_complexes = []
    
    for token in doc:
        token_text = token.text
        
        # Check if this is the focus token (if specified)
        if request.focus_token and request.focus_token not in token_text:
            continue
        
        # Analyze aspectual constructions
        if any(pattern in token_text for pattern in ['ている', 'ており', 'てある', 'ておく']):
            try:
                segmentation_decision = aspectual_handler.handle_shiteori_construction(
                    token_text, request.text
                )
                
                aspectual_patterns.append({
                    'token': token_text,
                    'type': segmentation_decision.aspectual_type.value,
                    'confidence': segmentation_decision.confidence,
                    'segments': segmentation_decision.segments,
                    'rationale': segmentation_decision.rationale,
                    'semantic_roles': segmentation_decision.semantic_roles
                })
            except Exception as e:
                print(f"Error in aspectual analysis: {e}")
        
        # Analyze complex verb constructions
        if any(pattern in token_text for pattern in ['させる', 'される', 'れる', 'らる']):
            try:
                verb_analysis = verb_analyzer.analyze_verb_complex(token_text, request.text)
                
                verb_complexes.append({
                    'token': token_text,
                    'base_verb': verb_analysis.base_verb,
                    'conjugation_type': verb_analysis.conjugation_type,
                    'auxiliaries': verb_analysis.auxiliaries,
                    'confidence': verb_analysis.confidence,
                    'morphophonology_valid': verb_analysis.morphophonology_valid
                })
            except Exception as e:
                print(f"Error in verb analysis: {e}")
        
        # Add to general compound constructions if any analysis was performed
        if any(pattern in token_text for pattern in ['ている', 'ており', 'させる', 'される']):
            compound_constructions.append({
                'token': token_text,
                'position': token.i,
                'has_aspectual': any(p in token_text for p in ['ている', 'ており']),
                'has_voice': any(p in token_text for p in ['させる', 'される']),
                'complexity_score': len([p for p in ['て', 'さ', 'れ'] if p in token_text]) / 3.0
            })
    
    return CompoundAnalysisResponse(
        text=request.text,
        compound_constructions=compound_constructions,
        aspectual_patterns=aspectual_patterns,
        verb_complexes=verb_complexes
    )

@app.post("/debug")
def debug_segmentation(request: AnalyzeRequest):
    """Debug endpoint to compare segmentation approaches."""
    if NLP_MODEL is None:
        raise RuntimeError("The GiNZA NLP model is not available.")

    doc = NLP_MODEL(request.text)
    
    # Get different segmentation results
    original_spans = list(ginza.bunsetu_spans(doc))
    enhanced_spans = segmenter.segment_enhanced(doc)
    
    debug_info = {
        "input_text": request.text,
        "original_ginza_segmentation": [],
        "enhanced_segmentation": [],
        "segmentation_improvements": [],
        "compound_expressions_found": [],
        "problematic_splits_fixed": []
    }
    
    # Original segmentation
    for span in original_spans:
        debug_info["original_ginza_segmentation"].append({
            "text": span.text,
            "tokens": [{"text": t.text, "pos": t.pos_, "lemma": t.lemma_} for t in span]
        })
    
    # Enhanced segmentation
    for token_group in enhanced_spans:
        if token_group:
            combined_text = ''.join([t.text for t in token_group])
            debug_info["enhanced_segmentation"].append({
                "text": combined_text,
                "token_count": len(token_group),
                "tokens": [{"text": t.text, "pos": t.pos_, "lemma": t.lemma_} for t in token_group],
                "is_compound": combined_text in COMPOUND_EXPRESSIONS,
                "compound_type": analyze_compound_expression(combined_text)[0] if combined_text in COMPOUND_EXPRESSIONS else None
            })
            
            # Track compound expressions found
            if combined_text in COMPOUND_EXPRESSIONS:
                debug_info["compound_expressions_found"].append({
                    "expression": combined_text,
                    "type": analyze_compound_expression(combined_text)[0],
                    "features": analyze_compound_expression(combined_text)[1]
                })
    
    # Compare and find improvements
    original_texts = [span.text for span in original_spans]
    enhanced_texts = [''.join([t.text for t in group]) for group in enhanced_spans if group]
    
    if original_texts != enhanced_texts:
        debug_info["segmentation_improvements"].append({
            "description": "Segmentation was improved by the enhanced algorithm",
            "original_segments": original_texts,
            "enhanced_segments": enhanced_texts,
            "improvement_count": len([expr for expr in enhanced_texts if expr in COMPOUND_EXPRESSIONS])
        })
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)