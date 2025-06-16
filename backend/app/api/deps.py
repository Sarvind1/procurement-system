"""API dependency injection for authentication and database sessions."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

# Initialize logger
logger = get_logger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    This dependency extracts the JWT token from the Authorization header,
    verifies it, and returns the corresponding user from the database.
    
    Args:
        db: Database session dependency
        token: JWT token from Authorization header
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode the JWT token
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing user ID (sub claim)")
            raise credentials_exception
            
    except (JWTError, ValidationError) as e:
        logger.warning(f"Token validation failed: {e}")
        raise credentials_exception
    
    # Fetch user from database
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User {user_id} not found in database")
            raise credentials_exception
            
        if not user.is_active:
            logger.warning(f"Inactive user {user_id} attempted access")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        logger.debug(f"Successfully authenticated user {user_id}")
        return user
        
    except Exception as e:
        logger.error(f"Database error during user authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current active user.
    
    This is a convenience dependency that ensures the user is active.
    It's redundant since get_current_user already checks this, but
    provided for explicit dependency injection where needed.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user {current_user.id} attempted access")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current admin user.
    
    This dependency ensures the current user has admin privileges.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The admin user object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.id} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current superuser.
    
    This dependency ensures the current user has superuser privileges.
    Superusers have the highest level of access in the system.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The superuser object
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not getattr(current_user, 'is_superuser', False):
        logger.warning(f"Non-superuser {current_user.id} attempted superuser access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges. Superuser access required."
        )
    return current_user


async def get_current_manager_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get current manager user.
    
    This dependency ensures the current user has manager or admin privileges.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The manager user object
        
    Raises:
        HTTPException: If user is not a manager or admin
    """
    if not (current_user.is_admin or getattr(current_user, 'role', '') in ['manager', 'procurement_manager']):
        logger.warning(f"Non-manager user {current_user.id} attempted manager access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager access required."
        )
    return current_user


# Optional token dependency (for endpoints that work with or without auth)
async def get_optional_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme)
) -> User | None:
    """
    Get current user if token is provided and valid, otherwise return None.
    
    This dependency is useful for endpoints that can work both with
    authenticated and anonymous users.
    
    Args:
        db: Database session dependency
        token: Optional JWT token from Authorization header
        
    Returns:
        User | None: The authenticated user or None if not authenticated
    """
    if not token:
        return None
        
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.is_active:
            return user
            
    except (JWTError, ValidationError, Exception):
        # Silently fail for optional authentication
        pass
        
    return None
