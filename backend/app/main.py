"""FastAPI application main module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.gzip import GZipMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    
    # Initialize database tables (if needed)
    # await create_tables()
    
    # Setup monitoring
    if settings.ENVIRONMENT == "production":
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
    
    yield
    
    # Shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Enterprise Procurement Management System API",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add middlewares
    application.add_middleware(GZipMiddleware, minimum_size=1000)
    
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    if settings.ENVIRONMENT == "production":
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Include routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Health check endpoint
    @application.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "procurement-backend"}

    return application


app = create_application()