"""Database session management with proper configuration."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    This function provides database sessions for FastAPI dependency injection.
    It ensures proper session lifecycle management with automatic commit/rollback.
    
    Yields:
        AsyncSession: Database session for use in API endpoints
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
