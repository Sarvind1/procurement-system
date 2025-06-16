"""Database session management with proper configuration."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.config import settings

# Create async engine using the correct configuration
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.DEBUG,  # Use DEBUG instead of SQL_ECHO
    future=True,
    **settings.database_config
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    This function provides database sessions for FastAPI dependency injection.
    It ensures proper session lifecycle management with automatic commit/rollback.
    
    Yields:
        AsyncSession: Database session for use in API endpoints
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
