"""User model for authentication and authorization."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import false

from app.models.base import Base


class UserRole(str, Enum):
    """User role enumeration for role-based access control."""
    ADMIN = "admin"
    PROCUREMENT_MANAGER = "procurement_manager"
    INVENTORY_MANAGER = "inventory_manager"
    FINANCE_APPROVER = "finance_approver"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and authorization.
    
    This model handles user accounts, roles, and basic profile information.
    Passwords are stored as bcrypt hashes for security.
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User's email address (used for login)"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password"
    )
    
    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User's full name"
    )
    
    # Authorization fields
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UserRole.VIEWER.value,
        comment="User's role for access control"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=false(),
        index=True,
        comment="Whether the user account is active"
    )
    
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
        comment="Whether the user has admin privileges"
    )
    
    # Activity tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the user last logged in"
    )
    
    # Helper properties
    @property
    def is_superuser(self) -> bool:
        """Check if user is a superuser (alias for is_admin)."""
        return self.is_admin
    
    @property
    def role_enum(self) -> UserRole:
        """Get the user's role as an enum."""
        try:
            return UserRole(self.role)
        except ValueError:
            return UserRole.VIEWER
    
    # Utility methods
    def has_role(self, required_role: UserRole) -> bool:
        """
        Check if user has the required role or higher privileges.
        
        Args:
            required_role: The minimum role required
            
        Returns:
            bool: True if user has sufficient privileges
        """
        if self.is_admin:
            return True
        
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.FINANCE_APPROVER: 2,
            UserRole.INVENTORY_MANAGER: 3,
            UserRole.PROCUREMENT_MANAGER: 4,
            UserRole.ADMIN: 5
        }
        
        user_level = role_hierarchy.get(self.role_enum, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.is_admin
    
    def can_manage_products(self) -> bool:
        """Check if user can manage products."""
        return self.is_admin or self.role in [
            UserRole.PROCUREMENT_MANAGER.value,
            UserRole.INVENTORY_MANAGER.value
        ]
    
    def can_manage_purchase_orders(self) -> bool:
        """Check if user can manage purchase orders."""
        return self.is_admin or self.role in [
            UserRole.PROCUREMENT_MANAGER.value,
            UserRole.FINANCE_APPROVER.value
        ]
    
    def can_manage_inventory(self) -> bool:
        """Check if user can manage inventory."""
        return self.is_admin or self.role in [
            UserRole.INVENTORY_MANAGER.value,
            UserRole.PROCUREMENT_MANAGER.value
        ]
    
    def can_view_reports(self) -> bool:
        """Check if user can view reports."""
        return self.is_admin or self.role != UserRole.VIEWER.value
    
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password is correct
        """
        from app.core.password import verify_password
        return verify_password(password, self.hashed_password)
    
    def set_password(self, password: str) -> None:
        """
        Set a new password for the user.
        
        Args:
            password: Plain text password to hash and store
        """
        from app.core.password import get_password_hash
        self.hashed_password = get_password_hash(password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to now."""
        self.last_login = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.full_name or self.email} ({self.role})"
