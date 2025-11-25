#!/bin/bash

# Quick script to start the website and show sharing information

echo "🚀 Starting Patent Design Pattern Website..."
echo "============================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "   Edit it to add your OPENAI_API_KEY (optional)"
fi

# Check if data directory exists
if [ ! -d "data/index" ] || [ -z "$(ls -A data/index 2>/dev/null)" ]; then
    echo "⚠️  Patent index not found."
    read -p "Do you want to run patent ingestion first? This will take time. [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Running patent ingestion..."
        docker-compose run --rm api python ingest.py
    fi
fi

# Start services
echo ""
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 5

# Get IP address
echo ""
echo "============================================="
echo "✅ Website is starting!"
echo "============================================="
echo ""

# Try to get IP address
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$IP" ]; then
    echo "⚠️  Could not automatically detect IP address"
    echo ""
    echo "📍 Access locally:"
    echo "   • Website: http://localhost:8501"
    echo "   • API: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
    echo "📱 To share with others on your network:"
    echo "   1. Find your IP address: ifconfig | grep 'inet '"
    echo "   2. Share: http://YOUR_IP:8501"
else
    echo "📍 Access locally:"
    echo "   • Website: http://localhost:8501"
    echo "   • API: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
    echo "🌐 Share with others on your network:"
    echo "   • Website: http://$IP:8501"
    echo "   • API: http://$IP:8000"
    echo ""
    echo "   Other devices on the same WiFi can access using the IP above."
fi

echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""

# Check health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API health check failed. Check logs with: docker-compose logs api"
fi

echo ""
echo "🎉 Setup complete! Open http://localhost:8501 in your browser."
