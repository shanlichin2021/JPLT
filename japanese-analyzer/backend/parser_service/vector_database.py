# backend/parser_service/vector_database.py
"""
Vector Database Manager for Japanese Dictionary Integration
Handles vectorization of existing dictionary and semantic search
"""

import asyncio
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import time
import os

from embedding_service import embedding_service, SimilarityResult

logger = logging.getLogger(__name__)

@dataclass
class DictionaryEntry:
    """Dictionary entry for vectorization"""
    word: str
    reading: str
    definitions: List[str]
    pos: List[str]
    frequency: Optional[int] = None
    jlpt_level: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VectorDatabaseManager:
    """
    Manages the vector database integration with existing dictionary
    
    Features:
    - Dictionary vectorization
    - Semantic search capabilities
    - Batch processing for performance
    - Progress tracking for large datasets
    """
    
    def __init__(self, dictionary_db_path: Optional[str] = None):
        # Use absolute path resolution for dictionary database
        if dictionary_db_path is None:
            # Default: look for dictionary.sqlite in parent directory of parser_service
            current_dir = Path(__file__).parent
            default_path = current_dir.parent / "dictionary.sqlite"
            self.dictionary_db_path = str(default_path)
        else:
            # Convert to absolute path if relative path provided
            self.dictionary_db_path = str(Path(dictionary_db_path).resolve())
        self.vectorization_progress = {
            'total_entries': 0,
            'processed_entries': 0,
            'start_time': None,
            'last_update': None,
            'status': 'not_started'
        }
    
    async def vectorize_dictionary(self, batch_size: int = 100, max_entries: Optional[int] = None):
        """
        Vectorize the existing dictionary database
        
        Args:
            batch_size: Number of entries to process in each batch
            max_entries: Maximum number of entries to process (for testing)
        """
        logger.info("Starting dictionary vectorization process")
        
        try:
            # Check if embedding service is ready
            if not embedding_service.model or not embedding_service.collection:
                raise RuntimeError("Embedding service not initialized")
            
            # Get dictionary entries
            entries = await self._load_dictionary_entries(max_entries)
            
            self.vectorization_progress.update({
                'total_entries': len(entries),
                'processed_entries': 0,
                'start_time': datetime.now(),
                'status': 'processing'
            })
            
            logger.info(f"Processing {len(entries)} dictionary entries in batches of {batch_size}")
            
            # Process in batches
            for i in range(0, len(entries), batch_size):
                batch = entries[i:i + batch_size]
                await self._process_dictionary_batch(batch)
                
                # Update progress
                self.vectorization_progress['processed_entries'] = min(i + batch_size, len(entries))
                self.vectorization_progress['last_update'] = datetime.now()
                
                # Log progress
                progress_pct = (self.vectorization_progress['processed_entries'] / len(entries)) * 100
                logger.info(f"Vectorization progress: {progress_pct:.1f}% ({self.vectorization_progress['processed_entries']}/{len(entries)})")
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            self.vectorization_progress['status'] = 'completed'
            logger.info("Dictionary vectorization completed successfully")
            
        except Exception as e:
            self.vectorization_progress['status'] = 'error'
            logger.error(f"Dictionary vectorization failed: {e}")
            raise
    
    async def _load_dictionary_entries(self, max_entries: Optional[int] = None) -> List[DictionaryEntry]:
        """Load dictionary entries from SQLite database"""
        entries = []
        
        try:
            # Connect to dictionary database
            conn = sqlite3.connect(self.dictionary_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query to get dictionary entries with their senses
            query = """
            SELECT DISTINCT
                e.kanji_elements,
                e.reading_elements,
                s.glosses,
                s.parts_of_speech,
                e.ent_seq
            FROM entries e
            LEFT JOIN senses s ON e.ent_seq = s.ent_seq
            WHERE s.glosses IS NOT NULL
            """
            
            if max_entries:
                query += f" LIMIT {max_entries}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            logger.info(f"Loaded {len(rows)} dictionary entries from database")
            
            # Process rows into DictionaryEntry objects
            for row in rows:
                try:
                    # Parse JSON fields
                    kanji_elements = json.loads(row['kanji_elements']) if row['kanji_elements'] else []
                    reading_elements = json.loads(row['reading_elements']) if row['reading_elements'] else []
                    glosses = json.loads(row['glosses']) if row['glosses'] else []
                    pos = json.loads(row['parts_of_speech']) if row['parts_of_speech'] else []
                    
                    # Extract primary word and reading
                    word = kanji_elements[0] if kanji_elements else (reading_elements[0] if reading_elements else "")
                    reading = reading_elements[0] if reading_elements else word
                    
                    # Skip entries without valid word
                    if not word or not glosses:
                        continue
                    
                    # Create entry
                    entry = DictionaryEntry(
                        word=word,
                        reading=reading,
                        definitions=glosses,
                        pos=pos,
                        metadata={
                            'ent_seq': row['ent_seq'],
                            'kanji_variants': kanji_elements,
                            'reading_variants': reading_elements,
                            'source': 'jmdict'
                        }
                    )
                    
                    entries.append(entry)
                    
                except (json.JSONDecodeError, IndexError, KeyError) as e:
                    logger.warning(f"Failed to parse dictionary row {row['ent_seq']}: {e}")
                    continue
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to load dictionary entries: {e}")
            raise
        
        return entries
    
    async def _process_dictionary_batch(self, entries: List[DictionaryEntry]):
        """Process a batch of dictionary entries"""
        try:
            # Prepare texts and metadata for vectorization
            texts = []
            metadatas = []
            doc_ids = []
            
            for entry in entries:
                # Create searchable text combining word, reading, and definitions
                searchable_text = f"{entry.word} {entry.reading} {' '.join(entry.definitions[:3])}"
                
                # Prepare metadata
                metadata = {
                    'word': entry.word,
                    'reading': entry.reading,
                    'definitions': entry.definitions,
                    'pos': entry.pos,
                    'type': 'dictionary_entry',
                    'source': 'jmdict',
                    'searchable_text': searchable_text
                }
                
                # Add optional fields
                if entry.frequency:
                    metadata['frequency'] = entry.frequency
                if entry.jlpt_level:
                    metadata['jlpt_level'] = entry.jlpt_level
                if entry.metadata:
                    metadata.update(entry.metadata)
                
                texts.append(searchable_text)
                metadatas.append(metadata)
                doc_ids.append(f"dict_{entry.metadata.get('ent_seq', len(doc_ids))}")
            
            # Add to vector database
            await embedding_service.add_documents_batch(texts, metadatas, doc_ids)
            
        except Exception as e:
            logger.error(f"Failed to process dictionary batch: {e}")
            raise
    
    async def semantic_word_search(self, 
                                  query: str, 
                                  top_k: int = 10, 
                                  pos_filter: Optional[List[str]] = None,
                                  similarity_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Perform semantic search for dictionary words
        
        Args:
            query: Search query in Japanese
            top_k: Number of results to return
            pos_filter: Filter by parts of speech
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of dictionary matches with similarity scores
        """
        try:
            # Prepare filter conditions
            where_conditions = {'type': 'dictionary_entry'}
            if pos_filter:
                # Note: Chroma DB filtering might require more complex logic for list fields
                pass
            
            # Perform semantic search
            results = await embedding_service.find_similar(
                query=query,
                top_k=top_k,
                where=where_conditions,
                threshold=similarity_threshold
            )
            
            # Format results for API response
            formatted_results = []
            for result in results:
                formatted_result = {
                    'word': result.metadata.get('word', ''),
                    'reading': result.metadata.get('reading', ''),
                    'definitions': result.metadata.get('definitions', []),
                    'pos': result.metadata.get('pos', []),
                    'similarity': result.similarity,
                    'confidence': result.similarity,
                    'source': 'semantic_search',
                    'metadata': {
                        'search_score': result.similarity,
                        'distance': result.distance,
                        'ent_seq': result.metadata.get('ent_seq')
                    }
                }
                
                # Add optional fields if available
                if 'frequency' in result.metadata:
                    formatted_result['frequency'] = result.metadata['frequency']
                if 'jlpt_level' in result.metadata:
                    formatted_result['jlpt_level'] = result.metadata['jlpt_level']
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic word search failed: {e}")
            raise
    
    async def find_related_words(self, 
                                word: str, 
                                top_k: int = 5, 
                                exclude_exact: bool = True) -> List[Dict[str, Any]]:
        """
        Find words related to the given word
        
        Args:
            word: Input word
            top_k: Number of related words to return
            exclude_exact: Whether to exclude exact matches
            
        Returns:
            List of related words with similarity scores
        """
        try:
            # Search for semantically similar words
            results = await self.semantic_word_search(
                query=word,
                top_k=top_k + (2 if exclude_exact else 0),  # Get extra in case we need to filter
                similarity_threshold=0.3
            )
            
            # Filter out exact matches if requested
            if exclude_exact:
                results = [r for r in results if r['word'] != word and r['reading'] != word]
            
            # Return top_k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Find related words failed: {e}")
            raise
    
    async def get_vectorization_status(self) -> Dict[str, Any]:
        """Get the current status of dictionary vectorization"""
        status = dict(self.vectorization_progress)
        
        # Calculate additional metrics
        if status['start_time'] and status['processed_entries'] > 0:
            elapsed = (datetime.now() - status['start_time']).total_seconds()
            rate = status['processed_entries'] / elapsed if elapsed > 0 else 0
            
            if status['total_entries'] > status['processed_entries'] and rate > 0:
                remaining = status['total_entries'] - status['processed_entries']
                eta_seconds = remaining / rate
                status['eta_seconds'] = eta_seconds
                status['processing_rate'] = rate
        
        # Add embedding service stats
        if embedding_service.collection:
            try:
                collection_stats = await embedding_service.get_collection_stats()
                status['collection_stats'] = {
                    'total_embeddings': collection_stats.total_embeddings,
                    'database_size_mb': collection_stats.database_size_mb,
                    'embedding_dimension': collection_stats.embedding_dimension
                }
            except Exception as e:
                logger.warning(f"Failed to get collection stats: {e}")
        
        return status

# Global vector database manager instance
vector_db_manager = VectorDatabaseManager()