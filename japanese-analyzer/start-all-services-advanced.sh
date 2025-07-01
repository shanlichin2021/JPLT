#!/bin/bash

# Advanced Japanese Analyzer - Complete Startup Script
# This script handles all dependencies and advanced features

echo "🚀 Starting Advanced Japanese Text Analyzer with Research Features..."
echo "=================================================================="

# Function to check if port is in use
check_port() {
    netstat -tuln | grep ":$1 " > /dev/null
    return $?
}

# Function to wait for service health
wait_for_service() {
    local service_name="$1"
    local health_url="$2"
    local max_wait="$3"
    local wait_time=0
    
    echo "⏳ Waiting for $service_name to initialize (max ${max_wait}s)..."
    
    while [ $wait_time -lt $max_wait ]; do
        if curl -s "$health_url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy!"
            return 0
        fi
        echo "   ⏳ Still initializing... (${wait_time}s/${max_wait}s)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    echo "⚠️  $service_name taking longer than expected. Continuing..."
    return 1
}

# Function to install dependencies if missing
install_dependencies() {
    echo "🔧 Checking and installing dependencies..."
    
    # Check parser service dependencies
    echo "📦 Checking parser service advanced dependencies..."
    cd backend/parser_service
    
    if [ ! -d "venv" ]; then
        echo "🆕 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install missing packages
    echo "📥 Installing advanced ML dependencies..."
    pip install --quiet torch>=2.0.0 xgboost>=1.7.0 pandas>=2.0.0 scikit-learn>=1.3.0
    pip install --quiet chromadb>=0.4.15 sentence-transformers>=2.2.2
    pip install --quiet accelerate>=0.24.0 transformers>=4.35.0
    pip install --quiet unidic-lite
    
    echo "✅ Advanced dependencies installed"
    cd ../..
    
    # Check OCR service
    echo "📦 Checking OCR service dependencies..."
    cd backend/ocr_service
    if [ ! -d "venv-linux" ]; then
        echo "🆕 Creating OCR virtual environment..."
        python3 -m venv venv-linux
        source venv-linux/bin/activate
        pip install -r requirements.txt
    fi
    cd ../..
    
    # Check Node.js dependencies
    echo "📦 Checking Node.js dependencies..."
    cd backend
    if [ ! -d "node_modules" ]; then
        echo "🆕 Installing backend dependencies..."
        npm install
    fi
    cd ..
    
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "🆕 Installing frontend dependencies..."
        npm install
    fi
    cd ..
}

# Function to start advanced service with proper initialization
start_advanced_service() {
    local service_name="$1"
    local command="$2"
    local port="$3"
    local health_url="$4"
    local max_wait="$5"
    
    echo "🚀 Starting $service_name on port $port..."
    
    if check_port $port; then
        echo "⚠️  Port $port is already in use. Checking if $service_name is healthy..."
        if wait_for_service "$service_name" "$health_url" 10; then
            echo "✅ $service_name already running and healthy"
            return 0
        else
            echo "❌ Service on port $port not responding. Please stop it first."
            return 1
        fi
    fi
    
    # Start service in background
    bash -c "$command" &
    local pid=$!
    
    # Give service time to initialize
    sleep 5
    
    # Check if process is still running
    if ! kill -0 $pid 2>/dev/null; then
        echo "❌ $service_name failed to start. Check logs/$(echo $service_name | tr '[:upper:]' '[:lower:]' | tr ' ' '_').log"
        return 1
    fi
    
    # Wait for service to be healthy
    if wait_for_service "$service_name" "$health_url" "$max_wait"; then
        echo "✅ $service_name started successfully with PID $pid"
        return 0
    else
        echo "⚠️  $service_name started but may still be initializing"
        return 0
    fi
}

# Create logs directory
mkdir -p logs

# Step 1: Install/check dependencies
install_dependencies

# Step 2: Start services with proper initialization times
echo ""
echo "🎯 Starting Services with Advanced Features..."
echo "============================================="

# 1. Start Parser Service (needs longest initialization time for transformers)
echo "1️⃣ Starting Advanced Parser Service..."
cd backend/parser_service
start_advanced_service "Parser Service" "source venv/bin/activate && uvicorn parser:app --host 0.0.0.0 --port 8001 > ../../logs/parser.log 2>&1" 8001 "http://localhost:8001/health" 60
cd ../..

# 2. Start OCR Service
echo "2️⃣ Starting OCR Service..."
cd backend/ocr_service
start_advanced_service "OCR Service" "source venv-linux/bin/activate && uvicorn ocr_server:app --host 0.0.0.0 --port 8000 > ../../logs/ocr.log 2>&1" 8000 "http://localhost:8000/health" 30
cd ../..

# 3. Start Backend API
echo "3️⃣ Starting Backend API..."
cd backend
start_advanced_service "Backend API" "node server.js > ../logs/backend.log 2>&1" 3000 "http://localhost:3000/health" 15
cd ..

# 4. Start Frontend
echo "4️⃣ Starting Frontend..."
cd frontend
start_advanced_service "Frontend" "npm run dev > ../logs/frontend.log 2>&1" 5173 "http://localhost:5173" 20
cd ..

# Step 3: Verify advanced features
echo ""
echo "🔬 Verifying Advanced Features..."
echo "================================"

# Test parser service advanced features
if curl -s "http://localhost:8001/health" | grep -q '"monte_carlo_uncertainty":true'; then
    echo "✅ Uncertainty quantification: ENABLED"
else
    echo "⚠️  Uncertainty quantification: Limited"
fi

if curl -s "http://localhost:8001/health" | grep -q '"vector_semantic_search":true'; then
    echo "✅ Vector database: ENABLED"
else
    echo "⚠️  Vector database: Limited"
fi

if curl -s "http://localhost:8001/health" | grep -q '"transformer_models":true'; then
    echo "✅ Advanced transformers: ENABLED"
else
    echo "⚠️  Advanced transformers: Limited (no GPU or still loading)"
fi

# Final summary
echo ""
echo "🎉 Advanced Japanese Text Analyzer Started!"
echo "==========================================="
echo ""
echo "📱 Frontend Application: http://localhost:5173"
echo "🔧 Backend API: http://localhost:3000"
echo "🧠 Parser Service (Advanced): http://localhost:8001"
echo "👁️  OCR Service: http://localhost:8000"
echo ""
echo "🔬 Advanced Features Available:"
echo "   • Monte Carlo uncertainty quantification"
echo "   • Vector-based semantic search"
echo "   • Advanced transformer models (llm-jp-modernbert)"
echo "   • Stacked generalization consensus"
echo "   • Batch processing with optimization"
echo "   • Compound verb aspectual analysis"
echo ""
echo "📊 Monitor Services:"
echo "   tail -f logs/parser.log     # Advanced NLP pipeline"
echo "   tail -f logs/ocr.log        # OCR processing"
echo "   tail -f logs/backend.log    # API and database"
echo "   tail -f logs/frontend.log   # UI development server"
echo ""
echo "🧪 Test Advanced Features:"
echo "   curl http://localhost:8001/health | jq"
echo "   curl -X POST http://localhost:8001/analyze/uncertainty -H 'Content-Type: application/json' -d '{\"text\":\"美しい花\"}'"
echo ""
echo "🛑 Stop All Services: ./stop-all-services.sh"