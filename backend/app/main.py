"""FastAPI application main module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from pydantic import ValidationError

# Import our modules
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, create_tables
from app.core.logging import setup_logging, get_logger

# Initialize logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    This function handles startup and shutdown events for the FastAPI application.
    It sets up logging, initializes the database, and handles cleanup.
    """
    # Startup
    logger.info("Starting up Procurement Management System")
    setup_logging()
    
    # Create database tables if needed (only in development)
    if settings.ENVIRONMENT == "development":
        try:
            await create_tables()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
    
    # Setup monitoring for production
    if settings.ENVIRONMENT == "production":
        try:
            from prometheus_fastapi_instrumentator import Instrumentator
            instrumentator = Instrumentator()
            instrumentator.instrument(app).expose(app)
            logger.info("Prometheus monitoring enabled")
        except ImportError:
            logger.warning("Prometheus instrumentator not available")
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Procurement Management System")
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    This function creates the FastAPI app instance and configures all
    middleware, routers, and exception handlers.
    
    Returns:
        FastAPI: Configured application instance
    """
    logger.info("Creating FastAPI application")
    
    application = FastAPI(
        title="Procurement Management System",
        description="""
        A comprehensive procurement management system that streamlines 
        purchase order management, inventory tracking, supplier relationships, 
        and shipment monitoring for enterprise operations.
        """,
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Add security middleware first
    if settings.ENVIRONMENT == "production":
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
        logger.info("Trusted host middleware enabled")

    # Add compression middleware
    application.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.debug("GZip compression middleware enabled")
    
    # Add CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS middleware enabled for origins: {settings.BACKEND_CORS_ORIGINS}")

    # Include API routers
    application.include_router(api_router, prefix=settings.API_V1_STR)
    logger.info(f"API router included with prefix: {settings.API_V1_STR}")

    # Health check endpoint
    @application.get("/health")
    async def health_check():
        """
        Health check endpoint for load balancers and monitoring.
        
        Returns:
            dict: Health status information
        """
        return {
            "status": "healthy",
            "service": "procurement-backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }

    # Root endpoint
    @application.get("/")
    async def root():
        """
        Root endpoint with basic API information.
        
        Returns:
            dict: API information
        """
        return {
            "message": "Procurement Management System API",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
            "health": "/health"
        }

    # Exception handlers
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        """
        Handle HTTP exceptions with structured logging.
        
        Args:
            request: The HTTP request that caused the exception
            exc: The HTTP exception that was raised
            
        Returns:
            JSONResponse: Formatted error response
        """
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "message": exc.detail,
                "type": "http_exception"
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """
        Handle request validation errors with detailed information.
        
        Args:
            request: The HTTP request that caused the exception
            exc: The validation exception that was raised
            
        Returns:
            JSONResponse: Formatted validation error response
        """
        logger.warning(
            f"Validation error: {exc} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "status_code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            },
        )

    @application.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request, exc):
        """
        Handle Pydantic validation errors.
        
        Args:
            request: The HTTP request that caused the exception
            exc: The Pydantic validation exception that was raised
            
        Returns:
            JSONResponse: Formatted validation error response
        """
        logger.warning(
            f"Pydantic validation error: {exc} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "status_code": 422,
                "message": "Data validation error",
                "type": "pydantic_validation_error",
                "details": str(exc)
            },
        )

    @application.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """
        Handle unexpected exceptions with secure error reporting.
        
        Args:
            request: The HTTP request that caused the exception
            exc: The exception that was raised
            
        Returns:
            JSONResponse: Formatted error response
        """
        logger.error(
            f"Unexpected error: {exc} - "
            f"Path: {request.url.path} - Method: {request.method}",
            exc_info=True
        )
        
        # Don't expose internal errors in production
        if settings.ENVIRONMENT == "production":
            message = "Internal server error"
            details = None
        else:
            message = str(exc)
            details = type(exc).__name__
        
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "status_code": 500,
                "message": message,
                "type": "internal_server_error",
                "details": details
            },
        )

    logger.info("FastAPI application created and configured")
    return application


# Create the application instance
app = create_application()

# Add any additional startup logic here if needed
if __name__ == "__main__":
    import uvicorn
    
    # This is only used when running the file directly
    # In production, use: uvicorn app.main:app
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
