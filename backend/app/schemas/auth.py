"""Authentication schemas for login, token management, and user registration."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class LoginResponse(BaseModel):
    """Schema for successful login response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: Optional[str] = Field("viewer", description="User's initial role")


class RegisterResponse(BaseModel):
    """Schema for successful registration response."""
    message: str = Field(..., description="Registration success message")
    user: dict = Field(..., description="Created user information")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetResponse(BaseModel):
    """Schema for password reset response."""
    message: str = Field(..., description="Password reset message")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    
    def validate_passwords_match(self) -> 'PasswordResetConfirm':
        """Validate that new password and confirmation match."""
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class TokenData(BaseModel):
    """Schema for JWT token data."""
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    type: str = Field(..., description="Token type (access or refresh)")


class AuthUser(BaseModel):
    """Schema for authenticated user information."""
    id: str = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: str = Field(..., description="User's role")
    is_active: bool = Field(..., description="Whether the user is active")
    is_admin: bool = Field(..., description="Whether the user has admin privileges")

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    
    def validate_passwords_match(self) -> 'ChangePasswordRequest':
        """Validate that new password and confirmation match."""
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class ChangePasswordResponse(BaseModel):
    """Schema for password change response."""
    message: str = Field(..., description="Password change success message")


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    message: str = Field(..., description="Logout success message")


class MeResponse(BaseModel):
    """Schema for current user information response."""
    user: AuthUser = Field(..., description="Current user information")


class UpdateProfileRequest(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, description="Updated full name")
    email: Optional[EmailStr] = Field(None, description="Updated email address")


class UpdateProfileResponse(BaseModel):
    """Schema for profile update response."""
    message: str = Field(..., description="Profile update success message")
    user: AuthUser = Field(..., description="Updated user information")
