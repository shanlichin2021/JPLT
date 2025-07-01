@echo off
echo 🎯 Japanese Text Analyzer - Starting Python Services
echo ====================================================

:: Check if we're in the right directory
if not exist "ocr_service" (
    echo ❌ Error: ocr_service directory not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

if not exist "parser_service" (
    echo ❌ Error: parser_service directory not found  
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

:: Try to find Python executable
set PYTHON_EXE=python
if exist "ocr_service\.venv\Scripts\python.exe" (
    set PYTHON_EXE=ocr_service\.venv\Scripts\python.exe
    echo 📦 Using OCR service virtual environment
) else if exist "parser_service\.venv\Scripts\python.exe" (
    set PYTHON_EXE=parser_service\.venv\Scripts\python.exe
    echo 📦 Using Parser service virtual environment
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    echo 📦 Using backend virtual environment
) else (
    echo 📦 Using system Python
)

echo 🚀 Starting services with: %PYTHON_EXE%
echo.

:: Run the unified launcher
%PYTHON_EXE% app.py

echo.
echo 🏁 Services stopped
pause