#!/bin/bash

# Run website locally without Docker
# This is an alternative if Docker is not available

echo "🚀 Starting Patent Design Website (Local Mode - No Docker)"
echo "==========================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "============================================"
echo "✅ Dependencies installed!"
echo "============================================"
echo ""
echo "Starting services..."
echo ""
echo "⚠️  IMPORTANT: You need TWO terminal windows!"
echo ""
echo "Terminal 1 - API Server:"
echo "  1. Open a new terminal"
echo "  2. Run: cd $(pwd) && source venv/bin/activate && python app.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  1. Open another terminal"
echo "  2. Run: cd $(pwd) && source venv/bin/activate && streamlit run streamlit_app.py"
echo ""
echo "Or run the API server in background now? [y/N]"
read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting API server in background..."
    python app.py &
    API_PID=$!
    echo "✅ API server started (PID: $API_PID)"
    echo ""
    echo "⏳ Waiting for API to start..."
    sleep 5
    
    # Check if API is running
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ API is healthy!"
    else
        echo "⚠️  API may still be starting. Check http://localhost:8000/health"
    fi
    
    echo ""
    echo "🚀 Starting Streamlit frontend..."
    echo ""
    echo "📍 Access your website at: http://localhost:8501"
    echo "🔌 API available at: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop services"
    echo ""
    
    # Start Streamlit in foreground
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
else
    echo ""
    echo "📝 Manual start instructions:"
    echo ""
    echo "Terminal 1:"
    echo "  cd $(pwd)"
    echo "  source venv/bin/activate"
    echo "  python app.py"
    echo ""
    echo "Terminal 2:"
    echo "  cd $(pwd)"
    echo "  source venv/bin/activate"
    echo "  streamlit run streamlit_app.py"
    echo ""
fi

