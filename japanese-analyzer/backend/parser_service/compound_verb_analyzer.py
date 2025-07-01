# compound_verb_analyzer.py - Specialized Compound Verb Analysis for Japanese
import re
import spacy
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AspectualType(Enum):
    CONTINUOUS_FORMAL = "continuous_formal"
    CONTINUOUS_CASUAL = "continuous_casual"
    RESULTATIVE = "resultative"
    EXPERIENTIAL = "experiential"
    ITERATIVE = "iterative"
    LEXICALIZED = "lexicalized"
    COMPOSITIONAL = "compositional"
    AMBIGUOUS = "ambiguous"

@dataclass
class SegmentationDecision:
    """Decision for how to segment a compound verb construction"""
    segments: List[str]
    labels: List[str]
    rationale: str
    confidence: float
    aspectual_type: AspectualType
    semantic_roles: List[str]

@dataclass
class VerbAnalysis:
    """Complete analysis of a verb complex"""
    original: str
    base_verb: str
    conjugation_type: str
    auxiliaries: List[str]
    segmentation: SegmentationDecision
    morphophonology_valid: bool
    confidence: float

@dataclass
class CompoundAnalysis:
    """Analysis of compound word formation"""
    original: str
    segmentation: List[str]
    formation_pattern: str
    productivity_score: float
    semantic_coherence: float
    confidence: float

