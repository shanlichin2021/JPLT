#!/usr/bin/env python3
"""
Simple script to start the OCR service properly
"""
import subprocess
import sys
import os

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if we're on Windows
    if sys.platform.startswith('win') or os.name == 'nt':
        python_exe = os.path.join('.venv', 'Scripts', 'python.exe')
        if not os.path.exists(python_exe):
            print("Error: Windows virtual environment not found at .venv/Scripts/python.exe")
            sys.exit(1)
    else:
        python_exe = os.path.join('.venv', 'bin', 'python')
        if not os.path.exists(python_exe):
            python_exe = 'python3'  # fallback
    
    # Start the OCR service
    cmd = [python_exe, '-m', 'uvicorn', 'ocr_server:app', '--host', '0.0.0.0', '--port', '8000']
    
    print(f"Starting OCR service with command: {' '.join(cmd)}")
    print("OCR service will be available at http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down OCR service...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting OCR service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()