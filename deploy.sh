#!/bin/bash

# Deployment script for Patent Design Pattern System
set -e

echo "🏗️  Patent Design Pattern System - Deployment Script"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo "   (At minimum, set OPENAI_API_KEY if you have one)"
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "📁 Creating data directories..."
    mkdir -p data/{raw,chunks,index,media}
    echo "✅ Created data directories"
fi

# Check if index exists
if [ ! -d "data/index" ] || [ -z "$(ls -A data/index 2>/dev/null)" ]; then
    echo "⚠️  No patent index found. You need to run ingestion first."
    read -p "Do you want to run ingestion now? (This will take some time) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Running patent ingestion..."
        docker-compose run --rm api python ingest.py
        echo "✅ Ingestion complete"
    else
        echo "⚠️  Skipping ingestion. Make sure to run 'python ingest.py' before using the system."
    fi
fi

# Ask for deployment type
echo ""
echo "Select deployment type:"
echo "1) Development (docker-compose.yml)"
echo "2) Production (docker-compose.prod.yml with Nginx)"
read -p "Enter choice [1-2]: " -n 1 -r
echo

if [[ $REPLY == "2" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🚀 Starting production deployment..."
else
    COMPOSE_FILE="docker-compose.yml"
    echo "🚀 Starting development deployment..."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f $COMPOSE_FILE build

echo "🚀 Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 5

# Check health
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed. Check logs with: docker-compose logs api"
fi

# Display access information
echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo "=================================================="
if [[ $COMPOSE_FILE == "docker-compose.prod.yml" ]]; then
    echo "🌐 Frontend: http://localhost/"
    echo "🔌 API: http://localhost/api/"
else
    echo "🌐 Frontend: http://localhost:8501"
    echo "🔌 API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
fi
echo ""
echo "📊 View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "🛑 Stop services: docker-compose -f $COMPOSE_FILE down"
echo ""

