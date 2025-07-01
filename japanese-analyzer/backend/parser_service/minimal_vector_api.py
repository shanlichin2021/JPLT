# minimal_vector_api.py
"""
Minimal Vector API for Testing Semantic Search
Uses mock vector service for demonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import time

from mock_vector_service import mock_vector_service

app = FastAPI(title="Mock Vector API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    similarity_threshold: float = 0.5
    pos_filter: Optional[str] = None

class RelatedWordsRequest(BaseModel):
    word: str
    top_k: int = 5
    exclude_exact: bool = True

# Response models
class SearchResultItem(BaseModel):
    word: str
    reading: str
    definitions: List[str]
    pos: List[str]
    similarity: float
    confidence: float
    source: str

class SemanticSearchResponse(BaseModel):
    results: List[SearchResultItem]
    total_results: int
    search_time_ms: float
    query: str

@app.on_event("startup")
async def startup_event():
    """Initialize mock vector service on startup"""
    success = await mock_vector_service.initialize()
    if success:
        print("🚀 Mock Vector API started successfully")
    else:
        print("❌ Failed to start Mock Vector API")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock_vector_api", "version": "1.0.0"}

@app.post("/vector/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search using mock service"""
    start_time = time.time()
    
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Perform mock semantic search
        results = await mock_vector_service.semantic_search(
            query=request.query.strip(),
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        # Convert to response format
        search_results = [
            SearchResultItem(
                word=result.word,
                reading=result.reading,
                definitions=result.definitions,
                pos=result.pos,
                similarity=result.similarity,
                confidence=result.confidence,
                source=result.source
            )
            for result in results
        ]
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SemanticSearchResponse(
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time, 2),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/vector/related-words")
async def find_related_words(request: RelatedWordsRequest):
    """Find semantically related words"""
    try:
        if not request.word or not request.word.strip():
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        
        # Find related words using mock service
        results = await mock_vector_service.find_related_words(
            word=request.word.strip(),
            top_k=request.top_k
        )
        
        # Convert to response format
        related_words = [
            {
                "word": result.word,
                "reading": result.reading,
                "definitions": result.definitions,
                "pos": result.pos,
                "similarity": result.similarity,
                "confidence": result.confidence,
                "source": result.source
            }
            for result in results
        ]
        
        return related_words
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Related words search failed: {str(e)}")

@app.get("/vector/stats")
async def get_stats():
    """Get mock vector database statistics"""
    return {
        "service_type": "mock",
        "status": "operational",
        "total_embeddings": "212K+ (simulated)",
        "embedding_dimension": 768,
        "model": "mock-japanese-bert",
        "database_size_mb": "simulated"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)