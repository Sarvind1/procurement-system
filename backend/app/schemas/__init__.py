"""Schemas package with all Pydantic models for API serialization."""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
    UserInDB,
    UserPasswordUpdate
)
from app.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryWithChildren,
    CategoryTree,
    CategorySummary
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserRead",
    "UserUpdate",
    "UserInDB",
    "UserPasswordUpdate",
    # Category schemas
    "CategoryBase",
    "CategoryCreate",
    "CategoryRead", 
    "CategoryUpdate",
    "CategoryWithChildren",
    "CategoryTree",
    "CategorySummary",
]