class AspectualConstructionHandler:
    """Specialized handler for Japanese aspectual constructions like しており"""
    
    def __init__(self):
        self.aspectual_patterns = {
            'continuous': ['ている', 'ておる', 'とる', 'でいる'],
            'resultative': ['てある', 'ておく', 'とく', 'でおく'],
            'experiential': ['たことがある', 'だことがある'],
            'iterative': ['ては', 'では', 'たり', 'だり'],
            'formal_continuous': ['ております', 'でおります', 'ており', 'でおり']
        }
        
        self.lexicalized_patterns = {
            # Common lexicalized aspectual constructions
            'している': 'lexicalized_continuous',
            'である': 'lexicalized_copula',
            'における': 'lexicalized_locative',
            'について': 'lexicalized_topic',
            'において': 'lexicalized_locative_formal',
            'に関して': 'lexicalized_relation'
        }
        
        self.formal_register_markers = [
            'ております', 'でおります', 'ており', 'でおり',
            'であります', 'でございます'
        ]
        
    def handle_shiteori_construction(self, text_segment: str, context: str = "") -> SegmentationDecision:
        """Specialized handling for しており and similar constructions"""
        
        # Clean and normalize input
        normalized_segment = self._normalize_segment(text_segment)
        
        # Identify the aspectual construction type
        construction_type = self._identify_aspectual_type(normalized_segment, context)
        
        # Apply type-specific segmentation strategy
        if construction_type == AspectualType.CONTINUOUS_FORMAL:
            return self._segment_as_aspectual_unit(normalized_segment)
        elif construction_type == AspectualType.LEXICALIZED:
            return self._segment_as_lexical_unit(normalized_segment)
        elif construction_type == AspectualType.COMPOSITIONAL:
            return self._segment_compositionally(normalized_segment)
        else:
            return self._segment_with_uncertainty(normalized_segment, construction_type)
    
    def _normalize_segment(self, segment: str) -> str:
        """Normalize text segment for processing"""
        # Remove extra whitespace and normalize characters
        normalized = re.sub(r'\s+', '', segment)
        return normalized
    
    def _identify_aspectual_type(self, segment: str, context: str) -> AspectualType:
        """Determine the specific type of aspectual construction"""
        
        # Check for lexicalized patterns first
        if self._is_lexicalized(segment):
            return AspectualType.LEXICALIZED
        
        # Check for formal register markers
        if self._is_formal_register(segment):
            if any(pattern in segment for pattern in ['ており', 'でおり', 'ております']):
                return AspectualType.CONTINUOUS_FORMAL
        
        # Check for casual continuous forms
        if any(pattern in segment for pattern in ['ている', 'でいる']):
            return AspectualType.CONTINUOUS_CASUAL
        
        # Check for resultative patterns
        if any(pattern in segment for pattern in ['てある', 'ておく', 'とく']):
            return AspectualType.RESULTATIVE
        
        # Check for experiential patterns
        if any(pattern in segment for pattern in ['たことがある', 'だことがある']):
            return AspectualType.EXPERIENTIAL
        
        # Check for iterative patterns
        if any(pattern in segment for pattern in ['ては', 'では', 'たり']):
            return AspectualType.ITERATIVE
        
        # Analyze context for compositional vs. non-compositional usage
        if self._is_compositional(segment, context):
            return AspectualType.COMPOSITIONAL
        
        return AspectualType.AMBIGUOUS
    
    def _is_lexicalized(self, segment: str) -> bool:
        """Check if the construction is lexicalized"""
        return any(pattern in segment for pattern in self.lexicalized_patterns.keys())
    
    def _is_formal_register(self, segment: str) -> bool:
        """Check for formal register markers"""
        return any(marker in segment for marker in self.formal_register_markers)
    
    def _is_compositional(self, segment: str, context: str) -> bool:
        """Determine if construction should be analyzed compositionally"""
        
        # Check for transparency indicators
        transparency_indicators = [
            'まさに',  # exactly
            'ちょうど',  # just/exactly
            'まだ',  # still
            '今',  # now
            'ずっと'  # continuously
        ]
        
        return any(indicator in context for indicator in transparency_indicators)
    
    def _segment_as_aspectual_unit(self, segment: str) -> SegmentationDecision:
        """Segment while preserving aspectual semantic unity"""
        
        # Pattern matching for different aspectual constructions
        if 'ており' in segment:
            # Find the verb stem
            match = re.match(r'(.+?)ており', segment)
            if match:
                verb_stem = match.group(1)
                return SegmentationDecision(
                    segments=[verb_stem, 'ており'],
                    labels=['VERB_STEM', 'ASPECTUAL_AUXILIARY'],
                    rationale='Preserving formal continuous aspectual meaning',
                    confidence=0.9,
                    aspectual_type=AspectualType.CONTINUOUS_FORMAL,
                    semantic_roles=['PROCESS', 'CONTINUATIVE_ASPECT']
                )
        
        if 'している' in segment:
            match = re.match(r'(.+?)している', segment)
            if match:
                verb_stem = match.group(1)
                return SegmentationDecision(
                    segments=[verb_stem, 'している'],
                    labels=['VERB_STEM', 'ASPECTUAL_AUXILIARY'],
                    rationale='Preserving continuous aspectual meaning',
                    confidence=0.85,
                    aspectual_type=AspectualType.CONTINUOUS_CASUAL,
                    semantic_roles=['PROCESS', 'CONTINUATIVE_ASPECT']
                )
        
        return self._fallback_segmentation(segment)
    
    def _segment_as_lexical_unit(self, segment: str) -> SegmentationDecision:
        """Segment as single lexical unit"""
        
        return SegmentationDecision(
            segments=[segment],
            labels=['LEXICALIZED_UNIT'],
            rationale='Treating as single lexicalized construction',
            confidence=0.95,
            aspectual_type=AspectualType.LEXICALIZED,
            semantic_roles=['LEXICAL_UNIT']
        )
    
    def _segment_compositionally(self, segment: str) -> SegmentationDecision:
        """Apply compositional analysis"""
        
        # More fine-grained compositional segmentation
        segments = []
        labels = []
        
        # Pattern for て-form + auxiliary
        te_form_pattern = r'(.+?)(て|で)(いる|おる|ある|おく)'
        match = re.match(te_form_pattern, segment)
        
        if match:
            verb_stem = match.group(1)
            connector = match.group(2)
            auxiliary = match.group(3)
            
            segments = [verb_stem, connector, auxiliary]
            labels = ['VERB_STEM', 'CONNECTOR', 'AUXILIARY_VERB']
            
            return SegmentationDecision(
                segments=segments,
                labels=labels,
                rationale='Compositional analysis of morpheme structure',
                confidence=0.8,
                aspectual_type=AspectualType.COMPOSITIONAL,
                semantic_roles=['PROCESS', 'CONNECTOR', 'ASPECT_MODIFIER']
            )
        
        return self._fallback_segmentation(segment)
    
    def _segment_with_uncertainty(self, segment: str, construction_type: AspectualType) -> SegmentationDecision:
        """Handle ambiguous cases with uncertainty marking"""
        
        # Default to aspectual unit segmentation with lower confidence
        if 'ている' in segment or 'ており' in segment:
            match = re.match(r'(.+?)(ている|ており)', segment)
            if match:
                verb_part = match.group(1)
                aspectual_part = match.group(2)
                
                return SegmentationDecision(
                    segments=[verb_part, aspectual_part],
                    labels=['VERB_STEM', 'ASPECTUAL_AUXILIARY'],
                    rationale='Uncertain aspectual construction - defaulting to unit segmentation',
                    confidence=0.6,
                    aspectual_type=construction_type,
                    semantic_roles=['PROCESS', 'UNCERTAIN_ASPECT']
                )
        
        return self._fallback_segmentation(segment)
    
    def _fallback_segmentation(self, segment: str) -> SegmentationDecision:
        """Fallback segmentation for unhandled cases"""
        
        return SegmentationDecision(
            segments=[segment],
            labels=['UNANALYZED'],
            rationale='Fallback - no specific pattern matched',
            confidence=0.3,
            aspectual_type=AspectualType.AMBIGUOUS,
            semantic_roles=['UNKNOWN']
        )

