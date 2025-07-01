# backend/parser_service/embedding_service.py
"""
Advanced Embedding Service for Japanese Text Analysis
Provides semantic understanding through vector embeddings
"""

import chromadb
import numpy as np
import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import hashlib
from datetime import datetime
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimilarityResult:
    """Result from similarity search"""
    id: str
    text: str
    similarity: float
    metadata: Dict[str, Any]
    distance: float

@dataclass
class EmbeddingStats:
    """Statistics about the embedding database"""
    total_embeddings: int
    database_size_mb: float
    last_updated: datetime
    model_name: str
    embedding_dimension: int

class JapaneseEmbeddingService:
    """
    Advanced embedding service optimized for Japanese text analysis
    
    Features:
    - Japanese-optimized BERT model
    - Persistent vector storage with Chroma DB
    - Batch processing for performance
    - Caching for frequent queries
    - Metadata support for enhanced search
    """
    
    def __init__(self, 
                 model_name: str = "cl-tohoku/bert-base-japanese-whole-word-masking",
                 db_path: str = "./chroma_db",
                 cache_size: int = 1000):
        """
        Initialize the embedding service
        
        Args:
            model_name: Hugging Face model name for Japanese embeddings
            db_path: Path to Chroma DB storage
            cache_size: Size of embedding cache
        """
        self.model_name = model_name
        self.db_path = Path(db_path)
        self.cache_size = cache_size
        
        # Initialize components
        self.model = None
        self.chroma_client = None
        self.collection = None
        self.embedding_cache = {}
        
        # Performance tracking
        self.stats = {
            'embeddings_generated': 0,
            'cache_hits': 0,
            'searches_performed': 0,
            'documents_added': 0
        }
        
        logger.info(f"Initializing Japanese Embedding Service with model: {model_name}")
    
    async def initialize(self):
        """Initialize the embedding model and database"""
        try:
            # Initialize sentence transformer model
            logger.info("Loading Japanese BERT model...")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            
            # Initialize Chroma DB
            logger.info("Initializing Chroma DB...")
            self.chroma_client = chromadb.PersistentClient(path=str(self.db_path))
            
            # Get or create collection for Japanese text
            self.collection = self.chroma_client.get_or_create_collection(
                name="japanese_text_embeddings",
                metadata={"description": "Japanese text embeddings for semantic analysis"}
            )
            
            logger.info(f"Chroma DB initialized. Collection has {self.collection.count()} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    def _generate_text_id(self, text: str) -> str:
        """Generate a unique ID for text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input Japanese text
            
        Returns:
            List of float values representing the embedding
        """
        if not self.model:
            raise RuntimeError("Embedding service not initialized")
        
        # Check cache first
        text_hash = self._generate_text_id(text)
        if text_hash in self.embedding_cache:
            self.stats['cache_hits'] += 1
            return self.embedding_cache[text_hash]
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            embedding_list = embedding.tolist()
            
            # Cache the result
            if len(self.embedding_cache) < self.cache_size:
                self.embedding_cache[text_hash] = embedding_list
            
            self.stats['embeddings_generated'] += 1
            return embedding_list
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {text[:50]}... Error: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if not self.model:
            raise RuntimeError("Embedding service not initialized")
        
        try:
            # Check which texts are already cached
            cached_embeddings = {}
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                text_hash = self._generate_text_id(text)
                if text_hash in self.embedding_cache:
                    cached_embeddings[i] = self.embedding_cache[text_hash]
                    self.stats['cache_hits'] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts")
                new_embeddings = self.model.encode(uncached_texts, convert_to_numpy=True)
                
                # Cache new embeddings
                for i, (text_idx, text) in enumerate(zip(uncached_indices, uncached_texts)):
                    embedding_list = new_embeddings[i].tolist()
                    cached_embeddings[text_idx] = embedding_list
                    
                    # Add to cache if space available
                    if len(self.embedding_cache) < self.cache_size:
                        text_hash = self._generate_text_id(text)
                        self.embedding_cache[text_hash] = embedding_list
                
                self.stats['embeddings_generated'] += len(uncached_texts)
            
            # Reconstruct results in original order
            results = [cached_embeddings[i] for i in range(len(texts))]
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def add_document(self, 
                          text: str, 
                          metadata: Dict[str, Any], 
                          doc_id: Optional[str] = None) -> str:
        """
        Add a document to the vector database
        
        Args:
            text: Document text
            metadata: Document metadata
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        if not self.collection:
            raise RuntimeError("Vector database not initialized")
        
        try:
            # Generate document ID if not provided
            if doc_id is None:
                doc_id = self._generate_text_id(text)
            
            # Generate embedding
            embedding = await self.embed_text(text)
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            self.stats['documents_added'] += 1
            logger.debug(f"Added document {doc_id} to vector database")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document to vector database: {e}")
            raise
    
    async def add_documents_batch(self, 
                                 texts: List[str], 
                                 metadatas: List[Dict[str, Any]], 
                                 doc_ids: Optional[List[str]] = None) -> List[str]:
        """
        Add multiple documents to the vector database efficiently
        
        Args:
            texts: List of document texts
            metadatas: List of document metadata
            doc_ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        if not self.collection:
            raise RuntimeError("Vector database not initialized")
        
        if len(texts) != len(metadatas):
            raise ValueError("Number of texts and metadatas must match")
        
        try:
            # Generate document IDs if not provided
            if doc_ids is None:
                doc_ids = [self._generate_text_id(text) for text in texts]
            
            # Generate embeddings
            logger.info(f"Processing batch of {len(texts)} documents")
            embeddings = await self.embed_batch(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=doc_ids
            )
            
            self.stats['documents_added'] += len(texts)
            logger.info(f"Added {len(texts)} documents to vector database")
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents batch to vector database: {e}")
            raise
    
    async def find_similar(self, 
                          query: str, 
                          top_k: int = 10, 
                          where: Optional[Dict[str, Any]] = None,
                          threshold: float = 0.0) -> List[SimilarityResult]:
        """
        Find semantically similar documents
        
        Args:
            query: Query text
            top_k: Number of results to return
            where: Metadata filter conditions
            threshold: Minimum similarity threshold
            
        Returns:
            List of similarity results
        """
        if not self.collection:
            raise RuntimeError("Vector database not initialized")
        
        try:
            # Generate query embedding
            query_embedding = await self.embed_text(query)
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            similarity_results = []
            
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    doc_id = results['ids'][0][i]
                    document = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity score (1 - normalized distance)
                    similarity = max(0.0, 1.0 - distance)
                    
                    # Apply threshold filter
                    if similarity >= threshold:
                        similarity_results.append(SimilarityResult(
                            id=doc_id,
                            text=document,
                            similarity=similarity,
                            metadata=metadata,
                            distance=distance
                        ))
            
            self.stats['searches_performed'] += 1
            logger.debug(f"Found {len(similarity_results)} similar documents for query: {query[:50]}...")
            
            return similarity_results
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {e}")
            raise
    
    async def get_collection_stats(self) -> EmbeddingStats:
        """Get statistics about the embedding collection"""
        if not self.collection:
            raise RuntimeError("Vector database not initialized")
        
        try:
            count = self.collection.count()
            
            # Estimate database size (rough calculation)
            embedding_dim = self.model.get_sentence_embedding_dimension() if self.model else 768
            estimated_size_mb = (count * embedding_dim * 4) / (1024 * 1024)  # 4 bytes per float
            
            return EmbeddingStats(
                total_embeddings=count,
                database_size_mb=estimated_size_mb,
                last_updated=datetime.now(),
                model_name=self.model_name,
                embedding_dimension=embedding_dim
            )
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_hit_rate = 0.0
        if self.stats['embeddings_generated'] + self.stats['cache_hits'] > 0:
            cache_hit_rate = self.stats['cache_hits'] / (self.stats['embeddings_generated'] + self.stats['cache_hits'])
        
        return {
            **self.stats,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.embedding_cache),
            'cache_capacity': self.cache_size
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up embedding service")
        if self.chroma_client:
            # Chroma DB automatically persists data
            pass
        self.embedding_cache.clear()

# Global embedding service instance
embedding_service = JapaneseEmbeddingService()

# Initialization function for use in FastAPI startup
async def initialize_embedding_service():
    """Initialize the global embedding service"""
    await embedding_service.initialize()
    logger.info("Embedding service initialization complete")

# Shutdown function for use in FastAPI shutdown
async def shutdown_embedding_service():
    """Shutdown the global embedding service"""
    await embedding_service.cleanup()
    logger.info("Embedding service shutdown complete")