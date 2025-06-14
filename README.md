# Procurement Management System 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.x-blue.svg)](https://reactjs.org/)

A comprehensive enterprise procurement management system built with **FastAPI** and **React**, designed to streamline purchase orders, inventory management, supplier relationships, and shipment tracking.

## ✨ Features

### 🛒 **Purchase Order Management**
- Complete lifecycle from requisition to fulfillment
- Multi-level approval workflows
- Budget validation and controls
- Real-time status tracking

### 📦 **Inventory Control**
- Real-time stock tracking with automated reordering
- Multi-location inventory support
- Low stock alerts and notifications
- Barcode scanning support

### 🏢 **Supplier Management**
- Comprehensive vendor relationship management
- Performance scorecards and KPIs
- Contract and SLA management
- Risk assessment and monitoring

### 🚚 **Shipment Tracking**
- Multi-carrier logistics and delivery monitoring
- Real-time tracking updates
- Exception management and alerts
- Proof of delivery management

### 📊 **Analytics & Reporting**
- Data-driven procurement insights
- Spend analysis and cost optimization
- Supplier performance metrics
- Custom dashboards and reports

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ • React 18      │    │ • FastAPI       │    │ • PostgreSQL 15 │
│ • TypeScript    │    │ • SQLAlchemy    │    │ • Redis Cache   │
│ • Vite          │    │ • Pydantic      │    │ • MinIO Storage │
│ • React Query   │    │ • Celery        │    │                 │
│ • Tailwind CSS  │    │ • WebSockets    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL toolkit and ORM with async support
- **[PostgreSQL](https://www.postgresql.org/)** - Advanced open source relational database
- **[Redis](https://redis.io/)** - In-memory data structure store for caching
- **[Celery](https://celeryproject.org/)** - Distributed task queue for background processing

### Frontend
- **[React 18](https://reactjs.org/)** - A JavaScript library for building user interfaces
- **[TypeScript](https://www.typescriptlang.org/)** - Typed superset of JavaScript
- **[Vite](https://vitejs.dev/)** - Next generation frontend tooling
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[React Query](https://tanstack.com/query/)** - Data fetching and state management

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Sarvind1/procurement-system.git
cd procurement-system
```

### 2. Start Development Environment
```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Application

🌐 **Services:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

🔑 **Demo Credentials:**
- **Email:** `admin@procurement.com`
- **Password:** `admin123`

## 📋 Available Commands

### Development Commands
```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

### Database Commands
```bash
# Database shell
docker-compose exec postgres psql -U postgres -d procurement

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create database backup
docker-compose exec postgres pg_dump -U postgres procurement > backup.sql
```

## 📁 Project Structure

```
procurement-system/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API route definitions
│   │   ├── core/           # Core functionality (config, security)
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic layer
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── requirements/       # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API services
│   │   ├── stores/         # State management
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── tests/              # Frontend tests
├── docs/                   # Project documentation
├── scripts/                # Utility scripts
└── docker-compose.yml      # Multi-container Docker application
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test

# With coverage
npm run test:coverage
```

## 📚 Documentation

- 📖 **[Technical PRD](./docs/PRD.md)** - Comprehensive product requirements
- 🔧 **[API Documentation](./docs/api-reference.md)** - Complete API reference
- 🚀 **[Deployment Guide](./docs/deployment.md)** - Production deployment instructions
- 🤝 **[Contributing Guidelines](./CONTRIBUTING.md)** - How to contribute to the project

### Interactive Documentation
When running the application, visit:
- **API