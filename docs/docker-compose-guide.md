# Docker Compose Setup Guide

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone and Navigate to Project
```bash
git clone https://github.com/Sarvind1/procurement-system.git
cd procurement-system
```

### 2. Start All Services
```bash
# Start all services in the background
docker-compose up -d

# Or to see logs in the terminal
docker-compose up
```

### 3. Access the Applications
Once all services are running, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **MinIO Console**: http://localhost:9001 (login: minioadmin/minioadmin123)
- **Flower (Celery Monitor)**: http://localhost:5555

### 4. Default Login Credentials
- **Email**: admin@procurement-system.com
- **Password**: changethis123

## Services Overview

### Core Services
1. **PostgreSQL** (postgres:5432) - Main database
2. **Redis** (redis:6379) - Caching and task queue
3. **MinIO** (minio:9000) - File storage
4. **Backend** (backend:8000) - FastAPI application
5. **Frontend** (frontend:5173) - React application

### Background Services
1. **Celery Worker** - Processes background tasks
2. **Celery Beat** - Schedules periodic tasks
3. **Flower** - Monitors Celery tasks

## Common Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Restart a service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Run database migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Create a new migration
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Access service shells
```bash
# Backend shell
docker-compose exec backend bash

# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d procurement

# Redis CLI
docker-compose exec redis redis-cli
```

## Troubleshooting

### Services not starting?
1. Check Docker Desktop is running
2. Check ports are not in use:
   ```bash
   # Check if ports are free
   lsof -i :8000  # Backend
   lsof -i :5173  # Frontend
   lsof -i :5432  # PostgreSQL
   lsof -i :6379  # Redis
   ```

### Database connection issues?
1. Wait for PostgreSQL to be fully ready:
   ```bash
   docker-compose logs postgres
   ```
2. Manually create database if needed:
   ```bash
   docker-compose exec postgres psql -U postgres -c "CREATE DATABASE procurement;"
   ```

### Frontend not connecting to backend?
1. Check CORS settings in `.env`
2. Ensure backend is running: `docker-compose ps backend`
3. Check backend logs: `docker-compose logs backend`

### Reset everything
```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove all containers and images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## Development Workflow

### Making code changes
- Backend changes: Automatically reloaded (FastAPI with --reload)
- Frontend changes: Automatically reloaded (Vite HMR)
- No need to restart containers for code changes

### Adding new dependencies

#### Backend
1. Add to `backend/requirements.txt`
2. Rebuild: `docker-compose build backend`
3. Restart: `docker-compose up -d backend`

#### Frontend
1. Add to `frontend/package.json`
2. Rebuild: `docker-compose build frontend`
3. Restart: `docker-compose up -d frontend`

## Environment Variables
- All configuration is in the root `.env` file
- Docker Compose automatically loads this file
- Service names (postgres, redis, minio) are used as hostnames within the Docker network

## Production Deployment
For production:
1. Update `.env` with production values
2. Change `SECRET_KEY` to a secure random value
3. Use external managed databases
4. Enable HTTPS
5. Set `DEBUG=false`
6. Use production Docker images (change target in docker-compose.yml)
