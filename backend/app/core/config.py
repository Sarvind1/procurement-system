"""Application configuration settings."""

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with development-friendly defaults."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        # Automatically look for .env file in parent directories
        env_file_encoding='utf-8'
    )
    
    # Application
    PROJECT_NAME: str = "Procurement System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security - Generate a default for development if not provided
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database - Provide development default
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_TEST_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Validate and set default database URL for development."""
        if v is None:
            # Default development database URL
            default_url = "postgresql://postgres:postgres@localhost:5432/procurement_db"
            print(f"⚠️  DATABASE_URL not set, using default: {default_url}")
            print("   Please create a .env file from .env.example for production use.")
            return default_url
        return v
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: Union[List[str], str] = ["localhost", "127.0.0.1"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse allowed hosts."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["localhost", "127.0.0.1"]
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Warn if using default secret key."""
        if v == secrets.token_urlsafe(32):
            print("⚠️  Using default SECRET_KEY - not suitable for production!")
            print("   Please set SECRET_KEY in your .env file.")
        return v
    
    # Object Storage (MinIO/S3)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "procurement-files"
    MINIO_SECURE: bool = False
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[EmailStr] = None
    EMAIL_FROM_NAME: Optional[str] = None
    
    # External APIs
    SHIPPING_API_KEY: Optional[str] = None
    PAYMENT_GATEWAY_API_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    NEW_RELIC_LICENSE_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # First Superuser (for initial setup)
    FIRST_SUPERUSER: Optional[EmailStr] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None
    
    def get_database_url(self, test: bool = False) -> str:
        """Get database URL."""
        if test and self.DATABASE_TEST_URL:
            return str(self.DATABASE_TEST_URL)
        return str(self.DATABASE_URL) if self.DATABASE_URL else "postgresql://postgres:postgres@localhost:5432/procurement_db"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "echo": self.DEBUG,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        }
    
    def __init__(self, **values):
        """Initialize settings with helpful error messages."""
        try:
            super().__init__(**values)
            print(f"✅ Configuration loaded successfully")
            print(f"   Environment: {self.ENVIRONMENT}")
            print(f"   Debug: {self.DEBUG}")
            print(f"   CORS Origins: {self.BACKEND_CORS_ORIGINS}")
            print(f"   Allowed Hosts: {self.ALLOWED_HOSTS}")
        except Exception as e:
            print("\n❌ Configuration Error!")
            print("=" * 50)
            print(f"Error: {str(e)}")
            print("\nTo fix this:")
            print("1. Check your .env file format")
            print("2. Ensure BACKEND_CORS_ORIGINS is a JSON array or comma-separated")
            print("3. Ensure ALLOWED_HOSTS is comma-separated")
            print("=" * 50)
            raise e


settings = Settings()
