#!/bin/bash

# Simple script to start both services correctly

echo "🚀 Starting Patent Design Website"
echo "=================================="
echo ""

# Change to project directory
cd /Users/anuj_kittur/Desktop/Scraper

# Stop any existing processes
echo "1. Stopping any existing services..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f streamlit 2>/dev/null
sleep 2

# Check if API is needed
API_RUNNING=false
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API is already running"
    API_RUNNING=true
else
    echo "2. Starting API server..."
    python3 app.py > api.log 2>&1 &
    API_PID=$!
    echo "   Started API (PID: $API_PID)"
    
    # Wait for API to start
    echo "   Waiting for API to start..."
    for i in {1..10}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            echo "   ✅ API is healthy!"
            API_RUNNING=true
            break
        fi
        sleep 1
    done
    
    if [ "$API_RUNNING" = false ]; then
        echo "   ❌ API failed to start. Check api.log"
        cat api.log
        exit 1
    fi
fi

echo ""
echo "3. Starting Streamlit frontend..."
echo ""
echo "============================================"
echo "✅ Services are starting!"
echo "============================================"
echo ""
echo "📍 Your website will be available at:"
echo "   • Frontend: http://localhost:8501"
echo "   • API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "⏳ Streamlit is starting... This may take 10-20 seconds"
echo "   A browser window should open automatically"
echo ""
echo "Press Ctrl+C to stop the website"
echo ""

# Start Streamlit in foreground so we can see errors
streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false

