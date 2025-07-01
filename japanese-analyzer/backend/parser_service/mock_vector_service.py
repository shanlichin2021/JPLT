# mock_vector_service.py
"""
Mock Vector Service for Testing Semantic Search
Provides a simplified interface for testing semantic search functionality
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import sqlite3
import random
from pathlib import Path

@dataclass
class MockSearchResult:
    word: str
    reading: str
    definitions: List[str]
    pos: List[str]
    similarity: float
    confidence: float
    source: str

class MockVectorService:
    """Mock vector service for testing semantic search"""
    
    def __init__(self, db_path: str = "../dictionary.sqlite"):
        self.db_path = db_path
        self.db = None
        self.mock_embeddings = {}  # Simple in-memory "embeddings"
        
    async def initialize(self):
        """Initialize the mock service"""
        try:
            self.db = sqlite3.connect(self.db_path, check_same_thread=False)
            print("✅ Mock vector service initialized with dictionary database")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize mock vector service: {e}")
            return False
    
    async def semantic_search(self, query: str, top_k: int = 10, similarity_threshold: float = 0.5) -> List[MockSearchResult]:
        """Mock semantic search using fuzzy matching"""
        if not self.db:
            return []
        
        try:
            # Simulate embedding-based search with fuzzy matching
            results = []
            
            # Direct exact match
            exact_results = await self._exact_search(query)
            for result in exact_results[:2]:  # Take first 2 exact matches
                results.append(MockSearchResult(
                    word=result['word'],
                    reading=result['reading'],
                    definitions=result['definitions'],
                    pos=result['pos'],
                    similarity=1.0,
                    confidence=1.0,
                    source='exact_match'
                ))
            
            # Fuzzy matches (simulate semantic similarity)
            fuzzy_results = await self._fuzzy_search(query)
            for i, result in enumerate(fuzzy_results[:top_k-len(results)]):
                # Simulate decreasing similarity scores
                similarity = max(0.3, 0.9 - (i * 0.1) + random.uniform(-0.1, 0.1))
                if similarity >= similarity_threshold:
                    results.append(MockSearchResult(
                        word=result['word'],
                        reading=result['reading'], 
                        definitions=result['definitions'],
                        pos=result['pos'],
                        similarity=similarity,
                        confidence=similarity * 0.8,
                        source='semantic_match'
                    ))
            
            # Sort by similarity
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Error in mock semantic search: {e}")
            return []
    
    async def find_related_words(self, word: str, top_k: int = 5) -> List[MockSearchResult]:
        """Find related words using mock similarity"""
        if not self.db:
            return []
        
        try:
            # Get base word definition to understand its type
            base_results = await self._exact_search(word)
            if not base_results:
                return []
            
            base_word = base_results[0]
            base_pos = base_word['pos'][0] if base_word['pos'] else 'noun'
            
            # Find words with similar POS or containing similar characters
            related = []
            
            # Character-based similarity (simplified)
            if len(word) > 1:
                for char in word:
                    char_results = await self._character_search(char, exclude=word)
                    related.extend(char_results[:2])
            
            # POS-based similarity
            pos_results = await self._pos_search(base_pos, exclude=word)
            related.extend(pos_results[:3])
            
            # Remove duplicates and create results
            seen_words = set()
            results = []
            for result in related:
                if result['word'] not in seen_words and len(results) < top_k:
                    seen_words.add(result['word'])
                    similarity = random.uniform(0.4, 0.8)
                    results.append(MockSearchResult(
                        word=result['word'],
                        reading=result['reading'],
                        definitions=result['definitions'],
                        pos=result['pos'],
                        similarity=similarity,
                        confidence=similarity * 0.9,
                        source='related_word'
                    ))
            
            return results
            
        except Exception as e:
            print(f"Error finding related words: {e}")
            return []
    
    async def _exact_search(self, query: str) -> List[Dict]:
        """Exact dictionary search"""
        cursor = self.db.cursor()
        
        # Search in both kanji and reading with simplified query
        cursor.execute("""
            SELECT DISTINCT 
                k.entry_id,
                k.value as kanji_spelling,
                r.value as reading,
                s.pos as pos,
                s.gloss as definitions
            FROM kanji k
            JOIN reading r ON r.entry_id = k.entry_id  
            JOIN sense s ON s.entry_id = k.entry_id
            WHERE k.value = ? OR r.value = ?
            LIMIT 5
        """, (query, query))
        
        results = []
        for row in cursor.fetchall():
            word = row[1] or row[2] or query
            reading = row[2] or word
            pos = row[3] or 'noun'
            definitions_raw = row[4] or '["No definition available"]'
            
            # Parse JSON definitions safely
            try:
                import json
                definitions = json.loads(definitions_raw) if definitions_raw.startswith('[') else [definitions_raw]
            except:
                definitions = [definitions_raw]
            
            results.append({
                'word': word,
                'reading': reading,
                'pos': [pos] if pos else ['noun'],
                'definitions': definitions[:3]
            })
        
        return results
    
    async def _fuzzy_search(self, query: str) -> List[Dict]:
        """Fuzzy dictionary search"""
        cursor = self.db.cursor()
        
        # Use LIKE patterns for fuzzy matching - simplified version
        cursor.execute("""
            SELECT DISTINCT 
                k.entry_id,
                k.value as word,
                r.value as reading,
                s.pos as pos,
                s.gloss as definitions
            FROM kanji k
            LEFT JOIN reading r ON r.entry_id = k.entry_id
            LEFT JOIN sense s ON s.entry_id = k.entry_id
            WHERE k.value LIKE ? OR k.value LIKE ? OR r.value LIKE ? OR r.value LIKE ?
            ORDER BY 
                CASE 
                    WHEN k.value LIKE ? THEN 1
                    WHEN r.value LIKE ? THEN 2
                    ELSE 3
                END
            LIMIT 15
        """, (f"{query}%", f"%{query}%", f"{query}%", f"%{query}%", f"{query}%", f"{query}%"))
        
        results = []
        for row in cursor.fetchall():
            word = row[1] or query
            reading = row[2] or word
            pos = row[3] or 'noun'
            definitions_raw = row[4] or '["No definition available"]'
            
            # Parse JSON definitions safely
            try:
                import json
                definitions = json.loads(definitions_raw) if definitions_raw.startswith('[') else [definitions_raw]
            except:
                definitions = [definitions_raw]
            
            results.append({
                'word': word,
                'reading': reading,
                'pos': [pos] if pos else ['noun'],
                'definitions': definitions[:3]
            })
        
        return results
    
    async def _character_search(self, char: str, exclude: str = None) -> List[Dict]:
        """Search for words containing a specific character"""
        cursor = self.db.cursor()
        
        exclude_clause = "AND k.value != ?" if exclude else ""
        params = [f"%{char}%", f"%{char}%"]
        if exclude:
            params.extend([exclude, exclude])
        
        cursor.execute(f"""
            SELECT DISTINCT 
                e.entry_id,
                COALESCE(k.value, r.value) as word,
                r.value as reading,
                GROUP_CONCAT(s.pos) as pos_list,
                GROUP_CONCAT(json_extract(s.gloss, '$[0]')) as definitions
            FROM entries e
            LEFT JOIN kanji k ON k.entry_id = e.entry_id
            LEFT JOIN reading r ON r.entry_id = e.entry_id
            JOIN sense s ON s.entry_id = e.entry_id
            WHERE (k.value LIKE ? OR r.value LIKE ?)
            {exclude_clause}
            GROUP BY e.entry_id
            LIMIT 10
        """, params)
        
        results = []
        for row in cursor.fetchall():
            word = row[1] or char
            reading = row[2] or word
            pos_list = row[3].split(',') if row[3] else ['noun']
            definitions = row[4].split(',') if row[4] else ['No definition available']
            
            results.append({
                'word': word,
                'reading': reading,
                'pos': pos_list[:3],
                'definitions': definitions[:3]
            })
        
        return results
    
    async def _pos_search(self, pos: str, exclude: str = None) -> List[Dict]:
        """Search for words with similar part of speech"""
        cursor = self.db.cursor()
        
        exclude_clause = "AND k.value != ? AND r.value != ?" if exclude else ""
        params = [f"%{pos}%"]
        if exclude:
            params.extend([exclude, exclude])
        
        cursor.execute(f"""
            SELECT DISTINCT 
                e.entry_id,
                COALESCE(k.value, r.value) as word,
                r.value as reading,
                GROUP_CONCAT(s.pos) as pos_list,
                GROUP_CONCAT(json_extract(s.gloss, '$[0]')) as definitions
            FROM entries e
            LEFT JOIN kanji k ON k.entry_id = e.entry_id
            LEFT JOIN reading r ON r.entry_id = e.entry_id
            JOIN sense s ON s.entry_id = e.entry_id
            WHERE s.pos LIKE ?
            {exclude_clause}
            GROUP BY e.entry_id
            ORDER BY RANDOM()
            LIMIT 8
        """, params)
        
        results = []
        for row in cursor.fetchall():
            word = row[1] or 'unknown'
            reading = row[2] or word
            pos_list = row[3].split(',') if row[3] else ['noun']
            definitions = row[4].split(',') if row[4] else ['No definition available']
            
            results.append({
                'word': word,
                'reading': reading,
                'pos': pos_list[:3],
                'definitions': definitions[:3]
            })
        
        return results

# Global instance
mock_vector_service = MockVectorService()

async def initialize_mock_service():
    """Initialize the mock vector service"""
    return await mock_vector_service.initialize()