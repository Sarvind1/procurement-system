"""FastAPI application main module with enhanced logging."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time
import uuid

from fastapi import FastAPI, Request, Response
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
    Create and configure FastAPI application with comprehensive logging.
    
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

    # Add request/response logging middleware
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Log all incoming requests and outgoing responses.
        """
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Store request ID in request state for use in logs
        request.state.request_id = request_id
        
        # Log request details
        start_time = time.time()
        
        # Get request body for POST/PUT requests (be careful with large bodies)
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.body()
                # Create a new request with the same body
                request._body = request_body
            except Exception as e:
                logger.error(f"Error reading request body: {e}")
        
        logger.info(
            f"Incoming request - ID: {request_id} - "
            f"Method: {request.method} - Path: {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'} - "
            f"Headers: {dict(request.headers)}"
        )
        
        if request_body and len(request_body) < 1000:  # Only log small bodies
            logger.debug(f"Request body - ID: {request_id} - Body: {request_body.decode('utf-8', errors='ignore')}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Outgoing response - ID: {request_id} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"Path: {request.url.path}"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - ID: {request_id} - "
                f"Error: {str(e)} - Time: {process_time:.3f}s - "
                f"Path: {request.url.path}",
                exc_info=True
            )
            raise

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
    
    # Add CORS middleware with detailed logging
    if settings.BACKEND_CORS_ORIGINS:
        cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
        application.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS middleware enabled for origins: {cors_origins}")

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
        try:
            # Test database connection
            from app.db.session import get_db
            async for db in get_db():
                await db.execute("SELECT 1")
                db_status = "healthy"
                break
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            logger.error(f"Database health check failed: {e}")
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "service": "procurement-backend",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": db_status
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

    # Exception handlers with enhanced logging
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle HTTP exceptions with structured logging.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"HTTP exception - ID: {request_id} - "
            f"Status: {exc.status_code} - Detail: {exc.detail} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "request_id": request_id,
                "status_code": exc.status_code,
                "message": exc.detail,
                "type": "http_exception"
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle request validation errors with detailed information.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"Validation error - ID: {request_id} - "
            f"Errors: {exc.errors()} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "request_id": request_id,
                "status_code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            },
        )

    @application.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """
        Handle Pydantic validation errors.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"Pydantic validation error - ID: {request_id} - "
            f"Error: {str(exc)} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "request_id": request_id,
                "status_code": 422,
                "message": "Data validation error",
                "type": "pydantic_validation_error",
                "details": str(exc)
            },
        )

    @application.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle unexpected exceptions with secure error reporting.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"Unexpected error - ID: {request_id} - "
            f"Error: {str(exc)} - Type: {type(exc).__name__} - "
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
                "request_id": request_id,
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
