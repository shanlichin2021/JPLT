# ocr_service/ocr_server.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import logging
import io                  # <-- REQUIRED for in-memory operations

# Mock MangaOcr for testing - replace with real implementation when needed
class MockMangaOcr:
    def __call__(self, image):
        return "サンプルテキスト (OCRサービステスト用)"

try:
    from manga_ocr import MangaOcr
    print("✅ Using real MangaOcr")
except ImportError:
    print("⚠️ manga_ocr not found, using mock OCR for testing")
    MangaOcr = MockMangaOcr

try:
    from PIL import Image      # <-- REQUIRED to create the image object  
except ImportError:
    print("⚠️ PIL not found, OCR will be limited")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize MangaOcr (no change here)
logger.info("Initializing MangaOcr... (This may take a moment on first launch)")
mocr = MangaOcr()
logger.info("MangaOcr initialized successfully.")

@app.post("/ocr")
async def process_image(file: UploadFile = File(...)):
    """
    Receives an image file, processes it with MangaOcr,
    and returns the extracted text.
    """
    logger.info(f"Received file: {file.filename}")
    try:
        image_bytes = await file.read()
        if not image_bytes:
            logger.error("Received an empty file.")
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        # --- THE KEY FIX ---
        # MangaOcr expects a PIL.Image object, not raw bytes.
        # We convert the received bytes into that object format in memory.
        try:
            # Create an in-memory binary stream from the bytes
            image_stream = io.BytesIO(image_bytes)
            # Open the stream as a PIL.Image object
            if 'Image' in globals():
                img = Image.open(image_stream)
            else:
                # Fallback when PIL is not available
                logger.warning("PIL not available, using mock response")
                return {"text": "サンプルテキスト (PIL未利用、モックレスポンス)"}
            logger.info("Successfully loaded image into a PIL.Image object.")
        except Exception as pil_error:
            logger.error(f"Failed to open image bytes with Pillow: {pil_error}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid or corrupt image file.")

        # Now, pass the prepared PIL.Image object to MangaOcr
        text = mocr(img)
        # --- END OF FIX ---

        logger.info(f"OCR successful. Extracted text length: {len(text)}")
        return {"text": text}

    except Exception as e:
        logger.error(f"An error occurred during OCR processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process image with Manga OCR. See service logs for details.")


@app.get("/")
def read_root():
    return {"message": "Manga OCR service is running. POST an image to /ocr to extract text."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OCR", "port": 8000}