class VerbConjugationAnalyzer:
    """Advanced analyzer for Japanese verb conjugation patterns"""
    
    def __init__(self):
        self.conjugation_patterns = {
            'godan': {
                'stems': ['か', 'が', 'さ', 'た', 'な', 'ば', 'ま', 'ら', 'わ'],
                'vowel_changes': {
                    'a': ['わ', 'か', 'が', 'さ', 'た', 'な', 'ば', 'ま', 'ら'],
                    'i': ['い', 'き', 'ぎ', 'し', 'ち', 'に', 'び', 'み', 'り'],
                    'u': ['う', 'く', 'ぐ', 'す', 'つ', 'ぬ', 'ぶ', 'む', 'る'],
                    'e': ['え', 'け', 'げ', 'せ', 'て', 'ね', 'べ', 'め', 'れ'],
                    'o': ['お', 'こ', 'ご', 'そ', 'と', 'の', 'ぼ', 'も', 'ろ']
                }
            },
            'ichidan': {
                'endings': ['る'],
                'stems_end_with': ['い', 'え']
            },
            'irregular': {
                'suru': ['する', 'し', 'せ', 'さ'],
                'kuru': ['くる', 'き', 'こ'],
                'aru': ['ある', 'あり'],
                'iku': ['いく', 'いっ', 'いか']
            }
        }
        
    def analyze_verb_complex(self, verb_segment: str, context: str = "") -> VerbAnalysis:
        """Analyze complex verb constructions with multiple auxiliaries"""
        
        # Identify base verb and conjugation type
        base_verb_info = self._identify_base_verb(verb_segment)
        
        if not base_verb_info:
            return self._create_fallback_analysis(verb_segment)
        
        base_verb, verb_type = base_verb_info
        
        # Parse auxiliary chain
        auxiliaries = self._parse_auxiliary_chain(verb_segment, base_verb)
        
        # Validate morphophonological consistency
        morpho_valid = self._validate_morphophonology(base_verb, auxiliaries)
        
        # Generate segmentation decision
        segmentation = self._generate_verb_segmentation(base_verb, auxiliaries, morpho_valid)
        
        return VerbAnalysis(
            original=verb_segment,
            base_verb=base_verb,
            conjugation_type=verb_type,
            auxiliaries=auxiliaries,
            segmentation=segmentation,
            morphophonology_valid=morpho_valid,
            confidence=segmentation.confidence
        )
    
    def _identify_base_verb(self, verb_segment: str) -> Optional[Tuple[str, str]]:
        """Identify base verb and its conjugation type"""
        
        # Check for irregular verbs first
        for verb_type, verbs in self.conjugation_patterns['irregular'].items():
            for verb_form in verbs:
                if verb_segment.startswith(verb_form):
                    return verb_form, f'irregular_{verb_type}'
        
        # Check for ichidan verbs
        if verb_segment.endswith('る'):
            stem = verb_segment[:-1]
            if stem and stem[-1] in ['い', 'え']:
                return verb_segment, 'ichidan'
        
        # Check for godan verbs (more complex pattern matching needed)
        godan_endings = ['く', 'ぐ', 'す', 'つ', 'ぬ', 'ぶ', 'む', 'る', 'う']
        for ending in godan_endings:
            if verb_segment.endswith(ending):
                return verb_segment, 'godan'
        
        return None
    
    def _parse_auxiliary_chain(self, verb_segment: str, base_verb: str) -> List[str]:
        """Parse the chain of auxiliary verbs following the base verb"""
        
        if len(verb_segment) <= len(base_verb):
            return []
        
        auxiliary_part = verb_segment[len(base_verb):]
        auxiliaries = []
        
        # Common auxiliary patterns
        auxiliary_patterns = [
            'ている', 'ており', 'てある', 'ておく', 'てくる', 'ていく',
            'られる', 'される', 'せる', 'させる',
            'たい', 'たがる', 'がる'
        ]
        
        remaining = auxiliary_part
        while remaining:
            found = False
            for pattern in auxiliary_patterns:
                if remaining.startswith(pattern):
                    auxiliaries.append(pattern)
                    remaining = remaining[len(pattern):]
                    found = True
                    break
            
            if not found:
                # Add remaining as single auxiliary
                auxiliaries.append(remaining)
                break
        
        return auxiliaries
    
    def _validate_morphophonology(self, base_verb: str, auxiliaries: List[str]) -> bool:
        """Validate morphophonological consistency of verb complex"""
        
        if not auxiliaries:
            return True
        
        # Check for valid connections between verb and first auxiliary
        first_aux = auxiliaries[0]
        
        # て-form connections
        if first_aux.startswith('て') or first_aux.startswith('で'):
            return self._validate_te_form_connection(base_verb, first_aux)
        
        # Passive/causative connections
        if first_aux in ['られる', 'される', 'せる', 'させる']:
            return self._validate_voice_connection(base_verb, first_aux)
        
        return True  # Default to valid for unknown patterns
    
    def _validate_te_form_connection(self, base_verb: str, auxiliary: str) -> bool:
        """Validate て-form morphophonological connection"""
        
        # Simplified validation - check if auxiliary uses correct て/で
        if base_verb.endswith(('く', 'ぐ')):
            return auxiliary.startswith('いて') or auxiliary.startswith('いで')
        elif base_verb.endswith(('す')):
            return auxiliary.startswith('して')
        elif base_verb.endswith(('つ', 'る', 'う')):
            return auxiliary.startswith('って')
        elif base_verb.endswith(('ぬ', 'ぶ', 'む')):
            return auxiliary.startswith('んで')
        
        return True  # Default to valid
    
    def _validate_voice_connection(self, base_verb: str, auxiliary: str) -> bool:
        """Validate passive/causative morphophonological connection"""
        
        # Simplified validation for voice connections
        return True  # Implementation would check specific morpheme alternations
    
    def _generate_verb_segmentation(self, base_verb: str, auxiliaries: List[str], morpho_valid: bool) -> SegmentationDecision:
        """Generate segmentation decision for verb complex"""
        
        segments = [base_verb] + auxiliaries
        labels = ['BASE_VERB'] + ['AUXILIARY'] * len(auxiliaries)
        
        confidence = 0.9 if morpho_valid else 0.7
        rationale = 'Morphophonologically valid' if morpho_valid else 'Potential morphophonological inconsistency'
        
        return SegmentationDecision(
            segments=segments,
            labels=labels,
            rationale=rationale,
            confidence=confidence,
            aspectual_type=AspectualType.COMPOSITIONAL,
            semantic_roles=['MAIN_PROCESS'] + ['MODIFIER'] * len(auxiliaries)
        )
    
    def _create_fallback_analysis(self, verb_segment: str) -> VerbAnalysis:
        """Create fallback analysis for unrecognized verbs"""
        
        fallback_segmentation = SegmentationDecision(
            segments=[verb_segment],
            labels=['UNANALYZED_VERB'],
            rationale='Could not identify verb structure',
            confidence=0.3,
            aspectual_type=AspectualType.AMBIGUOUS,
            semantic_roles=['UNKNOWN_VERB']
        )
        
        return VerbAnalysis(
            original=verb_segment,
            base_verb=verb_segment,
            conjugation_type='unknown',
            auxiliaries=[],
            segmentation=fallback_segmentation,
            morphophonology_valid=False,
            confidence=0.3
        )

