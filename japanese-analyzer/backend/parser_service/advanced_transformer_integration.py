# advanced_transformer_integration.py - Integration of Advanced Japanese Transformer Models
import torch
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from transformers import (
    AutoTokenizer, AutoModel, 
    BertTokenizer, BertModel,
    pipeline
)
import asyncio
from pathlib import Path
import logging

@dataclass
class TransformerConfig:
    """Configuration for transformer model"""
    model_name: str
    max_length: int
    batch_size: int
    device: str
    dtype: torch.dtype
    trust_remote_code: bool = True

@dataclass
class TransformerResult:
    """Result from transformer-based segmentation"""
    tokens: List[str]
    boundaries: List[int]
    confidence_scores: List[float]
    attention_weights: Optional[List[List[float]]]
    embeddings: Optional[torch.Tensor]
    processing_time: float
    model_name: str

@dataclass
class BatchProcessingResult:
    """Result from batch processing"""
    results: List[TransformerResult]
    total_processing_time: float
    avg_processing_time: float
    batch_size: int

class AdvancedJapaneseTransformer:
    """Advanced Japanese transformer for text segmentation with long context support"""
    
    def __init__(self, config: TransformerConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = torch.device(config.device if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger(__name__)
        
        # Model configurations for different transformers
        self.model_configs = {
            'llm-jp-modernbert-base': {
                'max_context': 8192,
                'architecture': 'modernbert',
                'optimization': ['flash_attention', 'rotary_pos', 'gated_linear']
            },
            'llm-jp-modernbert-large': {
                'max_context': 8192,
                'architecture': 'modernbert',
                'optimization': ['flash_attention', 'rotary_pos', 'gated_linear']
            },
            'sbintuitions/modernbert-ja-130m': {
                'max_context': 4096,
                'architecture': 'modernbert',
                'optimization': ['flash_attention', 'gradient_disentangled']
            },
            'sbintuitions/modernbert-ja-310m': {
                'max_context': 4096,
                'architecture': 'modernbert',
                'optimization': ['flash_attention', 'gradient_disentangled']
            }
        }
        
    async def initialize_model(self):
        """Initialize the transformer model with optimizations"""
        
        try:
            self.logger.info(f"Loading transformer model: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=self.config.trust_remote_code,
                use_fast=True
            )
            
            # Load model with optimizations
            model_kwargs = {
                'torch_dtype': self.config.dtype,
                'device_map': 'auto' if torch.cuda.is_available() else None,
                'trust_remote_code': self.config.trust_remote_code
            }
            
            # Add model-specific optimizations
            if self.config.model_name in self.model_configs:
                model_info = self.model_configs[self.config.model_name]
                if 'flash_attention' in model_info['optimization']:
                    model_kwargs['use_flash_attention_2'] = True
            
            self.model = AutoModel.from_pretrained(
                self.config.model_name,
                **model_kwargs
            )
            
            # Apply additional optimizations
            self._apply_model_optimizations()
            
            self.model.to(self.device)
            self.model.eval()
            
            self.logger.info(f"Successfully loaded {self.config.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load model {self.config.model_name}: {e}")
            raise
    
    def _apply_model_optimizations(self):
        """Apply model-specific optimizations"""
        
        if self.model is None:
            return
        
        try:
            # Apply quantization for memory efficiency
            if hasattr(torch, 'quantization') and self.config.dtype == torch.float16:
                self.model = torch.quantization.quantize_dynamic(
                    self.model, 
                    {torch.nn.Linear}, 
                    dtype=torch.qint8
                )
                self.logger.info("Applied dynamic quantization")
            
            # Compile for additional speed improvements (PyTorch 2.0+)
            if hasattr(torch, 'compile'):
                self.model = torch.compile(self.model, mode="reduce-overhead")
                self.logger.info("Applied torch.compile optimization")
                
        except Exception as e:
            self.logger.warning(f"Some optimizations failed: {e}")
    
    async def segment_with_context(self, text: str, context_length: Optional[int] = None) -> TransformerResult:
        """Segment text using transformer with extended context"""
        
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not initialized. Call initialize_model() first.")
        
        start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        
        if start_time:
            start_time.record()
        
        # Use model-specific max context length
        max_context = context_length or self._get_max_context_length()
        
        # Tokenize with extended context
        inputs = self.tokenizer(
            text,
            max_length=min(max_context, self.config.max_length),
            truncation=True,
            return_tensors="pt",
            padding=True,
            return_attention_mask=True,
            return_offsets_mapping=True
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items() if isinstance(v, torch.Tensor)}
        
        # Process with model
        with torch.no_grad():
            outputs = self.model(**{k: v for k, v in inputs.items() if k != 'offset_mapping'})
        
        # Extract segmentation from model outputs
        segmentation_result = self._extract_segmentation_from_outputs(
            outputs, inputs, text
        )
        
        if end_time:
            end_time.record()
            torch.cuda.synchronize()
            processing_time = start_time.elapsed_time(end_time) / 1000.0  # Convert to seconds
        else:
            processing_time = 0.0
        
        return TransformerResult(
            tokens=segmentation_result['tokens'],
            boundaries=segmentation_result['boundaries'],
            confidence_scores=segmentation_result['confidence_scores'],
            attention_weights=segmentation_result.get('attention_weights'),
            embeddings=segmentation_result.get('embeddings'),
            processing_time=processing_time,
            model_name=self.config.model_name
        )
    
    def _get_max_context_length(self) -> int:
        """Get maximum context length for the current model"""
        
        if self.config.model_name in self.model_configs:
            return self.model_configs[self.config.model_name]['max_context']
        
        # Default context length
        return getattr(self.tokenizer, 'model_max_length', 512)
    
    def _extract_segmentation_from_outputs(self, outputs, inputs, original_text: str) -> Dict[str, Any]:
        """Extract segmentation information from transformer outputs"""
        
        # Get hidden states and attention
        hidden_states = outputs.last_hidden_state  # [batch_size, seq_len, hidden_size]
        attention_weights = getattr(outputs, 'attentions', None)
        
        # Use offset mapping to align with original text
        offset_mapping = inputs.get('offset_mapping')
        
        if offset_mapping is not None:
            tokens, boundaries = self._extract_tokens_from_offsets(
                offset_mapping[0], original_text
            )
        else:
            # Fallback: use tokenizer decode
            tokens, boundaries = self._extract_tokens_fallback(
                inputs['input_ids'][0], original_text
            )
        
        # Calculate confidence scores from attention patterns
        confidence_scores = self._calculate_confidence_from_attention(
            hidden_states, attention_weights, len(tokens)
        )
        
        # Extract attention weights for visualization
        processed_attention = self._process_attention_weights(attention_weights) if attention_weights else None
        
        return {
            'tokens': tokens,
            'boundaries': boundaries,
            'confidence_scores': confidence_scores,
            'attention_weights': processed_attention,
            'embeddings': hidden_states[0].cpu() if hidden_states is not None else None
        }
    
    def _extract_tokens_from_offsets(self, offset_mapping: torch.Tensor, text: str) -> Tuple[List[str], List[int]]:
        """Extract tokens using offset mapping"""
        
        tokens = []
        boundaries = [0]
        
        for start, end in offset_mapping:
            start_idx, end_idx = int(start), int(end)
            
            if start_idx < end_idx and end_idx <= len(text):
                token = text[start_idx:end_idx]
                if token.strip():  # Skip empty tokens
                    tokens.append(token)
                    boundaries.append(end_idx)
        
        return tokens, boundaries
    
    def _extract_tokens_fallback(self, input_ids: torch.Tensor, text: str) -> Tuple[List[str], List[int]]:
        """Fallback token extraction using tokenizer decode"""
        
        tokens = []
        boundaries = [0]
        current_pos = 0
        
        for token_id in input_ids:
            if token_id in [self.tokenizer.cls_token_id, self.tokenizer.sep_token_id, 
                           self.tokenizer.pad_token_id]:
                continue
            
            token = self.tokenizer.decode([token_id], skip_special_tokens=True)
            if token:
                # Find token position in original text
                token_pos = text.find(token, current_pos)
                if token_pos != -1:
                    tokens.append(token)
                    current_pos = token_pos + len(token)
                    boundaries.append(current_pos)
        
        return tokens, boundaries
    
    def _calculate_confidence_from_attention(self, hidden_states: torch.Tensor, 
                                           attention_weights: Optional[Tuple], 
                                           num_tokens: int) -> List[float]:
        """Calculate confidence scores from attention patterns"""
        
        if attention_weights is None or num_tokens == 0:
            return [0.5] * num_tokens
        
        # Average attention across layers and heads
        # attention_weights: tuple of (batch_size, num_heads, seq_len, seq_len)
        try:
            avg_attention = torch.stack(attention_weights).mean(dim=(0, 1, 2))  # Average across layers, heads, query positions
            
            # Convert to confidence scores (higher attention = higher confidence)
            confidence_scores = []
            for i in range(min(num_tokens, len(avg_attention))):
                confidence = float(torch.sigmoid(avg_attention[i]))  # Normalize to [0, 1]
                confidence_scores.append(confidence)
            
            # Pad or truncate to match num_tokens
            while len(confidence_scores) < num_tokens:
                confidence_scores.append(0.5)
            
            return confidence_scores[:num_tokens]
            
        except Exception as e:
            self.logger.warning(f"Error calculating confidence from attention: {e}")
            return [0.5] * num_tokens
    
    def _process_attention_weights(self, attention_weights: Tuple) -> List[List[float]]:
        """Process attention weights for visualization"""
        
        if not attention_weights:
            return []
        
        try:
            # Take the last layer's attention and average across heads
            last_layer_attention = attention_weights[-1]  # [batch_size, num_heads, seq_len, seq_len]
            avg_attention = last_layer_attention.mean(dim=1)[0]  # [seq_len, seq_len]
            
            # Convert to list for JSON serialization
            return avg_attention.cpu().tolist()
            
        except Exception as e:
            self.logger.warning(f"Error processing attention weights: {e}")
            return []

class DynamicBatchProcessor:
    """Dynamic batch processor for transformer models"""
    
    def __init__(self, max_batch_size: int = 32, max_wait_time: float = 0.05):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time  # seconds
        self.pending_requests = []
        self.processing_lock = asyncio.Lock()
        
    async def create_batch(self, texts: List[str]) -> List[str]:
        """Create optimal batch from input texts"""
        
        # Simple batching - group texts by similar length
        texts_with_lengths = [(text, len(text)) for text in texts]
        texts_with_lengths.sort(key=lambda x: x[1])
        
        batches = []
        current_batch = []
        
        for text, length in texts_with_lengths:
            if len(current_batch) >= self.max_batch_size:
                batches.append([t for t, _ in current_batch])
                current_batch = []
            
            current_batch.append((text, length))
        
        if current_batch:
            batches.append([t for t, _ in current_batch])
        
        return batches[0] if batches else texts  # Return first batch for now
    
    async def process_batch(self, transformer: AdvancedJapaneseTransformer, 
                          texts: List[str]) -> BatchProcessingResult:
        """Process a batch of texts efficiently"""
        
        start_time = asyncio.get_event_loop().time()
        results = []
        
        # Process texts in parallel where possible
        tasks = []
        for text in texts:
            task = transformer.segment_with_context(text)
            tasks.append(task)
        
        # Execute batch
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                self.logger.error(f"Error processing text {i}: {result}")
                # Create fallback result
                fallback_result = TransformerResult(
                    tokens=[texts[i]],
                    boundaries=[0, len(texts[i])],
                    confidence_scores=[0.1],
                    attention_weights=None,
                    embeddings=None,
                    processing_time=0.0,
                    model_name="fallback"
                )
                results.append(fallback_result)
            else:
                results.append(result)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        avg_time = total_time / len(texts) if texts else 0.0
        
        return BatchProcessingResult(
            results=results,
            total_processing_time=total_time,
            avg_processing_time=avg_time,
            batch_size=len(texts)
        )

class TransformerModelPool:
    """Pool of transformer models for load balancing"""
    
    def __init__(self, model_configs: List[TransformerConfig]):
        self.model_configs = model_configs
        self.models = {}
        self.load_balancer = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize_pool(self):
        """Initialize all models in the pool"""
        
        for config in self.model_configs:
            try:
                transformer = AdvancedJapaneseTransformer(config)
                await transformer.initialize_model()
                
                self.models[config.model_name] = transformer
                self.load_balancer[config.model_name] = 0  # Request count
                
                self.logger.info(f"Added {config.model_name} to model pool")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {config.model_name}: {e}")
                continue
        
        if not self.models:
            raise RuntimeError("No models successfully initialized in pool")
    
    def get_best_model(self, text_length: int, priority: str = "balanced") -> AdvancedJapaneseTransformer:
        """Get the best model for given text characteristics"""
        
        if not self.models:
            raise RuntimeError("No models available in pool")
        
        if priority == "speed":
            # Prefer smaller, faster models
            return self._get_fastest_model()
        elif priority == "accuracy":
            # Prefer larger, more accurate models
            return self._get_most_accurate_model()
        elif priority == "context":
            # Prefer models with longer context windows
            return self._get_longest_context_model(text_length)
        else:
            # Balanced approach
            return self._get_balanced_model(text_length)
    
    def _get_fastest_model(self) -> AdvancedJapaneseTransformer:
        """Get the fastest available model"""
        
        # Prefer smaller models (heuristic: 130m < 310m < base < large)
        model_priority = [
            'sbintuitions/modernbert-ja-130m',
            'sbintuitions/modernbert-ja-310m',
            'llm-jp-modernbert-base',
            'llm-jp-modernbert-large'
        ]
        
        for model_name in model_priority:
            if model_name in self.models:
                return self.models[model_name]
        
        # Fallback to any available model
        return list(self.models.values())[0]
    
    def _get_most_accurate_model(self) -> AdvancedJapaneseTransformer:
        """Get the most accurate available model"""
        
        # Prefer larger models
        model_priority = [
            'llm-jp-modernbert-large',
            'llm-jp-modernbert-base',
            'sbintuitions/modernbert-ja-310m',
            'sbintuitions/modernbert-ja-130m'
        ]
        
        for model_name in model_priority:
            if model_name in self.models:
                return self.models[model_name]
        
        return list(self.models.values())[0]
    
    def _get_longest_context_model(self, text_length: int) -> AdvancedJapaneseTransformer:
        """Get model with appropriate context length"""
        
        # Choose based on text length requirements
        if text_length > 4000:
            # Need long context models
            for model_name in ['llm-jp-modernbert-large', 'llm-jp-modernbert-base']:
                if model_name in self.models:
                    return self.models[model_name]
        
        # Standard context is sufficient
        return self._get_balanced_model(text_length)
    
    def _get_balanced_model(self, text_length: int) -> AdvancedJapaneseTransformer:
        """Get balanced model based on load and capabilities"""
        
        # Simple load balancing: choose least used model
        least_used_model = min(self.load_balancer.items(), key=lambda x: x[1])
        model_name = least_used_model[0]
        
        # Update load counter
        self.load_balancer[model_name] += 1
        
        return self.models[model_name]
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self.models.keys())

# Factory function for easy model creation
def create_advanced_transformer(model_name: str, 
                               device: str = "auto",
                               max_length: int = 8192,
                               batch_size: int = 16) -> AdvancedJapaneseTransformer:
    """Factory function to create advanced transformer with optimal settings"""
    
    # Determine device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Determine optimal dtype
    if device == "cuda" and torch.cuda.is_available():
        dtype = torch.float16  # Use half precision on GPU
    else:
        dtype = torch.float32  # Full precision on CPU
    
    # Adjust max_length based on model capabilities
    if model_name in ['llm-jp-modernbert-base', 'llm-jp-modernbert-large']:
        max_length = min(max_length, 8192)
    else:
        max_length = min(max_length, 4096)
    
    config = TransformerConfig(
        model_name=model_name,
        max_length=max_length,
        batch_size=batch_size,
        device=device,
        dtype=dtype,
        trust_remote_code=True
    )
    
    return AdvancedJapaneseTransformer(config)