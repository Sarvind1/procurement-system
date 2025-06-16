"""Authentication endpoints with comprehensive logging."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password
)
from app.core.logging import get_logger, log_authentication_event, log_error_with_context
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin
from app.schemas.user import UserCreate, UserResponse, UserUpdate, PasswordUpdate
from app.services.auth import AuthService

router = APIRouter()
logger = get_logger(__name__)

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user with detailed logging.
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    auth_service = AuthService(db)
    
    try:
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user = await auth_service.register_user(user_data)
        log_authentication_event(logger, "registration", user.id, success=True)
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        log_error_with_context(logger, e, {"endpoint": "register", "email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login with comprehensive logging.
    """
    client_ip = request.client.host
    logger.info(f"Login attempt from IP {client_ip} for username: {form_data.username}")
    
    auth_service = AuthService(db)
    
    try:
        # Convert OAuth2 form to our schema
        login_data = UserLogin(email=form_data.username, password=form_data.password)
        
        # Authenticate user
        user = await auth_service.authenticate_user(login_data)
        
        if not user:
            log_authentication_event(logger, "login", user_id=form_data.username, success=False)
            logger.warning(f"Login failed - invalid credentials for: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            log_authentication_event(logger, "login", user_id=str(user.id), success=False)
            logger.warning(f"Login failed - inactive user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            str(user.id), expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(str(user.id))
        
        log_authentication_event(logger, "login", user_id=str(user.id), success=True)
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id}) from IP: {client_ip}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error_with_context(logger, e, {
            "endpoint": "login", 
            "username": form_data.username,
            "client_ip": client_ip
        })
        logger.error(f"Login error for {form_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Refresh access token with logging.
    """
    logger.info(f"Token refresh requested for user: {current_user.email} (ID: {current_user.id})")
    
    try:
        access_token = create_access_token(str(current_user.id))
        refresh_token = create_refresh_token(str(current_user.id))
        
        log_authentication_event(logger, "token_refresh", user_id=str(current_user.id), success=True)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        log_error_with_context(logger, e, {
            "endpoint": "refresh",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout user with logging.
    """
    logger.info(f"Logout requested for user: {current_user.email} (ID: {current_user.id})")
    log_authentication_event(logger, "logout", user_id=str(current_user.id), success=True)
    
    # In a real application, you might want to blacklist the token
    # or implement token revocation logic here
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user with logging.
    """
    logger.debug(f"User profile accessed: {current_user.email} (ID: {current_user.id})")
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update current user with logging.
    """
    logger.info(f"User update requested for: {current_user.email} (ID: {current_user.id})")
    
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(current_user.id)
        if not user:
            logger.error(f"User not found during update: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Track what fields are being updated
        updated_fields = []
        for field, value in user_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(user, field, value)
                updated_fields.append(field)
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User updated successfully: {user.email} (ID: {user.id}). Updated fields: {updated_fields}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        log_error_with_context(logger, e, {
            "endpoint": "update_user",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.put("/me/password")
async def update_password(
    password_data: PasswordUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update current user's password with logging.
    """
    logger.info(f"Password change requested for user: {current_user.email} (ID: {current_user.id})")
    
    try:
        auth_service = AuthService(db)
        success = await auth_service.update_user_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        
        if not success:
            log_authentication_event(logger, "password_change", user_id=str(current_user.id), success=False)
            logger.warning(f"Password change failed - incorrect current password for user: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        log_authentication_event(logger, "password_change", user_id=str(current_user.id), success=True)
        logger.info(f"Password changed successfully for user: {current_user.email}")
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error_with_context(logger, e, {
            "endpoint": "update_password",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password update failed"
        )
