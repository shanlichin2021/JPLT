# backend/parser_service/vectorize_dictionary.py
"""
Dictionary Vectorization Script
Processes the existing 212K+ dictionary entries for semantic search
"""

import asyncio
import sys
import argparse
from pathlib import Path
import time
from datetime import datetime

from embedding_service import initialize_embedding_service, embedding_service
from vector_database import vector_db_manager

async def vectorize_dictionary_entries(batch_size=50, max_entries=None, test_mode=False):
    """
    Vectorize dictionary entries for semantic search
    
    Args:
        batch_size: Number of entries to process in each batch
        max_entries: Maximum entries to process (for testing)
        test_mode: Run in test mode with smaller dataset
    """
    try:
        print("🚀 Starting Dictionary Vectorization")
        print("=" * 50)
        
        # Initialize embedding service
        print("📦 Initializing embedding service...")
        await initialize_embedding_service()
        
        if not embedding_service.model or not embedding_service.collection:
            raise RuntimeError("Failed to initialize embedding service")
        
        print("✅ Embedding service ready")
        
        # Set parameters for test mode
        if test_mode:
            max_entries = 100
            batch_size = 10
            print(f"🧪 Test mode: Processing {max_entries} entries in batches of {batch_size}")
        else:
            print(f"🗄️ Production mode: Processing all entries in batches of {batch_size}")
            if max_entries:
                print(f"📊 Limited to {max_entries} entries")
        
        # Start vectorization
        start_time = time.time()
        
        await vector_db_manager.vectorize_dictionary(
            batch_size=batch_size,
            max_entries=max_entries
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get final stats
        stats = await vector_db_manager.get_vectorization_status()
        collection_stats = await embedding_service.get_collection_stats()
        performance_stats = embedding_service.get_performance_stats()
        
        print("\n" + "=" * 50)
        print("🎉 Vectorization Complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Processed: {stats['processed_entries']:,} entries")
        print(f"🗄️  Database size: {collection_stats.database_size_mb:.1f} MB")
        print(f"📈 Cache hit rate: {performance_stats['cache_hit_rate']:.1%}")
        
        if stats['processed_entries'] > 0:
            rate = stats['processed_entries'] / duration
            print(f"⚡ Processing rate: {rate:.1f} entries/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Vectorization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_semantic_search():
    """Test semantic search functionality"""
    try:
        print("\n🔍 Testing Semantic Search")
        print("-" * 30)
        
        test_queries = [
            "食べる",  # to eat
            "美しい",  # beautiful
            "学校",    # school
            "愛",      # love
        ]
        
        for query in test_queries:
            print(f"\n🔎 Searching for: {query}")
            
            results = await vector_db_manager.semantic_word_search(
                query=query,
                top_k=3,
                similarity_threshold=0.3
            )
            
            if results:
                print(f"  Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    similarity = result['similarity']
                    word = result['word']
                    reading = result['reading']
                    definitions = result['definitions'][:2]  # First 2 definitions
                    
                    print(f"    {i}. {word} ({reading}) - {similarity:.1%}")
                    print(f"       {'; '.join(definitions)}")
            else:
                print("  No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic search test failed: {e}")
        return False

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Vectorize Japanese dictionary for semantic search")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--max-entries", type=int, help="Maximum entries to process")
    parser.add_argument("--test", action="store_true", help="Run in test mode (100 entries)")
    parser.add_argument("--no-search-test", action="store_true", help="Skip semantic search test")
    
    args = parser.parse_args()
    
    success = True
    
    # Vectorize dictionary
    vectorization_success = await vectorize_dictionary_entries(
        batch_size=args.batch_size,
        max_entries=args.max_entries,
        test_mode=args.test
    )
    
    if not vectorization_success:
        success = False
    
    # Test semantic search unless skipped
    if vectorization_success and not args.no_search_test:
        search_success = await test_semantic_search()
        if not search_success:
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All operations completed successfully!")
        print("\nNext steps:")
        print("1. Start the enhanced parser service")
        print("2. Test semantic search via API endpoints")
        print("3. Integrate with frontend applications")
    else:
        print("❌ Some operations failed. Check logs above.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)