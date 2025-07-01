# stacked_consensus.py - Advanced Stacked Generalization for Japanese NLP Consensus
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score
import pickle
import json
from pathlib import Path

@dataclass
class TokenizerResult:
    """Result from a single tokenizer"""
    tokenizer_name: str
    tokens: List[str]
    boundaries: List[int]
    confidence_scores: List[float]
    pos_tags: List[str]
    features: Dict[str, Any]
    processing_time: float

@dataclass
class ConsensusResult:
    """Final consensus result with meta-learning predictions"""
    tokens: List[str]
    boundaries: List[int]
    confidence: float
    uncertainty: float
    contributing_models: Dict[str, float]
    meta_features: Dict[str, float]
    individual_predictions: Dict[str, TokenizerResult]
    consensus_method: str

@dataclass
class TrainingExample:
    """Training example for meta-learner"""
    text: str
    base_predictions: Dict[str, TokenizerResult]
    ground_truth_tokens: List[str]
    ground_truth_boundaries: List[int]
    text_features: Dict[str, float]

class MetaFeatureExtractor:
    """Extract meta-features for stacked generalization"""
    
    def __init__(self):
        self.feature_extractors = {
            'agreement': self._extract_agreement_features,
            'confidence': self._extract_confidence_features,
            'text_characteristics': self._extract_text_features,
            'linguistic': self._extract_linguistic_features,
            'diversity': self._extract_diversity_features
        }
    
    def extract_meta_features(self, base_predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract comprehensive meta-features from base model predictions"""
        
        meta_features = {}
        
        # Extract features from each category
        for category, extractor in self.feature_extractors.items():
            try:
                features = extractor(base_predictions, text)
                for key, value in features.items():
                    meta_features[f"{category}_{key}"] = float(value)
            except Exception as e:
                print(f"Error extracting {category} features: {e}")
                continue
        
        return meta_features
    
    def _extract_agreement_features(self, predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract features related to model agreement"""
        
        if len(predictions) < 2:
            return {'pairwise_agreement': 0.0, 'boundary_consensus': 0.0}
        
        features = {}
        
        # Pairwise agreement calculation
        agreements = []
        tokenizer_names = list(predictions.keys())
        
        for i in range(len(tokenizer_names)):
            for j in range(i + 1, len(tokenizer_names)):
                name1, name2 = tokenizer_names[i], tokenizer_names[j]
                agreement = self._calculate_pairwise_agreement(
                    predictions[name1], predictions[name2]
                )
                agreements.append(agreement)
        
        features['pairwise_agreement'] = np.mean(agreements) if agreements else 0.0
        features['agreement_std'] = np.std(agreements) if agreements else 0.0
        
        # Boundary consensus
        all_boundaries = set()
        boundary_votes = {}
        
        for result in predictions.values():
            all_boundaries.update(result.boundaries)
            for boundary in result.boundaries:
                boundary_votes[boundary] = boundary_votes.get(boundary, 0) + 1
        
        if all_boundaries:
            consensus_boundaries = [b for b, votes in boundary_votes.items() 
                                  if votes > len(predictions) // 2]
            features['boundary_consensus'] = len(consensus_boundaries) / len(all_boundaries)
        else:
            features['boundary_consensus'] = 0.0
        
        # Token-level agreement
        token_agreements = []
        max_tokens = max(len(result.tokens) for result in predictions.values())
        
        for i in range(max_tokens):
            tokens_at_position = []
            for result in predictions.values():
                if i < len(result.tokens):
                    tokens_at_position.append(result.tokens[i])
            
            if tokens_at_position:
                most_common = max(set(tokens_at_position), key=tokens_at_position.count)
                agreement = tokens_at_position.count(most_common) / len(tokens_at_position)
                token_agreements.append(agreement)
        
        features['token_agreement_mean'] = np.mean(token_agreements) if token_agreements else 0.0
        features['token_agreement_std'] = np.std(token_agreements) if token_agreements else 0.0
        
        return features
    
    def _calculate_pairwise_agreement(self, result1: TokenizerResult, result2: TokenizerResult) -> float:
        """Calculate agreement between two tokenizer results"""
        
        # Boundary-based agreement
        boundaries1 = set(result1.boundaries)
        boundaries2 = set(result2.boundaries)
        
        intersection = len(boundaries1 & boundaries2)
        union = len(boundaries1 | boundaries2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_confidence_features(self, predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract confidence-related features"""
        
        features = {}
        
        # Individual model confidences
        all_confidences = []
        for name, result in predictions.items():
            if result.confidence_scores:
                model_confidence = np.mean(result.confidence_scores)
                all_confidences.append(model_confidence)
                features[f'{name}_confidence'] = model_confidence
        
        if all_confidences:
            features['confidence_mean'] = np.mean(all_confidences)
            features['confidence_std'] = np.std(all_confidences)
            features['confidence_min'] = np.min(all_confidences)
            features['confidence_max'] = np.max(all_confidences)
        else:
            features.update({
                'confidence_mean': 0.5,
                'confidence_std': 0.0,
                'confidence_min': 0.5,
                'confidence_max': 0.5
            })
        
        return features
    
    def _extract_text_features(self, predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract text characteristics features"""
        
        features = {}
        
        # Basic text statistics
        features['text_length'] = len(text)
        features['char_variety'] = len(set(text))
        features['avg_char_frequency'] = len(text) / max(len(set(text)), 1)
        
        # Japanese script analysis
        hiragana_count = sum(1 for c in text if '\u3040' <= c <= '\u309F')
        katakana_count = sum(1 for c in text if '\u30A0' <= c <= '\u30FF')
        kanji_count = sum(1 for c in text if '\u4E00' <= c <= '\u9FAF')
        latin_count = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        
        total_chars = len(text)
        if total_chars > 0:
            features['hiragana_ratio'] = hiragana_count / total_chars
            features['katakana_ratio'] = katakana_count / total_chars
            features['kanji_ratio'] = kanji_count / total_chars
            features['latin_ratio'] = latin_count / total_chars
        else:
            features.update({
                'hiragana_ratio': 0.0,
                'katakana_ratio': 0.0,
                'kanji_ratio': 0.0,
                'latin_ratio': 0.0
            })
        
        # Script mixing
        script_types = sum([
            hiragana_count > 0,
            katakana_count > 0,
            kanji_count > 0,
            latin_count > 0
        ])
        features['script_mixing'] = script_types / 4.0
        
        return features
    
    def _extract_linguistic_features(self, predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract linguistic pattern features"""
        
        features = {}
        
        # Average token lengths across models
        token_lengths = []
        for result in predictions.values():
            if result.tokens:
                lengths = [len(token) for token in result.tokens]
                token_lengths.extend(lengths)
        
        if token_lengths:
            features['avg_token_length'] = np.mean(token_lengths)
            features['token_length_std'] = np.std(token_lengths)
            features['max_token_length'] = np.max(token_lengths)
            features['min_token_length'] = np.min(token_lengths)
        else:
            features.update({
                'avg_token_length': 1.0,
                'token_length_std': 0.0,
                'max_token_length': 1.0,
                'min_token_length': 1.0
            })
        
        # Token count statistics
        token_counts = [len(result.tokens) for result in predictions.values()]
        if token_counts:
            features['avg_token_count'] = np.mean(token_counts)
            features['token_count_std'] = np.std(token_counts)
        else:
            features['avg_token_count'] = 1.0
            features['token_count_std'] = 0.0
        
        # POS tag diversity (if available)
        all_pos_tags = set()
        for result in predictions.values():
            if result.pos_tags:
                all_pos_tags.update(result.pos_tags)
        
        features['pos_diversity'] = len(all_pos_tags)
        
        return features
    
    def _extract_diversity_features(self, predictions: Dict[str, TokenizerResult], text: str) -> Dict[str, float]:
        """Extract features related to prediction diversity"""
        
        features = {}
        
        # Segmentation diversity
        unique_segmentations = set()
        for result in predictions.values():
            segmentation_tuple = tuple(result.tokens)
            unique_segmentations.add(segmentation_tuple)
        
        features['segmentation_diversity'] = len(unique_segmentations) / max(len(predictions), 1)
        
        # Boundary position variance
        all_boundary_positions = []
        for result in predictions.values():
            all_boundary_positions.extend(result.boundaries)
        
        if len(all_boundary_positions) > 1:
            features['boundary_position_variance'] = np.var(all_boundary_positions)
        else:
            features['boundary_position_variance'] = 0.0
        
        # Processing time features
        processing_times = [result.processing_time for result in predictions.values()]
        if processing_times:
            features['avg_processing_time'] = np.mean(processing_times)
            features['processing_time_std'] = np.std(processing_times)
        else:
            features['avg_processing_time'] = 0.0
            features['processing_time_std'] = 0.0
        
        return features

class StackedGeneralizationConsensus:
    """Advanced stacked generalization for Japanese tokenizer consensus"""
    
    def __init__(self, model_config: Optional[Dict] = None):
        self.model_config = model_config or {
            'primary': RandomForestRegressor(n_estimators=100, random_state=42),
            'secondary': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'tertiary': ElasticNet(alpha=0.1, random_state=42)
        }
        
        self.meta_learners = {}
        self.feature_extractor = MetaFeatureExtractor()
        self.is_trained = False
        self.feature_names = []
        self.model_weights = {}
        
    def train_meta_learners(self, training_examples: List[TrainingExample]) -> Dict[str, float]:
        """Train meta-learners on training data"""
        
        if not training_examples:
            raise ValueError("No training examples provided")
        
        print(f"Training meta-learners on {len(training_examples)} examples...")
        
        # Extract features and targets
        X, y = self._prepare_training_data(training_examples)
        
        if len(X) == 0:
            raise ValueError("No valid training features extracted")
        
        # Train each meta-learner
        training_scores = {}
        
        for name, model in self.model_config.items():
            print(f"Training {name} meta-learner...")
            
            try:
                # Cross-validation for model evaluation
                cv_scores = cross_val_score(model, X, y, cv=min(5, len(X)), 
                                          scoring='neg_mean_squared_error')
                training_scores[name] = -np.mean(cv_scores)
                
                # Train on full dataset
                model.fit(X, y)
                self.meta_learners[name] = model
                
                print(f"{name} CV RMSE: {training_scores[name]:.4f}")
                
            except Exception as e:
                print(f"Error training {name}: {e}")
                continue
        
        if not self.meta_learners:
            raise RuntimeError("No meta-learners successfully trained")
        
        self.is_trained = True
        self._calculate_model_weights(training_scores)
        
        return training_scores
    
    def _prepare_training_data(self, training_examples: List[TrainingExample]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for meta-learners"""
        
        X_list = []
        y_list = []
        
        for example in training_examples:
            try:
                # Extract meta-features
                meta_features = self.feature_extractor.extract_meta_features(
                    example.base_predictions, example.text
                )
                
                # Calculate target (quality score)
                target_score = self._calculate_quality_score(
                    example.base_predictions,
                    example.ground_truth_tokens,
                    example.ground_truth_boundaries
                )
                
                if meta_features and not np.isnan(target_score):
                    # Store feature names on first iteration
                    if not self.feature_names:
                        self.feature_names = sorted(meta_features.keys())
                    
                    # Create feature vector
                    feature_vector = [meta_features.get(name, 0.0) for name in self.feature_names]
                    X_list.append(feature_vector)
                    y_list.append(target_score)
                    
            except Exception as e:
                print(f"Error processing training example: {e}")
                continue
        
        return np.array(X_list), np.array(y_list)
    
    def _calculate_quality_score(self, predictions: Dict[str, TokenizerResult], 
                               ground_truth_tokens: List[str],
                               ground_truth_boundaries: List[int]) -> float:
        """Calculate quality score for predictions vs ground truth"""
        
        # Calculate consensus from predictions
        consensus_tokens = self._simple_voting_consensus(predictions)
        
        # Token-level F1 score
        token_f1 = self._calculate_token_f1(consensus_tokens, ground_truth_tokens)
        
        # Boundary-level F1 score
        consensus_boundaries = self._extract_consensus_boundaries(predictions)
        boundary_f1 = self._calculate_boundary_f1(consensus_boundaries, ground_truth_boundaries)
        
        # Combined quality score
        quality_score = 0.6 * token_f1 + 0.4 * boundary_f1
        
        return quality_score
    
    def _simple_voting_consensus(self, predictions: Dict[str, TokenizerResult]) -> List[str]:
        """Simple voting-based consensus for baseline"""
        
        if not predictions:
            return []
        
        # Find most common segmentation
        segmentation_votes = {}
        for result in predictions.values():
            segmentation_key = tuple(result.tokens)
            segmentation_votes[segmentation_key] = segmentation_votes.get(segmentation_key, 0) + 1
        
        if segmentation_votes:
            most_common = max(segmentation_votes.keys(), key=lambda x: segmentation_votes[x])
            return list(most_common)
        
        # Fallback to first result
        return list(predictions.values())[0].tokens
    
    def _extract_consensus_boundaries(self, predictions: Dict[str, TokenizerResult]) -> List[int]:
        """Extract consensus boundaries from predictions"""
        
        boundary_votes = {}
        for result in predictions.values():
            for boundary in result.boundaries:
                boundary_votes[boundary] = boundary_votes.get(boundary, 0) + 1
        
        # Majority vote threshold
        threshold = len(predictions) // 2
        consensus_boundaries = [b for b, votes in boundary_votes.items() if votes > threshold]
        
        return sorted(consensus_boundaries)
    
    def _calculate_token_f1(self, predicted: List[str], ground_truth: List[str]) -> float:
        """Calculate F1 score for token sequences"""
        
        if not predicted and not ground_truth:
            return 1.0
        if not predicted or not ground_truth:
            return 0.0
        
        # Convert to sets for comparison
        pred_set = set(predicted)
        gt_set = set(ground_truth)
        
        intersection = len(pred_set & gt_set)
        precision = intersection / len(pred_set) if pred_set else 0.0
        recall = intersection / len(gt_set) if gt_set else 0.0
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * precision * recall / (precision + recall)
    
    def _calculate_boundary_f1(self, predicted: List[int], ground_truth: List[int]) -> float:
        """Calculate F1 score for boundary positions"""
        
        if not predicted and not ground_truth:
            return 1.0
        if not predicted or not ground_truth:
            return 0.0
        
        pred_set = set(predicted)
        gt_set = set(ground_truth)
        
        intersection = len(pred_set & gt_set)
        precision = intersection / len(pred_set) if pred_set else 0.0
        recall = intersection / len(gt_set) if gt_set else 0.0
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * precision * recall / (precision + recall)
    
    def _calculate_model_weights(self, training_scores: Dict[str, float]):
        """Calculate weights for model ensemble based on performance"""
        
        if not training_scores:
            self.model_weights = {}
            return
        
        # Convert RMSE to weights (lower RMSE = higher weight)
        max_score = max(training_scores.values())
        
        weights = {}
        for name, score in training_scores.items():
            # Inverse relationship: lower error = higher weight
            weights[name] = (max_score - score + 0.1) / (max_score + 0.1)
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            self.model_weights = {name: weight / total_weight for name, weight in weights.items()}
        else:
            # Equal weights fallback
            self.model_weights = {name: 1.0 / len(weights) for name in weights.keys()}
    
    def generate_consensus(self, base_predictions: Dict[str, TokenizerResult], text: str) -> ConsensusResult:
        """Generate consensus using trained meta-learners"""
        
        if not self.is_trained:
            print("Warning: Meta-learners not trained, using simple voting consensus")
            return self._fallback_consensus(base_predictions, text)
        
        try:
            # Extract meta-features
            meta_features = self.feature_extractor.extract_meta_features(base_predictions, text)
            
            if not meta_features:
                return self._fallback_consensus(base_predictions, text)
            
            # Prepare feature vector
            feature_vector = np.array([[meta_features.get(name, 0.0) for name in self.feature_names]])
            
            # Get predictions from meta-learners
            meta_predictions = {}
            for name, model in self.meta_learners.items():
                try:
                    prediction = model.predict(feature_vector)[0]
                    meta_predictions[name] = prediction
                except Exception as e:
                    print(f"Error with meta-learner {name}: {e}")
                    continue
            
            if not meta_predictions:
                return self._fallback_consensus(base_predictions, text)
            
            # Weighted ensemble of meta-learner predictions
            weighted_prediction = sum(
                pred * self.model_weights.get(name, 1.0 / len(meta_predictions))
                for name, pred in meta_predictions.items()
            )
            
            # Use weighted prediction to guide consensus generation
            consensus_tokens, consensus_boundaries = self._generate_weighted_consensus(
                base_predictions, weighted_prediction
            )
            
            # Calculate final confidence and uncertainty
            confidence = max(0.0, min(1.0, weighted_prediction))
            uncertainty = 1.0 - confidence
            
            return ConsensusResult(
                tokens=consensus_tokens,
                boundaries=consensus_boundaries,
                confidence=confidence,
                uncertainty=uncertainty,
                contributing_models=self.model_weights.copy(),
                meta_features=meta_features,
                individual_predictions=base_predictions,
                consensus_method="stacked_generalization"
            )
            
        except Exception as e:
            print(f"Error in consensus generation: {e}")
            return self._fallback_consensus(base_predictions, text)
    
    def _generate_weighted_consensus(self, predictions: Dict[str, TokenizerResult], 
                                   meta_prediction: float) -> Tuple[List[str], List[int]]:
        """Generate consensus using meta-learner guidance"""
        
        # Use meta-prediction to weight individual tokenizer results
        if meta_prediction > 0.8:
            # High confidence: prefer most confident individual model
            best_model = max(predictions.items(), 
                           key=lambda x: np.mean(x[1].confidence_scores) if x[1].confidence_scores else 0.5)
            return best_model[1].tokens, best_model[1].boundaries
        
        elif meta_prediction < 0.3:
            # Low confidence: use conservative majority voting
            return self._conservative_consensus(predictions)
        
        else:
            # Medium confidence: use standard voting with confidence weighting
            return self._confidence_weighted_consensus(predictions)
    
    def _conservative_consensus(self, predictions: Dict[str, TokenizerResult]) -> Tuple[List[str], List[int]]:
        """Conservative consensus that prefers agreement"""
        
        # Find boundaries agreed upon by majority
        boundary_votes = {}
        for result in predictions.values():
            for boundary in result.boundaries:
                boundary_votes[boundary] = boundary_votes.get(boundary, 0) + 1
        
        # Require super-majority for boundary inclusion
        threshold = len(predictions) * 0.6  # 60% agreement
        consensus_boundaries = sorted([b for b, votes in boundary_votes.items() if votes >= threshold])
        
        # Generate tokens from consensus boundaries
        if len(consensus_boundaries) < 2:
            # Fallback to single token
            return [predictions[list(predictions.keys())[0]].tokens[0] if predictions else ""], [0, 1]
        
        # Extract text and generate tokens
        full_text = "".join(list(predictions.values())[0].tokens)
        consensus_tokens = []
        
        for i in range(len(consensus_boundaries) - 1):
            start = consensus_boundaries[i]
            end = consensus_boundaries[i + 1]
            if start < len(full_text) and end <= len(full_text):
                token = full_text[start:end]
                if token:
                    consensus_tokens.append(token)
        
        return consensus_tokens, consensus_boundaries
    
    def _confidence_weighted_consensus(self, predictions: Dict[str, TokenizerResult]) -> Tuple[List[str], List[int]]:
        """Confidence-weighted consensus generation"""
        
        # Weight each model's contribution by its confidence
        weighted_boundaries = {}
        
        for name, result in predictions.items():
            model_confidence = np.mean(result.confidence_scores) if result.confidence_scores else 0.5
            
            for boundary in result.boundaries:
                if boundary not in weighted_boundaries:
                    weighted_boundaries[boundary] = 0.0
                weighted_boundaries[boundary] += model_confidence
        
        # Select boundaries with highest weighted votes
        total_confidence = sum(np.mean(r.confidence_scores) if r.confidence_scores else 0.5 
                             for r in predictions.values())
        threshold = total_confidence * 0.5  # 50% of total confidence
        
        consensus_boundaries = sorted([b for b, weight in weighted_boundaries.items() 
                                     if weight >= threshold])
        
        # Generate tokens
        if not consensus_boundaries:
            return self._fallback_consensus(predictions, "")[0:2]
        
        full_text = "".join(list(predictions.values())[0].tokens)
        consensus_tokens = []
        
        for i in range(len(consensus_boundaries) - 1):
            start = consensus_boundaries[i]
            end = consensus_boundaries[i + 1]
            if start < len(full_text) and end <= len(full_text):
                token = full_text[start:end]
                if token:
                    consensus_tokens.append(token)
        
        return consensus_tokens, consensus_boundaries
    
    def _fallback_consensus(self, predictions: Dict[str, TokenizerResult], text: str) -> ConsensusResult:
        """Fallback consensus using simple voting"""
        
        if not predictions:
            return ConsensusResult(
                tokens=[text] if text else [],
                boundaries=[0, len(text)] if text else [],
                confidence=0.1,
                uncertainty=0.9,
                contributing_models={},
                meta_features={},
                individual_predictions={},
                consensus_method="fallback_voting"
            )
        
        # Simple majority voting
        consensus_tokens = self._simple_voting_consensus(predictions)
        consensus_boundaries = self._extract_consensus_boundaries(predictions)
        
        return ConsensusResult(
            tokens=consensus_tokens,
            boundaries=consensus_boundaries,
            confidence=0.5,
            uncertainty=0.5,
            contributing_models={name: 1.0/len(predictions) for name in predictions.keys()},
            meta_features={},
            individual_predictions=predictions,
            consensus_method="fallback_voting"
        )
    
    def save_models(self, save_path: str):
        """Save trained meta-learners to disk"""
        
        save_dir = Path(save_path)
        save_dir.mkdir(exist_ok=True)
        
        # Save meta-learners
        for name, model in self.meta_learners.items():
            model_path = save_dir / f"{name}_meta_learner.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'model_weights': self.model_weights,
            'is_trained': self.is_trained
        }
        
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Models saved to {save_path}")
    
    def load_models(self, load_path: str):
        """Load trained meta-learners from disk"""
        
        load_dir = Path(load_path)
        if not load_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {load_path}")
        
        # Load metadata
        metadata_path = load_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.feature_names = metadata['feature_names']
            self.model_weights = metadata['model_weights']
            self.is_trained = metadata['is_trained']
        
        # Load meta-learners
        self.meta_learners = {}
        for name in self.model_config.keys():
            model_path = load_dir / f"{name}_meta_learner.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    self.meta_learners[name] = pickle.load(f)
        
        if self.meta_learners:
            print(f"Loaded {len(self.meta_learners)} meta-learners from {load_path}")
        else:
            raise RuntimeError("No meta-learners found to load")