# advanced_parser_helpers.py - Helper functions for advanced Japanese NLP analysis
import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Import required classes - prefer stacked_consensus for TokenizerResult
try:
    from stacked_consensus import TokenizerResult, ConsensusResult
    from uncertainty_quantifier import UncertaintyResult, UncertaintyInfo  
    from compound_verb_analyzer import SegmentationDecision, AspectualType
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Some advanced imports unavailable: {e}")
    # Create minimal functional classes
    from dataclasses import dataclass
    from typing import List, Dict, Any
    
    @dataclass
    class TokenizerResult:
        tokenizer_name: str = ""
        tokens: List[str] = None
        boundaries: List[int] = None
        confidence_scores: List[float] = None
        pos_tags: List[str] = None
        features: Dict[str, Any] = None
        processing_time: float = 0.0
        
        def __post_init__(self):
            if self.tokens is None: self.tokens = []
            if self.boundaries is None: self.boundaries = []
            if self.confidence_scores is None: self.confidence_scores = []
            if self.pos_tags is None: self.pos_tags = []
            if self.features is None: self.features = {}
    
    @dataclass
    class ConsensusResult:
        tokens: List[str] = None
        def __post_init__(self):
            if self.tokens is None: self.tokens = []
    
    class UncertaintyResult: pass
    class UncertaintyInfo: pass
    class SegmentationDecision: pass
    class AspectualType: pass
    IMPORTS_AVAILABLE = False


async def _get_base_model_predictions(text: str) -> Dict[str, TokenizerResult]:
    """Get predictions from multiple base models for consensus"""
    
    # Get NLP model from globals (avoiding circular import)
    import sys
    parser_module = sys.modules.get('parser')
    NLP_MODEL = getattr(parser_module, 'NLP_MODEL', None) if parser_module else None
    
    predictions = {}
    
    # Add spaCy + GiNZA prediction
    if NLP_MODEL:
        start_time = time.time()
        doc = NLP_MODEL(text)
        
        tokens = []
        boundaries = [0]
        confidence_scores = []
        pos_tags = []
        
        for token in doc:
            tokens.append(token.text)
            boundaries.append(token.idx + len(token.text))
            # Use token probability if available, otherwise default
            confidence = getattr(token, 'prob', -10.0)
            confidence_scores.append(max(0.1, min(1.0, 1.0 + confidence/10.0)))
            pos_tags.append(token.pos_)
        
        processing_time = time.time() - start_time
        
        predictions['ginza'] = TokenizerResult(
            tokenizer_name='ginza',
            tokens=tokens,
            boundaries=boundaries,
            confidence_scores=confidence_scores,
            pos_tags=pos_tags,
            features={'model_type': 'spacy_ginza'},
            processing_time=processing_time
        )
    
    # Add other tokenizers if available
    try:
        import fugashi
        start_time = time.time()
        tagger = fugashi.Tagger()
        
        tokens = []
        boundaries = [0]
        pos_tags = []
        current_pos = 0
        
        for word in tagger(text):
            surface = str(word).split('\t')[0]
            tokens.append(surface)
            current_pos += len(surface)
            boundaries.append(current_pos)
            pos_tags.append(word.pos.split(',')[0] if hasattr(word, 'pos') else 'UNKNOWN')
        
        processing_time = time.time() - start_time
        
        predictions['fugashi'] = TokenizerResult(
            tokenizer_name='fugashi',
            tokens=tokens,
            boundaries=boundaries,
            confidence_scores=[0.8] * len(tokens),  # Default confidence
            pos_tags=pos_tags,
            features={'model_type': 'mecab_fugashi'},
            processing_time=processing_time
        )
    except ImportError:
        pass
    
    # Add SudachiPy if available
    try:
        from sudachipy import tokenizer, dictionary
        
        start_time = time.time()
        tokenizer_obj = dictionary.Dictionary().create()
        mode = tokenizer.Tokenizer.SplitMode.A
        
        tokens = []
        boundaries = [0]
        pos_tags = []
        
        for m in tokenizer_obj.tokenize(text, mode):
            surface = m.surface()
            tokens.append(surface)
            boundaries.append(m.end())
            pos_tags.append(m.part_of_speech()[0])
        
        processing_time = time.time() - start_time
        
        predictions['sudachi'] = TokenizerResult(
            tokenizer_name='sudachi',
            tokens=tokens,
            boundaries=boundaries,
            confidence_scores=[0.85] * len(tokens),  # Default confidence
            pos_tags=pos_tags,
            features={'model_type': 'sudachi'},
            processing_time=processing_time
        )
    except ImportError:
        pass
    
    return predictions


