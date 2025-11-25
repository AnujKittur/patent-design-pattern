#!/bin/bash

# Quick start script for local development
set -e

echo "🚀 Starting Patent Design Pattern System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Using defaults..."
fi

# Start services
if command -v docker-compose &> /dev/null; then
    docker-compose up
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

