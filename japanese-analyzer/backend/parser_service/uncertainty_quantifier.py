# uncertainty_quantifier.py - Advanced Uncertainty Quantification for Japanese NLP
import torch
import numpy as np
import math
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from dataclasses import dataclass
import spacy
from spacy.tokens import Doc

@dataclass
class UncertaintyResult:
    """Result of uncertainty quantification"""
    segmentation: List[str]
    uncertainty_score: float
    confidence: float
    token_uncertainties: List[float]
    boundary_confidence: List[float]
    method: str

@dataclass
class TokenUncertainty:
    """Uncertainty information for individual tokens"""
    token: str
    pos_uncertainty: float
    boundary_uncertainty: float
    reading_uncertainty: float
    overall_uncertainty: float

class MonteCarloDropoutUncertainty:
    """Monte Carlo Dropout for uncertainty estimation in Japanese NLP"""
    
    def __init__(self, nlp_model, n_samples: int = 50):
        self.nlp_model = nlp_model
        self.n_samples = n_samples
        self.dropout_rate = 0.1
        
    def estimate_uncertainty(self, text: str) -> UncertaintyResult:
        """Estimate segmentation uncertainty using Monte Carlo Dropout"""
        
        # Generate multiple predictions with dropout
        predictions = []
        
        for _ in range(self.n_samples):
            # Process text with stochastic forward pass
            doc = self._process_with_dropout(text)
            
            # Extract segmentation and features
            segmentation = self._extract_segmentation(doc)
            predictions.append(segmentation)
        
        # Calculate consensus and uncertainty
        consensus_segmentation = self._calculate_consensus(predictions)
        uncertainty_scores = self._calculate_uncertainty_scores(predictions)
        
        return UncertaintyResult(
            segmentation=consensus_segmentation,
            uncertainty_score=uncertainty_scores['overall'],
            confidence=1.0 - uncertainty_scores['overall'],
            token_uncertainties=uncertainty_scores['tokens'],
            boundary_confidence=uncertainty_scores['boundaries'],
            method="monte_carlo_dropout"
        )
    
    def _process_with_dropout(self, text: str) -> Doc:
        """Process text with dropout enabled during inference"""
        
        # Enable training mode for dropout during inference
        if hasattr(self.nlp_model, 'get_pipe'):
            for pipe_name in self.nlp_model.pipe_names:
                pipe = self.nlp_model.get_pipe(pipe_name)
                if hasattr(pipe, 'model') and hasattr(pipe.model, 'train'):
                    pipe.model.train()  # Enable dropout
        
        # Process with stochastic behavior
        doc = self.nlp_model(text)
        
        return doc
    
    def _extract_segmentation(self, doc: Doc) -> Dict:
        """Extract segmentation information from spaCy doc"""
        tokens = []
        
        for token in doc:
            token_data = {
                'surface': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,
                'tag': token.tag_,
                'start': token.idx,
                'end': token.idx + len(token.text),
                'reading': getattr(token._, 'reading', None) if hasattr(token, '_') else None
            }
            tokens.append(token_data)
        
        return {
            'tokens': tokens,
            'boundaries': [token['start'] for token in tokens] + [len(doc.text)]
        }
    
    def _calculate_consensus(self, predictions: List[Dict]) -> List[str]:
        """Calculate consensus segmentation from multiple predictions"""
        
        # Count boundary occurrences
        boundary_votes = defaultdict(int)
        
        for pred in predictions:
            for boundary in pred['boundaries']:
                boundary_votes[boundary] += 1
        
        # Select boundaries with majority vote
        consensus_boundaries = []
        for boundary, votes in boundary_votes.items():
            if votes > self.n_samples // 2:  # Majority threshold
                consensus_boundaries.append(boundary)
        
        consensus_boundaries = sorted(set(consensus_boundaries))
        
        # Generate consensus tokens
        if not predictions:
            return []
        
        text = predictions[0]['tokens'][0]['surface'] if predictions[0]['tokens'] else ""
        for pred in predictions:
            if pred['tokens']:
                full_text = ''.join([t['surface'] for t in pred['tokens']])
                if len(full_text) > len(text):
                    text = full_text
                break
        
        consensus_tokens = []
        for i in range(len(consensus_boundaries) - 1):
            start = consensus_boundaries[i]
            end = consensus_boundaries[i + 1]
            if start < len(text) and end <= len(text):
                token = text[start:end]
                if token.strip():
                    consensus_tokens.append(token)
        
        return consensus_tokens
    
    def _calculate_uncertainty_scores(self, predictions: List[Dict]) -> Dict[str, float]:
        """Calculate various uncertainty metrics"""
        
        if not predictions:
            return {
                'overall': 1.0,
                'tokens': [],
                'boundaries': []
            }
        
        # Boundary uncertainty (entropy-based)
        boundary_votes = defaultdict(int)
        for pred in predictions:
            for boundary in pred['boundaries']:
                boundary_votes[boundary] += 1
        
        boundary_uncertainties = []
        for boundary, votes in boundary_votes.items():
            prob = votes / self.n_samples
            entropy = -prob * math.log2(prob) - (1-prob) * math.log2(max(1-prob, 1e-10))
            boundary_uncertainties.append(entropy)
        
        # Token-level uncertainty
        token_uncertainties = self._calculate_token_uncertainties(predictions)
        
        # Overall uncertainty (average of boundary uncertainties)
        overall_uncertainty = np.mean(boundary_uncertainties) if boundary_uncertainties else 0.0
        
        return {
            'overall': min(overall_uncertainty, 1.0),
            'tokens': token_uncertainties,
            'boundaries': boundary_uncertainties
        }
    
    def _calculate_token_uncertainties(self, predictions: List[Dict]) -> List[float]:
        """Calculate uncertainty for individual tokens"""
        
        if not predictions:
            return []
        
        # Collect all unique tokens across predictions
        all_tokens = set()
        for pred in predictions:
            for token in pred['tokens']:
                all_tokens.add(token['surface'])
        
        token_uncertainties = []
        
        for token_surface in all_tokens:
            # Count POS tag variations for this token
            pos_counts = defaultdict(int)
            total_occurrences = 0
            
            for pred in predictions:
                for token in pred['tokens']:
                    if token['surface'] == token_surface:
                        pos_counts[token['pos']] += 1
                        total_occurrences += 1
            
            if total_occurrences > 0:
                # Calculate entropy of POS distribution
                entropy = 0.0
                for count in pos_counts.values():
                    prob = count / total_occurrences
                    if prob > 0:
                        entropy -= prob * math.log2(prob)
                
                token_uncertainties.append(entropy)
        
        return token_uncertainties