async def _analyze_with_compound_specialization(consensus_result: ConsensusResult, 
                                              text: str) -> List[Dict[str, Any]]:
    """Analyze tokens with specialized compound verb handling"""
    
    # Get compound_verb_analyzer from globals (avoiding circular import)
    import sys
    parser_module = sys.modules.get('parser')
    compound_verb_analyzer = getattr(parser_module, 'compound_verb_analyzer', None) if parser_module else None
    
    enhanced_chunks = []
    
    if not compound_verb_analyzer:
        return await _basic_chunk_analysis(consensus_result, text)
    
    aspectual_handler = compound_verb_analyzer['aspectual_handler']
    verb_analyzer = compound_verb_analyzer['verb_analyzer']
    
    for i, token in enumerate(consensus_result.tokens):
        chunk_data = {
            'text': token,
            'lemma_to_lookup': token,
            'reading': token,  # Would be enhanced with actual reading
            'grammar': None,
            'context': None,
            'dependency': None,
            'compound_analysis': None
        }
        
        # Check for aspectual constructions (like しており)
        if any(pattern in token for pattern in ['ている', 'ており', 'てある', 'ておく']):
            try:
                segmentation_decision = aspectual_handler.handle_shiteori_construction(
                    token, text
                )
                
                chunk_data['compound_analysis'] = {
                    'type': segmentation_decision.aspectual_type.value,
                    'confidence': segmentation_decision.confidence,
                    'segments': segmentation_decision.segments,
                    'labels': segmentation_decision.labels,
                    'rationale': segmentation_decision.rationale,
                    'description': f"Aspectual construction: {segmentation_decision.rationale}"
                }
            except Exception as e:
                print(f"Error in compound analysis for '{token}': {e}")
        
        # Check for complex verb constructions
        elif any(pattern in token for pattern in ['させる', 'される', 'れる', 'らる']):
            try:
                verb_analysis = verb_analyzer.analyze_verb_complex(token, text)
                
                chunk_data['compound_analysis'] = {
                    'type': 'complex_verb',
                    'confidence': verb_analysis.confidence,
                    'base_verb': verb_analysis.base_verb,
                    'conjugation_type': verb_analysis.conjugation_type,
                    'auxiliaries': verb_analysis.auxiliaries,
                    'description': f"Complex verb: {verb_analysis.base_verb} + {', '.join(verb_analysis.auxiliaries)}"
                }
            except Exception as e:
                print(f"Error in verb analysis for '{token}': {e}")
        
        enhanced_chunks.append(chunk_data)
    
    return enhanced_chunks


async def _basic_chunk_analysis(consensus_result: ConsensusResult, text: str) -> List[Dict[str, Any]]:
    """Basic chunk analysis without advanced compound handling"""
    
    chunks = []
    
    for token in consensus_result.tokens:
        chunk_data = {
            'text': token,
            'lemma_to_lookup': token,
            'reading': token,
            'grammar': None,
            'context': None,
            'dependency': None
        }
        chunks.append(chunk_data)
    
    return chunks


