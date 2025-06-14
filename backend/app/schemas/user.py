from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str 