#!/bin/bash

echo "🎯 Japanese Text Analyzer - Starting Python Services"
echo "===================================================="

# Check if we're in the right directory
if [[ ! -d "ocr_service" ]]; then
    echo "❌ Error: ocr_service directory not found"
    echo "Please run this script from the backend directory"
    exit 1
fi

if [[ ! -d "parser_service" ]]; then
    echo "❌ Error: parser_service directory not found"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Try to find Python executable
PYTHON_EXE="python3"

if [[ -f "ocr_service/.venv/bin/python" ]]; then
    PYTHON_EXE="ocr_service/.venv/bin/python"
    echo "📦 Using OCR service virtual environment"
elif [[ -f "parser_service/.venv/bin/python" ]]; then
    PYTHON_EXE="parser_service/.venv/bin/python"
    echo "📦 Using Parser service virtual environment"
elif [[ -f "venv/bin/python" ]]; then
    PYTHON_EXE="venv/bin/python"
    echo "📦 Using backend virtual environment"
else
    echo "📦 Using system Python"
fi

echo "🚀 Starting services with: $PYTHON_EXE"
echo

# Run the unified launcher
$PYTHON_EXE app.py

echo
echo "🏁 Services stopped"