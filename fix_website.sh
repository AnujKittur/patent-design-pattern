#!/bin/bash

# Fix website issues - automated troubleshooting script

echo "🔧 Patent Design Website - Troubleshooting Script"
echo "===================================================="
echo ""

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo "✅ Docker is running"
        USE_DOCKER=true
    else
        echo "⚠️  Docker is installed but not running"
        echo "   Start Docker Desktop and try again"
        USE_DOCKER=false
    fi
else
    echo "❌ Docker is not installed"
    USE_DOCKER=false
fi

echo ""

# If Docker not available, offer local option
if [ "$USE_DOCKER" = false ]; then
    echo "Docker is not available. Options:"
    echo ""
    echo "Option 1: Start Docker Desktop (if installed)"
    echo "  1. Open Docker Desktop app"
    echo "  2. Wait for it to start"
    echo "  3. Run: docker-compose up --build"
    echo ""
    echo "Option 2: Run locally without Docker"
    echo "  Run: ./run_local.sh"
    echo ""
    read -p "Do you want to try running locally without Docker? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./run_local.sh
        exit 0
    else
        echo "Please start Docker Desktop and try again."
        exit 1
    fi
fi

# Docker is available - continue with Docker setup
echo "2. Checking environment..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating..."
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file exists"
fi

echo ""

echo "3. Checking data directory..."
if [ ! -d "data/index" ] || [ -z "$(ls -A data/index 2>/dev/null)" ]; then
    echo "⚠️  Patent index not found"
    read -p "Do you want to run patent ingestion now? (Takes 10-30 minutes) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Running patent ingestion..."
        docker-compose run --rm api python ingest.py
    else
        echo "⚠️  Skipping ingestion. Website may not work without patent index."
    fi
else
    echo "✅ Patent index found"
fi

echo ""

echo "4. Stopping any existing containers..."
docker-compose down 2>/dev/null

echo ""

echo "5. Building and starting services..."
docker-compose up --build -d

echo ""

echo "6. Waiting for services to start..."
sleep 10

echo ""

echo "7. Checking service health..."
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null)

if [ "$API_HEALTH" = "200" ]; then
    echo "✅ API is healthy (http://localhost:8000)"
else
    echo "❌ API is not responding (http://localhost:8000)"
    echo "   Check logs: docker-compose logs api"
fi

if [ "$FRONTEND_CHECK" = "200" ] || [ "$FRONTEND_CHECK" = "000" ]; then
    echo "✅ Frontend is accessible (http://localhost:8501)"
else
    echo "❌ Frontend is not responding (http://localhost:8501)"
    echo "   Check logs: docker-compose logs frontend"
fi

echo ""
echo "============================================"
echo "📍 Access your website:"
echo "   • Frontend: http://localhost:8501"
echo "   • API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""

if [ "$API_HEALTH" != "200" ] || [ "$FRONTEND_CHECK" != "200" ]; then
    echo "⚠️  Some services are not responding correctly."
    echo "   Check logs: docker-compose logs"
    echo "   Or try running locally: ./run_local.sh"
fi

