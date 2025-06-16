"""Category model for hierarchical product categorization."""

from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import false

from app.models.base import Base


class Category(Base):
    """
    Product category model for hierarchical organization.
    
    This model supports unlimited depth hierarchical categories with
    proper path tracking and level calculation.
    """
    
    __tablename__ = "categories"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Category name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Category description"
    )
    
    # Hierarchy fields
    parent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="Parent category ID for hierarchy"
    )
    
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Hierarchy level (0 for root categories)"
    )
    
    path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="Full path from root to this category"
    )
    
    # Status and metadata
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=false(),
        index=True,
        comment="Whether the category is active"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When the category was created"
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        comment="When the category was last updated"
    )
    
    # Computed properties for API responses
    @property
    def product_count(self) -> int:
        """Get the number of products in this category."""
        # TODO: Implement when Product model is available
        return 0
    
    @property
    def children_count(self) -> int:
        """Get the number of direct child categories."""
        # This will be computed in queries when needed
        return 0
    
    def __repr__(self) -> str:
        """String representation of the category."""
        return f"<Category(id={self.id}, name='{self.name}', level={self.level})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.path}"
    
    # Validation methods
    def is_root_category(self) -> bool:
        """Check if this is a root category (no parent)."""
        return self.parent_id is None
    
    def is_leaf_category(self) -> bool:
        """Check if this is a leaf category (no children)."""
        return self.children_count == 0
    
    def get_depth(self) -> int:
        """Get the depth of this category in the hierarchy."""
        return self.level
    
    def get_parent_path(self) -> str:
        """Get the path of the parent category."""
        if self.is_root_category():
            return ""
        
        path_parts = self.path.split(" / ")
        if len(path_parts) > 1:
            return " / ".join(path_parts[:-1])
        return ""
    
    def get_category_breadcrumbs(self) -> List[str]:
        """Get breadcrumb list from root to this category."""
        return self.path.split(" / ")
    
    def generate_path(self, parent_path: Optional[str] = None) -> str:
        """Generate the full path for this category."""
        if parent_path:
            return f"{parent_path} / {self.name}"
        return self.name
    
    def update_path(self, parent_path: Optional[str] = None) -> None:
        """Update the path based on parent path."""
        self.path = self.generate_path(parent_path)
        
    def calculate_level(self, parent_level: Optional[int] = None) -> int:
        """Calculate the level based on parent level."""
        if parent_level is not None:
            return parent_level + 1
        return 0 if self.is_root_category() else 1