class CompoundWordAnalyzer:
    """Analyzer for Japanese compound word formation patterns"""
    
    def __init__(self):
        self.productive_patterns = {
            'verb_noun': {
                'patterns': ['込む', '出す', '上げる', '下げる', '入れる'],
                'descriptions': ['intensification', 'outward_motion', 'upward_motion', 'downward_motion', 'inward_motion']
            },
            'noun_noun': {
                'patterns': ['間', '中', '上', '下', '前', '後', '内', '外'],
                'descriptions': ['interval', 'middle', 'surface', 'bottom', 'front', 'back', 'inside', 'outside']
            },
            'adjective_noun': {
                'patterns': ['新', '古', '大', '小', '長', '短', '高', '低'],
                'descriptions': ['new', 'old', 'big', 'small', 'long', 'short', 'high', 'low']
            }
        }
    
    def analyze_compound_formation(self, compound: str) -> CompoundAnalysis:
        """Analyze compound word formation patterns"""
        
        # Generate potential segmentation points
        candidates = self._generate_segmentation_candidates(compound)
        
        if not candidates:
            return self._create_fallback_compound_analysis(compound)
        
        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            scores = self._score_segmentation_candidate(candidate)
            total_score = sum(scores.values()) / len(scores)
            scored_candidates.append((candidate, total_score, scores))
        
        # Select best candidate
        best_candidate, best_score, score_breakdown = max(scored_candidates, key=lambda x: x[1])
        
        return CompoundAnalysis(
            original=compound,
            segmentation=best_candidate,
            formation_pattern=self._identify_formation_pattern(best_candidate),
            productivity_score=score_breakdown.get('productivity', 0.0),
            semantic_coherence=score_breakdown.get('semantic_coherence', 0.0),
            confidence=best_score
        )
    
    def _generate_segmentation_candidates(self, compound: str) -> List[List[str]]:
        """Generate possible segmentation candidates"""
        
        candidates = []
        
        # Binary segmentation points
        for i in range(1, len(compound)):
            left = compound[:i]
            right = compound[i:]
            candidates.append([left, right])
        
        # Ternary segmentation for longer compounds
        if len(compound) > 4:
            for i in range(1, len(compound) - 1):
                for j in range(i + 1, len(compound)):
                    left = compound[:i]
                    middle = compound[i:j]
                    right = compound[j:]
                    candidates.append([left, middle, right])
        
        return candidates
    
    def _score_segmentation_candidate(self, candidate: List[str]) -> Dict[str, float]:
        """Score a segmentation candidate on multiple criteria"""
        
        scores = {
            'productivity': self._calculate_productivity_score(candidate),
            'semantic_coherence': self._calculate_semantic_coherence(candidate),
            'frequency': self._calculate_frequency_score(candidate),
            'morphological_validity': self._calculate_morphological_validity(candidate)
        }
        
        return scores
    
    def _calculate_productivity_score(self, candidate: List[str]) -> float:
        """Calculate productivity score based on known patterns"""
        
        score = 0.0
        
        for segment in candidate:
            for pattern_type, pattern_info in self.productive_patterns.items():
                if segment in pattern_info['patterns']:
                    score += 0.8  # High score for known productive morphemes
                    break
            else:
                # Check if segment could be a productive morpheme
                if len(segment) == 1 and self._is_potential_morpheme(segment):
                    score += 0.3
        
        return min(score / len(candidate), 1.0)
    
    def _calculate_semantic_coherence(self, candidate: List[str]) -> float:
        """Calculate semantic coherence of segmentation"""
        
        # Simplified coherence calculation
        # In practice, this would use semantic embeddings
        
        coherence = 0.5  # Base coherence
        
        # Boost for known semantic relationships
        if len(candidate) == 2:
            left, right = candidate
            if self._has_semantic_relationship(left, right):
                coherence += 0.3
        
        return min(coherence, 1.0)
    
    def _calculate_frequency_score(self, candidate: List[str]) -> float:
        """Calculate frequency-based score"""
        
        # Simplified frequency scoring
        # Would use actual corpus frequencies in practice
        
        total_score = 0.0
        for segment in candidate:
            if len(segment) >= 2:  # Prefer longer segments
                total_score += 0.6
            else:
                total_score += 0.2
        
        return min(total_score / len(candidate), 1.0)
    
    def _calculate_morphological_validity(self, candidate: List[str]) -> float:
        """Calculate morphological validity score"""
        
        validity = 0.5  # Base validity
        
        # Check for valid morpheme boundaries
        for segment in candidate:
            if self._is_valid_morpheme(segment):
                validity += 0.2
        
        return min(validity, 1.0)
    
    def _is_potential_morpheme(self, segment: str) -> bool:
        """Check if segment could be a morpheme"""
        return len(segment) >= 1 and segment.isalpha()
    
    def _has_semantic_relationship(self, left: str, right: str) -> bool:
        """Check for semantic relationship between segments"""
        # Simplified check - would use semantic models in practice
        return True
    
    def _is_valid_morpheme(self, segment: str) -> bool:
        """Check if segment is a valid morpheme"""
        # Simplified validation
        return len(segment) >= 1
    
    def _identify_formation_pattern(self, segmentation: List[str]) -> str:
        """Identify the compound formation pattern"""
        
        if len(segmentation) == 2:
            return "binary_compound"
        elif len(segmentation) == 3:
            return "ternary_compound"
        else:
            return "complex_compound"
    
    def _create_fallback_compound_analysis(self, compound: str) -> CompoundAnalysis:
        """Create fallback analysis for unanalyzable compounds"""
        
        return CompoundAnalysis(
            original=compound,
            segmentation=[compound],
            formation_pattern="unanalyzed",
            productivity_score=0.0,
            semantic_coherence=0.0,
            confidence=0.1
        )