#!/bin/bash

# Simple script to start the website - checks and starts both services

echo "🚀 Starting Patent Design Website"
echo "================================"
echo ""

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check port 8000 (API)
if check_port 8000; then
    echo "✅ API is already running on port 8000"
    API_RUNNING=true
else
    echo "⚠️  API is not running. Starting API server..."
    API_RUNNING=false
    
    # Start API in background
    cd /Users/anuj_kittur/Desktop/Scraper
    python3 app.py > api.log 2>&1 &
    API_PID=$!
    echo "   Started API server (PID: $API_PID)"
    
    # Wait for API to start
    echo "   Waiting for API to start..."
    sleep 5
    
    # Check if API started successfully
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "   ✅ API is now healthy!"
        API_RUNNING=true
    else
        echo "   ❌ API failed to start. Check api.log for errors"
        echo "   Run: cat api.log"
        exit 1
    fi
fi

echo ""

# Check port 8501 (Frontend)
if check_port 8501; then
    echo "✅ Frontend is already running on port 8501"
    echo ""
    echo "📍 Your website is already running!"
    echo "   • Website: http://localhost:8501"
    echo "   • API: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo "⚠️  Frontend is not running. Starting Streamlit..."
    
    # Start Streamlit
    cd /Users/anuj_kittur/Desktop/Scraper
    echo ""
    echo "🚀 Starting Streamlit frontend..."
    echo "   This will open in your browser automatically"
    echo ""
    
    # Start Streamlit (this will block, so run in foreground)
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
fi

