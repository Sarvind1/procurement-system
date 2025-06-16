#!/bin/bash

# Procurement System - Docker Compose Startup Script

echo "🚀 Starting Procurement System with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your settings if needed."
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start services
echo "🎯 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "✅ Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "🎉 Procurement System is ready!"
echo ""
echo "📌 Access Points:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:5173"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Flower (Celery): http://localhost:5555"
echo ""
echo "👤 Default Login:"
echo "   - Email: admin@procurement-system.com"
echo "   - Password: changethis123"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
