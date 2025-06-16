"""Category schemas for API serialization."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    is_active: bool = Field(True, description="Whether the category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    parent_id: Optional[str] = Field(None, description="Parent category ID for hierarchical structure")


class CategoryUpdate(BaseModel):
    """Schema for updating category information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated category name")
    description: Optional[str] = Field(None, max_length=500, description="Updated category description")
    parent_id: Optional[str] = Field(None, description="Updated parent category ID")
    is_active: Optional[bool] = Field(None, description="Updated active status")


class CategoryRead(CategoryBase):
    """Schema for reading category data (response)."""
    id: str = Field(..., description="Category's unique identifier")
    parent_id: Optional[str] = Field(None, description="Parent category ID")
    level: int = Field(0, description="Hierarchy level (0 for root categories)")
    path: str = Field(..., description="Full path from root to this category")
    product_count: int = Field(0, description="Number of products in this category")
    children_count: int = Field(0, description="Number of direct child categories")
    created_at: datetime = Field(..., description="When the category was created")
    updated_at: Optional[datetime] = Field(None, description="When the category was last updated")

    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryRead):
    """Category schema with nested children for tree operations."""
    children: List['CategoryWithChildren'] = Field(default=[], description="Direct child categories")


class CategoryTree(CategoryRead):
    """Complete category tree structure."""
    children: List['CategoryTree'] = Field(default=[], description="All descendant categories")


class CategorySummary(BaseModel):
    """Minimal category information for references."""
    id: str = Field(..., description="Category's unique identifier")
    name: str = Field(..., description="Category name")
    path: str = Field(..., description="Full path from root to this category")

    class Config:
        from_attributes = True


# Update forward references
CategoryWithChildren.model_rebuild()
CategoryTree.model_rebuild()
