# backend/parser_service/vector_api.py
"""
Vector Database API Endpoints
Provides semantic search and embedding capabilities via FastAPI
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time

from embedding_service import embedding_service
from vector_database import vector_db_manager

logger = logging.getLogger(__name__)

# Create router for vector API endpoints
vector_router = APIRouter(prefix="/vector", tags=["vector"])

# Pydantic models for API requests/responses

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query in Japanese")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    pos_filter: Optional[List[str]] = Field(default=None, description="Filter by parts of speech")
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum similarity threshold")

class SemanticSearchResult(BaseModel):
    word: str
    reading: str
    definitions: List[str]
    pos: List[str]
    similarity: float
    confidence: float
    source: str
    metadata: Dict[str, Any]

class SemanticSearchResponse(BaseModel):
    results: List[SemanticSearchResult]
    query: str
    total_results: int
    search_time_ms: float

class RelatedWordsRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=100, description="Input word to find related words for")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of related words to return")
    exclude_exact: bool = Field(default=True, description="Exclude exact matches")

class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to generate embedding for")

class EmbeddingResponse(BaseModel):
    text: str
    embedding: List[float]
    dimension: int
    model_name: str

class BatchEmbeddingRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to generate embeddings for")

class BatchEmbeddingResponse(BaseModel):
    texts: List[str]
    embeddings: List[List[float]]
    dimension: int
    model_name: str
    batch_size: int

class VectorizationStatusResponse(BaseModel):
    status: str
    total_entries: int
    processed_entries: int
    progress_percentage: float
    processing_rate: Optional[float] = None
    eta_seconds: Optional[float] = None
    collection_stats: Optional[Dict[str, Any]] = None

class VectorizationRequest(BaseModel):
    batch_size: int = Field(default=100, ge=10, le=1000, description="Batch size for processing")
    max_entries: Optional[int] = Field(default=None, description="Maximum entries to process (for testing)")

# API Endpoints

@vector_router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Perform semantic search on the dictionary database
    
    Returns semantically similar words based on the query.
    """
    try:
        # Additional validation
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty or whitespace only")
        
        if request.top_k <= 0:
            raise HTTPException(status_code=400, detail="top_k must be greater than 0")
        
        if not (0.0 <= request.similarity_threshold <= 1.0):
            raise HTTPException(status_code=400, detail="similarity_threshold must be between 0.0 and 1.0")
        
        start_time = time.time()
        
        # Perform semantic search
        results = await vector_db_manager.semantic_word_search(
            query=request.query,
            top_k=request.top_k,
            pos_filter=request.pos_filter,
            similarity_threshold=request.similarity_threshold
        )
        
        search_time_ms = (time.time() - start_time) * 1000
        
        # Convert to response format
        formatted_results = [
            SemanticSearchResult(**result) for result in results
        ]
        
        return SemanticSearchResponse(
            results=formatted_results,
            query=request.query,
            total_results=len(formatted_results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@vector_router.post("/related-words", response_model=List[SemanticSearchResult])
async def find_related_words(request: RelatedWordsRequest):
    """
    Find words semantically related to the input word
    
    Returns a list of related words with similarity scores.
    """
    try:
        # Additional validation
        if not request.word.strip():
            raise HTTPException(status_code=400, detail="Word cannot be empty or whitespace only")
        
        if request.top_k <= 0:
            raise HTTPException(status_code=400, detail="top_k must be greater than 0")
        
        # Find related words
        results = await vector_db_manager.find_related_words(
            word=request.word,
            top_k=request.top_k,
            exclude_exact=request.exclude_exact
        )
        
        # Convert to response format
        formatted_results = [
            SemanticSearchResult(**result) for result in results
        ]
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Find related words failed: {e}")
        raise HTTPException(status_code=500, detail=f"Find related words failed: {str(e)}")

@vector_router.post("/embed", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """
    Generate embedding vector for a single text
    
    Returns the embedding vector and metadata.
    """
    try:
        # Additional validation
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty or whitespace only")
        
        # Generate embedding
        embedding = await embedding_service.embed_text(request.text)
        
        return EmbeddingResponse(
            text=request.text,
            embedding=embedding,
            dimension=len(embedding),
            model_name=embedding_service.model_name
        )
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@vector_router.post("/embed-batch", response_model=BatchEmbeddingResponse)
async def generate_batch_embeddings(request: BatchEmbeddingRequest):
    """
    Generate embedding vectors for multiple texts
    
    More efficient than individual requests for multiple texts.
    """
    try:
        # Validate batch size
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
        
        if not request.texts:
            raise HTTPException(status_code=400, detail="Empty text list provided")
        
        # Validate individual texts
        for i, text in enumerate(request.texts):
            if not text or not text.strip():
                raise HTTPException(status_code=400, detail=f"Text at index {i} cannot be empty or whitespace only")
        
        # Generate embeddings
        embeddings = await embedding_service.embed_batch(request.texts)
        
        # Validate embeddings were generated
        if not embeddings or len(embeddings) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")
        
        # Safely get dimension from first embedding
        dimension = len(embeddings[0]) if embeddings and len(embeddings[0]) > 0 else 0
        
        return BatchEmbeddingResponse(
            texts=request.texts,
            embeddings=embeddings,
            dimension=dimension,
            model_name=embedding_service.model_name,
            batch_size=len(request.texts)
        )
        
    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch embedding generation failed: {str(e)}")

@vector_router.get("/status", response_model=VectorizationStatusResponse)
async def get_vectorization_status():
    """
    Get the current status of dictionary vectorization
    
    Returns progress information and collection statistics.
    """
    try:
        status = await vector_db_manager.get_vectorization_status()
        
        # Calculate progress percentage
        progress_percentage = 0.0
        if status['total_entries'] > 0:
            progress_percentage = (status['processed_entries'] / status['total_entries']) * 100
        
        return VectorizationStatusResponse(
            status=status['status'],
            total_entries=status['total_entries'],
            processed_entries=status['processed_entries'],
            progress_percentage=progress_percentage,
            processing_rate=status.get('processing_rate'),
            eta_seconds=status.get('eta_seconds'),
            collection_stats=status.get('collection_stats')
        )
        
    except Exception as e:
        logger.error(f"Failed to get vectorization status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get vectorization status: {str(e)}")

@vector_router.post("/vectorize")
async def start_vectorization(request: VectorizationRequest, background_tasks: BackgroundTasks):
    """
    Start the dictionary vectorization process
    
    Runs in the background and can be monitored via /status endpoint.
    """
    try:
        # Check if already running
        status = await vector_db_manager.get_vectorization_status()
        if status['status'] == 'processing':
            raise HTTPException(status_code=400, detail="Vectorization already in progress")
        
        # Start vectorization in background
        background_tasks.add_task(
            vector_db_manager.vectorize_dictionary,
            batch_size=request.batch_size,
            max_entries=request.max_entries
        )
        
        return {
            "message": "Vectorization started",
            "batch_size": request.batch_size,
            "max_entries": request.max_entries,
            "monitor_url": "/vector/status"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start vectorization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start vectorization: {str(e)}")

@vector_router.get("/health")
async def vector_service_health():
    """
    Health check for vector services
    
    Returns the health status of embedding service and vector database.
    """
    try:
        health_status = {
            "status": "healthy",
            "embedding_service": {
                "initialized": embedding_service.model is not None,
                "model_name": embedding_service.model_name,
                "cache_size": len(embedding_service.embedding_cache)
            },
            "vector_database": {
                "initialized": embedding_service.collection is not None,
                "collection_count": embedding_service.collection.count() if embedding_service.collection else 0
            },
            "performance_stats": embedding_service.get_performance_stats()
        }
        
        # Check if services are properly initialized
        if not embedding_service.model or not embedding_service.collection:
            health_status["status"] = "degraded"
            health_status["message"] = "Some services not fully initialized"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@vector_router.get("/stats")
async def get_vector_stats():
    """
    Get detailed statistics about the vector database and embedding service
    
    Returns performance metrics and usage statistics.
    """
    try:
        stats = {
            "embedding_service": embedding_service.get_performance_stats(),
            "vector_database": await vector_db_manager.get_vectorization_status()
        }
        
        # Add collection stats if available
        if embedding_service.collection:
            collection_stats = await embedding_service.get_collection_stats()
            stats["collection"] = {
                "total_embeddings": collection_stats.total_embeddings,
                "database_size_mb": collection_stats.database_size_mb,
                "embedding_dimension": collection_stats.embedding_dimension,
                "model_name": collection_stats.model_name,
                "last_updated": collection_stats.last_updated.isoformat()
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get vector stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get vector stats: {str(e)}")