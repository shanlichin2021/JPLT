#!/bin/bash

# Japanese Analyzer - Start All Services Script
# This script starts all required services for the Japanese text analyzer

echo "🚀 Starting Japanese Text Analyzer Services..."
echo ""
echo "⚠️  NOTICE: This is the basic startup script."
echo "   For ADVANCED FEATURES (uncertainty quantification, vector search, transformers):"
echo "   Use: ./start-all-services-advanced.sh"
echo ""

# Function to check if port is in use
check_port() {
    netstat -tuln | grep ":$1 " > /dev/null
    return $?
}

# Function to start service with error handling
start_service() {
    local service_name="$1"
    local command="$2"
    local port="$3"
    
    echo "Starting $service_name on port $port..."
    
    if check_port $port; then
        echo "⚠️  Port $port is already in use. $service_name may already be running."
        return 1
    fi
    
    # Start service in background with error handling
    bash -c "$command" &
    local pid=$!
    
    # Give service a moment to start
    sleep 2
    
    # Check if process is still running
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $service_name started successfully with PID $pid"
        return 0
    else
        echo "❌ $service_name failed to start. Check logs/$(echo $service_name | tr '[:upper:]' '[:lower:]' | tr ' ' '_').log"
        return 1
    fi
}

# Create logs directory if it doesn't exist
mkdir -p logs

echo "📋 Checking services..."

# 1. Start Parser Service (FastAPI)
echo "1️⃣ Starting Parser Service (Port 8001)..."
cd backend/parser_service
start_service "Parser Service" "source venv/bin/activate && uvicorn parser:app --host 0.0.0.0 --port 8001 > ../../logs/parser.log 2>&1" 8001
cd ../..

# 2. Start OCR Service (FastAPI with MangaOCR) 
echo "2️⃣ Starting OCR Service (Port 8000)..."
cd backend/ocr_service
start_service "OCR Service" "source venv-linux/bin/activate && uvicorn ocr_server:app --host 0.0.0.0 --port 8000 > ../../logs/ocr.log 2>&1" 8000
cd ../..

# 3. Start Backend API (Express)
echo "3️⃣ Starting Backend API (Port 3000)..."
cd backend
start_service "Backend API" "node server.js > ../logs/backend.log 2>&1" 3000
cd ..

# 4. Start Frontend (Vite)
echo "4️⃣ Starting Frontend (Port 5173)..."
cd frontend
start_service "Frontend" "npm run dev > ../logs/frontend.log 2>&1" 5173
cd ..

echo ""
echo "🎉 All services started!"
echo ""
echo "📱 Access the application at: http://localhost:5173"
echo "🔧 Backend API: http://localhost:3000"
echo "🧠 Parser Service: http://localhost:8001"
echo "👁️  OCR Service: http://localhost:8000"
echo ""
echo "📊 View logs:"
echo "  - Parser: tail -f logs/parser.log"
echo "  - OCR: tail -f logs/ocr.log"
echo "  - Backend: tail -f logs/backend.log"
echo "  - Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop all services, run: ./stop-all-services.sh"