class EnsembleUncertainty:
    """Uncertainty estimation using ensemble of different models"""
    
    def __init__(self, models: List):
        self.models = models
        
    def estimate_ensemble_uncertainty(self, text: str) -> UncertaintyResult:
        """Estimate uncertainty using model ensemble"""
        
        predictions = []
        
        # Get predictions from all models
        for model in self.models:
            try:
                if hasattr(model, 'tokenize'):
                    # Traditional tokenizer
                    tokens = model.tokenize(text)
                    pred = self._format_tokenizer_output(tokens, text)
                else:
                    # spaCy model
                    doc = model(text)
                    pred = self._format_spacy_output(doc)
                
                predictions.append(pred)
            except Exception as e:
                print(f"Model prediction failed: {e}")
                continue
        
        if not predictions:
            return UncertaintyResult(
                segmentation=[text],
                uncertainty_score=1.0,
                confidence=0.0,
                token_uncertainties=[1.0],
                boundary_confidence=[0.0],
                method="ensemble_fallback"
            )
        
        # Calculate consensus and disagreement
        consensus = self._calculate_ensemble_consensus(predictions)
        uncertainty = self._calculate_ensemble_uncertainty(predictions)
        
        return UncertaintyResult(
            segmentation=consensus,
            uncertainty_score=uncertainty['overall'],
            confidence=1.0 - uncertainty['overall'],
            token_uncertainties=uncertainty['tokens'],
            boundary_confidence=uncertainty['boundaries'],
            method="ensemble_uncertainty"
        )
    
    def _format_tokenizer_output(self, tokens, text: str) -> Dict:
        """Format traditional tokenizer output"""
        formatted_tokens = []
        current_pos = 0
        
        for token in tokens:
            token_text = str(token)
            start_pos = text.find(token_text, current_pos)
            if start_pos != -1:
                formatted_tokens.append({
                    'surface': token_text,
                    'start': start_pos,
                    'end': start_pos + len(token_text)
                })
                current_pos = start_pos + len(token_text)
        
        boundaries = [0] + [t['end'] for t in formatted_tokens]
        
        return {
            'tokens': formatted_tokens,
            'boundaries': boundaries
        }
    
    def _format_spacy_output(self, doc: Doc) -> Dict:
        """Format spaCy output"""
        tokens = []
        
        for token in doc:
            tokens.append({
                'surface': token.text,
                'start': token.idx,
                'end': token.idx + len(token.text),
                'pos': token.pos_,
                'lemma': token.lemma_
            })
        
        boundaries = [0] + [t['end'] for t in tokens]
        
        return {
            'tokens': tokens,
            'boundaries': boundaries
        }
    
    def _calculate_ensemble_consensus(self, predictions: List[Dict]) -> List[str]:
        """Calculate consensus from ensemble predictions"""
        
        # Use voting-based consensus
        all_boundaries = set()
        for pred in predictions:
            all_boundaries.update(pred['boundaries'])
        
        # Count votes for each boundary
        boundary_votes = defaultdict(int)
        for boundary in all_boundaries:
            for pred in predictions:
                if boundary in pred['boundaries']:
                    boundary_votes[boundary] += 1
        
        # Select boundaries with majority vote
        threshold = len(predictions) // 2
        consensus_boundaries = sorted([
            boundary for boundary, votes in boundary_votes.items()
            if votes > threshold
        ])
        
        # Extract text segments
        if not predictions or not consensus_boundaries:
            return []
        
        # Get original text
        text = ""
        for pred in predictions:
            if pred['tokens']:
                candidate_text = ''.join([t['surface'] for t in pred['tokens']])
                if len(candidate_text) > len(text):
                    text = candidate_text
        
        # Generate consensus tokens
        consensus_tokens = []
        for i in range(len(consensus_boundaries) - 1):
            start = consensus_boundaries[i]
            end = consensus_boundaries[i + 1]
            if start < len(text) and end <= len(text):
                token = text[start:end]
                if token.strip():
                    consensus_tokens.append(token)
        
        return consensus_tokens
    
    def _calculate_ensemble_uncertainty(self, predictions: List[Dict]) -> Dict[str, float]:
        """Calculate uncertainty metrics for ensemble"""
        
        if not predictions:
            return {'overall': 1.0, 'tokens': [], 'boundaries': []}
        
        # Calculate boundary disagreement
        all_boundaries = set()
        for pred in predictions:
            all_boundaries.update(pred['boundaries'])
        
        boundary_disagreements = []
        for boundary in all_boundaries:
            votes = sum(1 for pred in predictions if boundary in pred['boundaries'])
            disagreement = 1.0 - (votes / len(predictions))
            boundary_disagreements.append(disagreement)
        
        # Calculate token disagreement
        token_disagreements = self._calculate_token_disagreements(predictions)
        
        overall_uncertainty = np.mean(boundary_disagreements) if boundary_disagreements else 0.0
        
        return {
            'overall': min(overall_uncertainty, 1.0),
            'tokens': token_disagreements,
            'boundaries': boundary_disagreements
        }
    
    def _calculate_token_disagreements(self, predictions: List[Dict]) -> List[float]:
        """Calculate disagreement for individual tokens"""
        
        token_agreements = []
        
        # Compare tokens across predictions
        if len(predictions) < 2:
            return [0.0] * len(predictions[0]['tokens']) if predictions else []
        
        max_tokens = max(len(pred['tokens']) for pred in predictions)
        
        for i in range(max_tokens):
            token_surfaces = []
            for pred in predictions:
                if i < len(pred['tokens']):
                    token_surfaces.append(pred['tokens'][i]['surface'])
            
            if token_surfaces:
                # Calculate disagreement as fraction of non-matching tokens
                most_common = max(set(token_surfaces), key=token_surfaces.count)
                agreement_rate = token_surfaces.count(most_common) / len(token_surfaces)
                disagreement = 1.0 - agreement_rate
                token_agreements.append(disagreement)
        
        return token_agreements