async def _add_uncertainty_information(chunks: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """Add uncertainty information to chunks"""
    
    # Get uncertainty_quantifier from globals (avoiding circular import)
    import sys
    parser_module = sys.modules.get('parser')
    uncertainty_quantifier = getattr(parser_module, 'uncertainty_quantifier', None) if parser_module else None
    
    if not uncertainty_quantifier:
        return chunks
    
    try:
        # Get uncertainty estimation for the entire text
        uncertainty_result = uncertainty_quantifier.estimate_uncertainty(text)
        
        # Distribute uncertainty information to chunks
        for i, chunk in enumerate(chunks):
            if i < len(uncertainty_result.token_uncertainties):
                token_uncertainty = uncertainty_result.token_uncertainties[i]
                boundary_confidence = (
                    uncertainty_result.boundary_confidence[i] 
                    if i < len(uncertainty_result.boundary_confidence) 
                    else 0.5
                )
                
                chunk['uncertainty'] = UncertaintyInfo(
                    overall_uncertainty=token_uncertainty,
                    boundary_confidence=1.0 - boundary_confidence,  # Convert to confidence
                    pos_uncertainty=token_uncertainty * 0.8,  # Approximation
                    reading_uncertainty=token_uncertainty * 0.6,  # Approximation
                    consensus_method=uncertainty_result.method
                )
            else:
                # Default uncertainty for extra tokens
                chunk['uncertainty'] = UncertaintyInfo(
                    overall_uncertainty=0.5,
                    boundary_confidence=0.5,
                    pos_uncertainty=0.5,
                    reading_uncertainty=0.5,
                    consensus_method="default"
                )
    
    except Exception as e:
        print(f"Error adding uncertainty information: {e}")
        # Add default uncertainty to all chunks
        for chunk in chunks:
            chunk['uncertainty'] = UncertaintyInfo(
                overall_uncertainty=0.5,
                boundary_confidence=0.5,
                pos_uncertainty=0.5,
                reading_uncertainty=0.5,
                consensus_method="error_fallback"
            )
    
    return chunks


def _create_parse_validation(dependency_tree) -> Dict[str, Any]:
    """Create parse validation information"""
    
    if not dependency_tree:
        return {
            'is_valid': False,
            'errors': ['No dependency tree available'],
            'confidence': 0.0,
            'complexity_score': 0.0
        }
    
    # Calculate validation metrics
    errors = []
    confidence = 1.0
    
    # Check for basic validation
    if not hasattr(dependency_tree, 'nodes') or len(dependency_tree.nodes) == 0:
        errors.append('Empty dependency tree')
        confidence *= 0.5
    
    # Check for validation errors if available
    if hasattr(dependency_tree, 'validation_errors'):
        errors.extend(dependency_tree.validation_errors)
        confidence *= max(0.1, 1.0 - len(dependency_tree.validation_errors) * 0.2)
    
    # Calculate complexity score
    complexity_score = 0.5
    if hasattr(dependency_tree, 'nodes'):
        complexity_score = min(1.0, len(dependency_tree.nodes) / 20.0)
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'confidence': confidence,
        'complexity_score': complexity_score
    }


class SimpleDynamicBatchProcessor:
    """Simple dynamic batch processor for improved performance"""
    
    def __init__(self, max_batch_size: int = 16, max_wait_time: float = 0.1):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.processing = False
    
    async def process_request(self, text: str, analysis_function) -> Any:
        """Process a single request with batching"""
        
        # For now, just process immediately without batching
        # Full batching implementation would require more complex request queuing
        return await analysis_function(text)
    
    async def process_batch(self, texts: List[str], analysis_function) -> List[Any]:
        """Process a batch of texts"""
        
        results = []
        
        # Process in chunks of max_batch_size
        for i in range(0, len(texts), self.max_batch_size):
            batch = texts[i:i + self.max_batch_size]
            
            # Process batch in parallel
            tasks = [analysis_function(text) for text in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"Error in batch processing: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return results


# Global batch processor instance
batch_processor = SimpleDynamicBatchProcessor()