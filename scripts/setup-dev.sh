#!/bin/bash

# Development setup script for Procurement System
# This script sets up the development environment

set -e

echo "🚀 Setting up Procurement System development environment..."

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

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env 2>/dev/null || echo "⚠️  Backend .env.example not found, skipping..."
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env 2>/dev/null || echo "⚠️  Frontend .env.example not found, skipping..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/minio

# Pull Docker images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d postgres redis minio

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Run database migrations (when implemented)
echo "🗃️  Setting up database..."
# docker-compose exec backend alembic upgrade head

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Show service status
echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🌐 Services available at:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   MinIO:     http://localhost:9001 (admin/admin123)"
echo "   Flower:    http://localhost:5555"
echo ""
echo "📚 Useful commands:"
echo "   View logs:           docker-compose logs -f"
echo "   Stop services:       docker-compose down"
echo "   Restart services:    docker-compose restart"
echo "   Run backend shell:   docker-compose exec backend bash"
echo "   Run frontend shell:  docker-compose exec frontend sh"
echo ""
echo "🎉 Happy coding!"