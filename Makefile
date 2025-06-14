# Makefile for Procurement System
# Provides convenient commands for development and deployment

.PHONY: help install dev build test clean docker-build docker-up docker-down

# Default target
help:
	@echo "Procurement System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start development environment"
	@echo "  install      - Install dependencies"
	@echo "  build        - Build all services"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run linting and formatting"
	@echo "  clean        - Clean up development environment"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up    - Start Docker services"
	@echo "  docker-down  - Stop Docker services"
	@echo "  docker-logs  - View Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  db-backup    - Backup database"
	@echo "  db-restore   - Restore database from backup"
	@echo "  db-reset     - Reset database with sample data"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-prod  - Deploy to production"
	@echo "  deploy-stage - Deploy to staging"

# Development commands
dev:
	@echo "🚀 Starting development environment..."
	@chmod +x scripts/setup-dev.sh
	@./scripts/setup-dev.sh

install:
	@echo "📦 Installing dependencies..."
	@cd backend && poetry install
	@cd frontend && npm install

build:
	@echo "🔨 Building all services..."
	@cd backend && poetry build
	@cd frontend && npm run build

test:
	@echo "🧪 Running tests..."
	@cd backend && poetry run pytest
	@cd frontend && npm run test

test-coverage:
	@echo "📊 Running tests with coverage..."
	@cd backend && poetry run pytest --cov=app --cov-report=html
	@cd frontend && npm run test:coverage

lint:
	@echo "🔍 Running linting and formatting..."
	@cd backend && poetry run black . && poetry run isort . && poetry run pylint app/
	@cd frontend && npm run lint:fix && npm run format

clean:
	@echo "🧹 Cleaning up development environment..."
	@chmod +x scripts/cleanup.sh
	@./scripts/cleanup.sh

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	@docker-compose build

docker-up:
	@echo "🚀 Starting Docker services..."
	@docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	@docker-compose down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	@docker-compose logs -f

docker-restart:
	@echo "🔄 Restarting Docker services..."
	@docker-compose restart

# Database commands
db-backup:
	@echo "💾 Creating database backup..."
	@chmod +x scripts/backup-db.sh
	@./scripts/backup-db.sh

db-restore:
	@echo "🔄 Restoring database from backup..."
	@chmod +x scripts/restore-db.sh
	@./scripts/restore-db.sh

db-reset:
	@echo "🗃️ Resetting database with sample data..."
	@docker-compose exec backend alembic downgrade base
	@docker-compose exec backend alembic upgrade head
	@python scripts/generate-sample-data.py
	@echo "✅ Database reset complete"

db-migrate:
	@echo "🗃️ Running database migrations..."
	@docker-compose exec backend alembic upgrade head

db-shell:
	@echo "🐘 Connecting to database shell..."
	@docker-compose exec postgres psql -U postgres -d procurement

# Sample data
generate-data:
	@echo "🎲 Generating sample data..."
	@python scripts/generate-sample-data.py

# Health checks
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend unhealthy"
	@docker-compose ps

# Security
security-scan:
	@echo "🔒 Running security scans..."
	@cd backend && poetry run bandit -r app/
	@cd backend && poetry run safety check
	@cd frontend && npm audit

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@cd backend && poetry run sphinx-build -b html docs/ docs/_build/
	@echo "📖 API documentation available at: http://localhost:8000/docs"

# Performance
load-test:
	@echo "⚡ Running load tests..."
	@echo "Load testing not implemented yet"

# Deployment (placeholder commands)
deploy-stage:
	@echo "🚀 Deploying to staging..."
	@echo "Staging deployment not implemented yet"

deploy-prod:
	@echo "🚀 Deploying to production..."
	@echo "Production deployment not implemented yet"

# Quick shortcuts
up: docker-up
down: docker-down
logs: docker-logs
restart: docker-restart
ps:
	@docker-compose ps

# Backend specific
backend-shell:
	@docker-compose exec backend bash

backend-logs:
	@docker-compose logs -f backend

# Frontend specific
frontend-shell:
	@docker-compose exec frontend sh

frontend-logs:
	@docker-compose logs -f frontend

# Monitoring
monitor:
	@echo "📊 Opening monitoring dashboards..."
	@echo "Flower (Celery): http://localhost:5555"
	@echo "MinIO Console: http://localhost:9001"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:3000"