#!/usr/bin/env python3
# backend/parser_service/install_vector_deps.py
"""
Installation script for vector database dependencies
Handles the setup of Chroma DB and embedding models
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"🔧 {description}")
    logger.info(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    logger.info("🐍 Checking Python version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8+ is required for vector database features")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install vector database dependencies"""
    logger.info("📦 Installing vector database dependencies")
    
    # Install from requirements.txt
    success = run_command(
        "pip install -r requirements.txt",
        "Installing dependencies from requirements.txt"
    )
    
    if not success:
        logger.error("❌ Failed to install dependencies")
        return False
    
    return True

def download_models():
    """Download required embedding models"""
    logger.info("🤖 Downloading Japanese embedding models")
    
    # Try to download the Japanese BERT model
    try:
        logger.info("Downloading Japanese BERT model (this may take a few minutes)...")
        
        import sentence_transformers
        model = sentence_transformers.SentenceTransformer('cl-tohoku/bert-base-japanese-whole-word-masking')
        logger.info("✅ Japanese BERT model downloaded successfully")
        
        # Test the model
        test_embedding = model.encode("これはテストです")
        logger.info(f"✅ Model test successful. Embedding dimension: {len(test_embedding)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download embedding model: {e}")
        return False

def setup_chroma_db():
    """Initialize Chroma DB"""
    logger.info("🗄️ Setting up Chroma DB")
    
    try:
        import chromadb
        
        # Create Chroma DB directory
        db_path = Path("./chroma_db")
        db_path.mkdir(exist_ok=True)
        
        # Initialize client
        client = chromadb.PersistentClient(path=str(db_path))
        
        # Create test collection
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"description": "Test collection for setup verification"}
        )
        
        logger.info("✅ Chroma DB setup successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Chroma DB setup failed: {e}")
        return False

def test_vector_services():
    """Test vector services functionality"""
    logger.info("🧪 Testing vector services")
    
    try:
        # Test embedding service
        logger.info("Testing embedding service...")
        
        # Import our services
        sys.path.append('.')
        from embedding_service import JapaneseEmbeddingService
        
        # Initialize service
        service = JapaneseEmbeddingService()
        
        # Test in a simple way
        logger.info("✅ Vector services import successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Vector services test failed: {e}")
        return False

def main():
    """Main installation process"""
    logger.info("🚀 Starting Vector Database Installation")
    logger.info("=" * 50)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Download Models", download_models),
        ("Setup Chroma DB", setup_chroma_db),
        ("Test Vector Services", test_vector_services),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        logger.info(f"\n📋 Step: {step_name}")
        logger.info("-" * 30)
        
        success = step_function()
        if not success:
            failed_steps.append(step_name)
    
    logger.info("\n" + "=" * 50)
    logger.info("🏁 Installation Summary")
    
    if not failed_steps:
        logger.info("🎉 Vector database installation completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Start the parser service: uvicorn parser:app --host 0.0.0.0 --port 8002")
        logger.info("2. Run vectorization: POST to /vector/vectorize")
        logger.info("3. Test semantic search: POST to /vector/search")
        return True
    else:
        logger.error("❌ Installation failed for the following steps:")
        for step in failed_steps:
            logger.error(f"  - {step}")
        logger.error("\nPlease check the error messages above and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)