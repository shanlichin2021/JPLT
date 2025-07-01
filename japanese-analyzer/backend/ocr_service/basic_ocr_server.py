#!/usr/bin/env python3
# basic_ocr_server.py - Ultra-simple OCR server using only Python standard library
import http.server
import socketserver
import json
import urllib.parse
import cgi
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "Basic OCR service is running",
                "version": "1.0.0",
                "status": "healthy",
                "endpoints": ["/", "/health", "/ocr"],
                "note": "Mock OCR service for testing"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "Basic OCR",
                "port": 8000,
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/ocr':
            try:
                # Parse multipart form data
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' not in content_type:
                    self.send_error_response(400, "Expected multipart/form-data")
                    return
                
                # Get content length
                content_length = int(self.headers.get('Content-Length', 0))
                
                if content_length == 0:
                    self.send_error_response(400, "No file uploaded")
                    return
                
                # Read the file data
                post_data = self.rfile.read(content_length)
                
                # Generate mock OCR result
                sample_texts = [
                    "こんにちは、世界！",
                    "日本語のテキストを解析します。",
                    "これはOCRテストのサンプルです。",
                    "漢字、ひらがな、カタカナが含まれています。",
                    "OCRサービスが正常に動作しています。"
                ]
                
                # Use data length to pick different sample texts
                text_index = len(post_data) % len(sample_texts)
                extracted_text = sample_texts[text_index]
                
                # Send successful response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "text": extracted_text,
                    "confidence": 0.95,
                    "processing_time_ms": 150,
                    "file_size_bytes": len(post_data),
                    "mock": True,
                    "note": "This is mock OCR data for testing"
                }
                
                logger.info(f"OCR request processed. Generated text: {extracted_text}")
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                logger.error(f"Error processing OCR request: {e}")
                self.send_error_response(500, f"Internal server error: {str(e)}")
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, status_code, message):
        """Send an error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"error": message, "status": status_code}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), OCRRequestHandler) as httpd:
        logger.info(f"Basic OCR Server starting on port {PORT}")
        logger.info(f"Server available at: http://localhost:{PORT}")
        logger.info("Endpoints:")
        logger.info("  GET  / - Service info")
        logger.info("  GET  /health - Health check") 
        logger.info("  POST /ocr - Process image (mock)")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()