class AdaptiveUncertaintyThreshold:
    """Adaptive thresholding for uncertainty-based decisions"""
    
    def __init__(self, initial_threshold: float = 0.5):
        self.threshold = initial_threshold
        self.performance_history = []
        self.adaptation_rate = 0.1
        
    def should_request_annotation(self, uncertainty: float) -> bool:
        """Determine if annotation is needed based on uncertainty"""
        return uncertainty > self.threshold
    
    def update_from_feedback(self, uncertainty: float, was_correct: bool):
        """Update threshold based on feedback"""
        
        self.performance_history.append((uncertainty, was_correct))
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        # Adapt threshold based on performance
        if len(self.performance_history) >= 10:
            self._adapt_threshold()
    
    def _adapt_threshold(self):
        """Adapt threshold based on recent performance"""
        
        # Calculate precision at current threshold
        above_threshold = [(u, c) for u, c in self.performance_history if u > self.threshold]
        
        if above_threshold:
            precision = sum(1 for _, correct in above_threshold if not correct) / len(above_threshold)
            
            # Adjust threshold based on precision
            if precision < 0.5:  # Too many false positives
                self.threshold += self.adaptation_rate
            elif precision > 0.8:  # Too few true positives
                self.threshold -= self.adaptation_rate
            
            # Keep threshold in reasonable bounds
            self.threshold = max(0.1, min(0.9, self.threshold))