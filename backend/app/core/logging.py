"""Logging configuration for the application."""

import logging
import logging.config
import sys
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging.
    
    This function sets up structured logging with appropriate formatters
    and handlers based on the environment (development vs production).
    """
    
    # Define log format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    )
    
    # Simple format for development
    simple_format = "%(levelname)s:     %(name)s - %(message)s"
    
    # Choose format based on environment
    formatter = log_format if settings.ENVIRONMENT == "production" else simple_format
    
    # Logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": formatter,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(funcName)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "level": settings.LOG_LEVEL,
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json" if settings.ENVIRONMENT == "production" else "standard",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"] if settings.ENVIRONMENT == "production" else ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    # Create logs directory if it doesn't exist (only in production)
    if settings.ENVIRONMENT == "production":
        import os
        os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Get logger for this module
    logger = logging.getLogger("app.core.logging")
    logger.info(f"Logging configured for {settings.ENVIRONMENT} environment with level {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: The name of the logger (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(f"app.{name}")


# Structured logging helpers
def log_api_request(logger: logging.Logger, method: str, path: str, user_id: str = None) -> None:
    """Log API request with structured data."""
    extra_data = {
        "event_type": "api_request",
        "method": method,
        "path": path,
    }
    if user_id:
        extra_data["user_id"] = user_id
    
    logger.info(f"API Request: {method} {path}", extra=extra_data)


def log_database_operation(logger: logging.Logger, operation: str, table: str, record_id: str = None) -> None:
    """Log database operation with structured data."""
    extra_data = {
        "event_type": "database_operation",
        "operation": operation,
        "table": table,
    }
    if record_id:
        extra_data["record_id"] = record_id
    
    logger.info(f"Database {operation} on {table}", extra=extra_data)


def log_authentication_event(logger: logging.Logger, event: str, user_id: str = None, success: bool = True) -> None:
    """Log authentication events with structured data."""
    extra_data = {
        "event_type": "authentication",
        "auth_event": event,
        "success": success,
    }
    if user_id:
        extra_data["user_id"] = user_id
    
    level = logger.info if success else logger.warning
    level(f"Authentication {event}: {'Success' if success else 'Failed'}", extra=extra_data)


def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with additional context."""
    extra_data = {
        "event_type": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        extra_data.update(context)
    
    logger.error(f"Error occurred: {error}", extra=extra_data, exc_info=True)
