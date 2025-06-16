"""User service for business logic operations."""

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.password import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Initialize logger
logger = get_logger(__name__)


class UserService:
    """Service class for user-related business logic."""

    def __init__(self, db: AsyncSession):
        """
        Initialize user service with database session.
        
        Args:
            db: Database session for operations
        """
        self.db = db

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get a list of users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user objects
        """
        logger.debug(f"Fetching users with skip={skip}, limit={limit}")
        
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        
        logger.info(f"Retrieved {len(users)} users")
        return list(users)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            User object if found, None otherwise
        """
        logger.debug(f"Fetching user by ID: {user_id}")
        
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.debug(f"Found user {user_id}")
        else:
            logger.debug(f"User {user_id} not found")
            
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User object if found, None otherwise
        """
        logger.debug(f"Fetching user by email: {email}")
        
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.debug(f"Found user with email {email}")
        else:
            logger.debug(f"User with email {email} not found")
            
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            Exception: If user creation fails
        """
        logger.info(f"Creating new user with email: {user_data.email}")
        
        try:
            # Hash the password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user object
            db_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                is_active=user_data.is_active,
                role=getattr(user_data, 'role', 'user')
            )
            
            # Add to database
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            
            logger.info(f"Successfully created user {db_user.id}")
            return db_user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            await self.db.rollback()
            raise

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id: The user's unique identifier
            user_data: Updated user data
            
        Returns:
            Updated user object if found and updated, None otherwise
            
        Raises:
            Exception: If user update fails
        """
        logger.info(f"Updating user {user_id}")
        
        try:
            # Get user
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            # Build update data
            update_data = {}
            if user_data.email is not None:
                update_data['email'] = user_data.email
            if user_data.full_name is not None:
                update_data['full_name'] = user_data.full_name
            if user_data.is_active is not None:
                update_data['is_active'] = user_data.is_active
            if user_data.role is not None:
                update_data['role'] = user_data.role
            
            if not update_data:
                logger.debug(f"No updates provided for user {user_id}")
                return user
            
            # Update user
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            # Refresh and return updated user
            await self.db.refresh(user)
            
            logger.info(f"Successfully updated user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            await self.db.rollback()
            raise

    async def delete_user(self, user_id: str) -> bool:
        """
        Soft delete a user (mark as inactive).
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            True if user was deleted, False if not found
            
        Raises:
            Exception: If user deletion fails
        """
        logger.info(f"Soft deleting user {user_id}")
        
        try:
            # Check if user exists
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            # Soft delete by marking as inactive
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_active=False)
            )
            
            await self.db.commit()
            
            logger.info(f"Successfully soft deleted user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            await self.db.rollback()
            raise

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        logger.debug(f"Authenticating user with email: {email}")
        
        user = await self.get_user_by_email(email)
        if not user:
            logger.debug(f"User with email {email} not found")
            return None
        
        if not user.is_active:
            logger.debug(f"User {user.id} is inactive")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.debug(f"Invalid password for user {user.id}")
            return None
        
        logger.info(f"Successfully authenticated user {user.id}")
        return user

    async def update_user_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: The user's unique identifier
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was updated, False otherwise
            
        Raises:
            Exception: If password update fails
        """
        logger.info(f"Updating password for user {user_id}")
        
        try:
            # Get user
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for password update")
                return False
            
            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                logger.warning(f"Invalid current password for user {user_id}")
                return False
            
            # Hash new password
            new_hashed_password = get_password_hash(new_password)
            
            # Update password
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(hashed_password=new_hashed_password)
            )
            
            await self.db.commit()
            
            logger.info(f"Successfully updated password for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update password for user {user_id}: {e}")
            await self.db.rollback()
            raise

    async def get_active_users_count(self) -> int:
        """
        Get the count of active users.
        
        Returns:
            Number of active users
        """
        result = await self.db.execute(
            select(User.id).where(User.is_active == True)
        )
        count = len(result.scalars().all())
        
        logger.debug(f"Active users count: {count}")
        return count
