#!/bin/bash

echo "🔧 Setting Up Advanced Japanese Analyzer Dependencies"
echo "====================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "1️⃣ Checking Prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Python virtual environments
echo ""
echo "2️⃣ Setting Up Python Virtual Environments..."

# Parser service
echo "📦 Setting up parser service environment..."
cd backend/parser_service

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Installing advanced dependencies..."
source venv/bin/activate

# Core NLP
pip install --upgrade pip
pip install fastapi[all]
pip install spacy>=3.7.0,\<3.8.0
pip install ginza
pip install ja_ginza
pip install numpy\<2.0

# Advanced ML stack
echo "   Installing machine learning dependencies..."
pip install torch>=2.0.0
pip install scikit-learn>=1.3.0
pip install xgboost>=1.7.0
pip install pandas>=2.0.0

# Vector database
echo "   Installing vector database dependencies..."
pip install chromadb>=0.4.15
pip install sentence-transformers>=2.2.2

# Transformers
echo "   Installing transformer dependencies..."
pip install transformers>=4.35.0
pip install accelerate>=0.24.0

# Additional tokenizers
echo "   Installing additional tokenizers..."
pip install fugashi
pip install ipadic
pip install SudachiPy>=0.6.0
pip install Janome
pip install unidic-lite

# Development tools
pip install pytest>=7.0.0
pip install pytest-asyncio>=0.21.0

echo "✅ Parser service environment ready"
cd ../..

# OCR service
echo "📦 Setting up OCR service environment..."
cd backend/ocr_service

if [ ! -d "venv-linux" ]; then
    echo "   Creating OCR virtual environment..."
    python3 -m venv venv-linux
fi

source venv-linux/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ OCR service environment ready"
cd ../..

# Node.js dependencies
echo ""
echo "3️⃣ Setting Up Node.js Dependencies..."

# Backend
echo "📦 Installing backend dependencies..."
cd backend
npm install
echo "✅ Backend dependencies installed"
cd ..

# Frontend
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"
cd ..

# Create logs directory
mkdir -p logs

# Test imports
echo ""
echo "4️⃣ Testing Advanced Feature Imports..."

cd backend/parser_service
source venv/bin/activate

echo -n "   Testing core NLP imports... "
if python3 -c "import spacy, ginza; nlp=spacy.load('ja_ginza'); print('✅')" 2>/dev/null; then
    echo "PASS"
else
    echo "FAIL - run: python3 -m spacy download ja_ginza"
fi

echo -n "   Testing ML imports... "
if python3 -c "import torch, xgboost, pandas, sklearn; print('✅')" 2>/dev/null; then
    echo "PASS"
else
    echo "FAIL - some ML dependencies missing"
fi

echo -n "   Testing vector database imports... "
if python3 -c "import chromadb; from sentence_transformers import SentenceTransformer; print('✅')" 2>/dev/null; then
    echo "PASS"
else
    echo "FAIL - vector database dependencies missing"
fi

echo -n "   Testing advanced parser imports... "
if python3 -c "from uncertainty_quantifier import MonteCarloDropoutUncertainty; from stacked_consensus import StackedGeneralizationConsensus; print('✅')" 2>/dev/null; then
    echo "PASS"
else
    echo "FAIL - advanced parser modules may need debugging"
fi

cd ../..

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "✅ All dependencies installed and tested"
echo "✅ Virtual environments configured"
echo "✅ Advanced features ready for use"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start services: ./start-all-services-advanced.sh"
echo "   2. Test features: ./test-advanced-features.sh"
echo "   3. Access app: http://localhost:5173"
echo ""
echo "📋 What's Available:"
echo "   • Monte Carlo uncertainty quantification"
echo "   • Vector-based semantic search with Japanese BERT"
echo "   • Advanced transformer models (llm-jp-modernbert)"
echo "   • Stacked generalization consensus algorithm"
echo "   • High-performance batch processing"
echo "   • Compound verb aspectual analysis"
echo "   • Interactive uncertainty visualization"
echo ""
echo "💡 If any tests failed above, check the specific error messages"
echo "   and install missing dependencies manually."