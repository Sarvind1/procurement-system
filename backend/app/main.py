"""FastAPI application main module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

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
        title="Procurement Management System",
        description="API for managing procurement processes",
        version="1.0.0",
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

    # Exception handlers
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    @application.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    return application


app = create_application()