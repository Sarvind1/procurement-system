"""User management API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import UserService

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserRead]:
    """
    Retrieve a list of all users.
    
    This endpoint allows administrators to view all users in the system.
    Regular users can only see their own profile.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        List of user records
        
    Raises:
        HTTPException: If user lacks permission to view users
    """
    logger.info(f"User {current_user.id} requesting user list")
    
    # Check if user has permission to view all users
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view users"
        )
    
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    
    logger.info(f"Retrieved {len(users)} users")
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Get a specific user by ID.
    
    Users can only view their own profile unless they are administrators.
    
    Args:
        user_id: The ID of the user to retrieve
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found or access denied
    """
    logger.info(f"User {current_user.id} requesting user {user_id}")
    
    # Check if user can access this profile
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"Retrieved user {user_id}")
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Create a new user.
    
    Only administrators can create new users through this endpoint.
    
    Args:
        user_data: User creation data
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If user lacks permission or email already exists
    """
    logger.info(f"User {current_user.id} creating new user: {user_data.email}")
    
    # Check if user has permission to create users
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create users"
        )
    
    user_service = UserService(db)
    
    # Check if user with email already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        logger.warning(f"Attempt to create user with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await user_service.create_user(user_data)
    logger.info(f"Created new user: {user.id}")
    
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Update a user's information.
    
    Users can update their own profile, administrators can update any user.
    
    Args:
        user_id: The ID of the user to update
        user_data: Updated user data
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found or access denied
    """
    logger.info(f"User {current_user.id} updating user {user_id}")
    
    # Check if user can update this profile
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning(f"Attempt to update non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await user_service.update_user(user_id, user_data)
    logger.info(f"Updated user: {user_id}")
    
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a user (soft delete).
    
    Only administrators can delete users. Users cannot delete themselves.
    
    Args:
        user_id: The ID of the user to delete
        db: Database session dependency
        current_user: Currently authenticated user
        
    Raises:
        HTTPException: If user not found, access denied, or trying to delete self
    """
    logger.info(f"User {current_user.id} attempting to delete user {user_id}")
    
    # Check if user has permission to delete users
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users"
        )
    
    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning(f"Attempt to delete non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user_service.delete_user(user_id)
    logger.info(f"Deleted user: {user_id}")


@router.get("/{user_id}/profile", response_model=UserRead)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Get user profile information.
    
    This is an alias for the get_user endpoint with additional
    profile-specific information.
    
    Args:
        user_id: The ID of the user whose profile to retrieve
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        User profile data
    """
    return await get_user(user_id, db, current_user)


@router.put("/{user_id}/status", response_model=UserRead)
async def update_user_status(
    user_id: str,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Update user's active status.
    
    Only administrators can activate/deactivate users.
    
    Args:
        user_id: The ID of the user to update
        is_active: New active status
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found or access denied
    """
    logger.info(f"User {current_user.id} updating status of user {user_id} to {is_active}")
    
    # Check if user has permission
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update user status"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        logger.warning(f"Attempt to update status of non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = UserUpdate(is_active=is_active)
    updated_user = await user_service.update_user(user_id, user_data)
    
    logger.info(f"Updated user {user_id} status to {is_active}")
    return updated_user
