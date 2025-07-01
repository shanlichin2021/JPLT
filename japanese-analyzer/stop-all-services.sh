#!/bin/bash

# Japanese Analyzer - Stop All Services Script

echo "🛑 Stopping Japanese Text Analyzer Services..."

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local service_name=$2
    
    echo "Stopping $service_name on port $port..."
    
    # Find and kill process using the port
    local pid=$(lsof -t -i:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            kill -KILL $pid 2>/dev/null
            echo "  ⚡ Force stopped $service_name (PID: $pid)"
        else
            echo "  ✅ Gracefully stopped $service_name (PID: $pid)"
        fi
    else
        echo "  ⚪ $service_name not running on port $port"
    fi
}

# Stop all services
kill_port 5173 "Frontend (Vite)"
kill_port 3000 "Backend API (Express)"
kill_port 8001 "Parser Service (FastAPI)"
kill_port 8000 "OCR Service (FastAPI)"

# Also kill any remaining Node/Python processes that might be related
echo ""
echo "🧹 Cleaning up remaining processes..."

# Kill any remaining vite processes
pkill -f "vite" 2>/dev/null && echo "  ✅ Stopped remaining Vite processes"

# Kill any remaining uvicorn processes  
pkill -f "uvicorn" 2>/dev/null && echo "  ✅ Stopped remaining uvicorn processes"

# Kill any remaining node processes (be careful here)
# pkill -f "node.*server.js" 2>/dev/null && echo "  ✅ Stopped remaining Node server processes"

echo ""
echo "✅ All services stopped!"
echo ""
echo "💡 Tip: Check if any processes are still running with:"
echo "  lsof -i :3000,5173,8000,8001"