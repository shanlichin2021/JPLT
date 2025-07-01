#!/usr/bin/env python3
# simple_ocr_server.py - Lightweight OCR service for testing
from fastapi import FastAPI, UploadFile, File, HTTPException
import logging
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple OCR Service", version="1.0.0")

# Mock OCR that returns sample Japanese text
def mock_ocr(image_data):
    """Mock OCR function that returns sample Japanese text"""
    # Return different sample texts based on image size for variety
    sample_texts = [
        "こんにちは、世界！",
        "日本語のテキストを解析します。",
        "これはOCRテストのサンプルです。",
        "漢字、ひらがな、カタカナが含まれています。",
        "OCRサービスが正常に動作しています。"
    ]
    
    # Use image size to pick different sample texts
    size_factor = len(image_data) % len(sample_texts)
    return sample_texts[size_factor]

@app.get("/")
def read_root():
    return {
        "message": "Simple OCR service is running", 
        "version": "1.0.0",
        "status": "healthy",
        "note": "This is a mock OCR service for testing purposes"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "Simple OCR", 
        "port": 8000,
        "version": "1.0.0"
    }

@app.post("/ocr")
async def process_image(file: UploadFile = File(...)):
    """
    Receives an image file and returns mock Japanese text.
    This is a simplified version for testing without heavy ML dependencies.
    """
    logger.info(f"Processing image: {file.filename}")
    
    try:
        # Read the uploaded file
        image_bytes = await file.read()
        
        if not image_bytes:
            logger.error("Received an empty file")
            raise HTTPException(status_code=400, detail="The uploaded file is empty")
        
        # Validate it's actually an image file
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate mock OCR result
        extracted_text = mock_ocr(image_bytes)
        
        logger.info(f"Mock OCR completed. Generated text: {extracted_text}")
        
        return {
            "text": extracted_text,
            "confidence": 0.95,
            "processing_time_ms": 150,
            "image_size_bytes": len(image_bytes),
            "filename": file.filename,
            "mock": True,
            "note": "This is mock OCR data for testing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Simple OCR Service on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")