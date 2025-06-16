"""User schemas for API serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(True, description="Whether the user account is active")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    role: Optional[str] = Field("user", description="User's role in the system")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, description="Updated full name")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    role: Optional[str] = Field(None, description="Updated user role")


class UserRead(UserBase):
    """Schema for reading user data (response)."""
    id: str = Field(..., description="User's unique identifier")
    role: str = Field(..., description="User's role in the system")
    is_admin: bool = Field(False, description="Whether the user has admin privileges")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: Optional[datetime] = Field(None, description="When the user account was last updated")

    class Config:
        from_attributes = True


class UserInDB(UserRead):
    """User schema as stored in database (includes password hash)."""
    hashed_password: str = Field(..., description="Hashed password")


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")

    def validate_passwords_match(self) -> 'UserPasswordUpdate':
        """Validate that new password and confirmation match."""
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
