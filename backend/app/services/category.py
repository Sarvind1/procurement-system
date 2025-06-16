"""Category service for business logic operations."""

from typing import List, Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

# Initialize logger
logger = get_logger(__name__)


class CategoryService:
    """Service class for category-related business logic."""

    def __init__(self, db: AsyncSession):
        """
        Initialize category service with database session.
        
        Args:
            db: Database session for operations
        """
        self.db = db

    async def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        parent_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[Category]:
        """
        Get a list of categories with filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            parent_id: Filter by parent category ID
            active_only: Whether to include only active categories
            
        Returns:
            List of category objects
        """
        logger.debug(f"Fetching categories with skip={skip}, limit={limit}, parent_id={parent_id}")
        
        query = select(Category)
        
        # Apply filters
        filters = []
        if active_only:
            filters.append(Category.is_active == True)
        if parent_id is not None:
            filters.append(Category.parent_id == parent_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Category.name)
        
        result = await self.db.execute(query)
        categories = result.scalars().all()
        
        logger.info(f"Retrieved {len(categories)} categories")
        return list(categories)

    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """
        Get a category by its ID.
        
        Args:
            category_id: The category's unique identifier
            
        Returns:
            Category object if found, None otherwise
        """
        logger.debug(f"Fetching category by ID: {category_id}")
        
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if category:
            logger.debug(f"Found category {category_id}")
        else:
            logger.debug(f"Category {category_id} not found")
            
        return category

    async def get_category_by_name(self, name: str, parent_id: Optional[str] = None) -> Optional[Category]:
        """
        Get a category by its name within a parent category.
        
        Args:
            name: The category name
            parent_id: Parent category ID (None for root level)
            
        Returns:
            Category object if found, None otherwise
        """
        logger.debug(f"Fetching category by name: {name}, parent_id: {parent_id}")
        
        query = select(Category).where(Category.name == name)
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        else:
            query = query.where(Category.parent_id.is_(None))
        
        result = await self.db.execute(query)
        category = result.scalar_one_or_none()
        
        if category:
            logger.debug(f"Found category with name {name}")
        else:
            logger.debug(f"Category with name {name} not found")
            
        return category

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """
        Create a new category.
        
        Args:
            category_data: Category creation data
            
        Returns:
            Created category object
            
        Raises:
            Exception: If category creation fails
        """
        logger.info(f"Creating new category: {category_data.name}")
        
        try:
            # Calculate level and path
            level = 0
            path = category_data.name
            
            if category_data.parent_id:
                parent = await self.get_category_by_id(category_data.parent_id)
                if parent:
                    level = parent.level + 1
                    path = f"{parent.path} / {category_data.name}"
            
            # Create category object
            db_category = Category(
                name=category_data.name,
                description=category_data.description,
                parent_id=category_data.parent_id,
                level=level,
                path=path,
                is_active=category_data.is_active
            )
            
            # Add to database
            self.db.add(db_category)
            await self.db.commit()
            await self.db.refresh(db_category)
            
            logger.info(f"Successfully created category {db_category.id}")
            return db_category
            
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
            await self.db.rollback()
            raise

    async def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[Category]:
        """
        Update an existing category.
        
        Args:
            category_id: The category's unique identifier
            category_data: Updated category data
            
        Returns:
            Updated category object if found and updated, None otherwise
            
        Raises:
            Exception: If category update fails
        """
        logger.info(f"Updating category {category_id}")
        
        try:
            # Get category
            category = await self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"Category {category_id} not found for update")
                return None
            
            # Build update data
            update_data = {}
            if category_data.name is not None:
                update_data['name'] = category_data.name
            if category_data.description is not None:
                update_data['description'] = category_data.description
            if category_data.is_active is not None:
                update_data['is_active'] = category_data.is_active
            if category_data.parent_id is not None:
                update_data['parent_id'] = category_data.parent_id
            
            # Update path and level if parent or name changed
            if category_data.parent_id is not None or category_data.name is not None:
                new_name = category_data.name or category.name
                level = 0
                path = new_name
                
                if category_data.parent_id:
                    parent = await self.get_category_by_id(category_data.parent_id)
                    if parent:
                        level = parent.level + 1
                        path = f"{parent.path} / {new_name}"
                
                update_data['level'] = level
                update_data['path'] = path
            
            if not update_data:
                logger.debug(f"No updates provided for category {category_id}")
                return category
            
            # Update category
            await self.db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            # Refresh and return updated category
            await self.db.refresh(category)
            
            logger.info(f"Successfully updated category {category_id}")
            return category
            
        except Exception as e:
            logger.error(f"Failed to update category {category_id}: {e}")
            await self.db.rollback()
            raise

    async def delete_category(self, category_id: str, force: bool = False) -> bool:
        """
        Delete a category (soft delete).
        
        Args:
            category_id: The category's unique identifier
            force: Whether to force delete despite dependencies
            
        Returns:
            True if category was deleted, False if not found
            
        Raises:
            Exception: If category deletion fails
        """
        logger.info(f"Deleting category {category_id}, force={force}")
        
        try:
            # Check if category exists
            category = await self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"Category {category_id} not found for deletion")
                return False
            
            if force:
                # Force delete: deactivate all children and associated products
                await self._deactivate_category_tree(category_id)
            
            # Soft delete by marking as inactive
            await self.db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(is_active=False)
            )
            
            await self.db.commit()
            
            logger.info(f"Successfully deleted category {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            await self.db.rollback()
            raise

    async def get_child_categories(self, parent_id: str, active_only: bool = True) -> List[Category]:
        """
        Get all direct child categories of a parent category.
        
        Args:
            parent_id: Parent category ID
            active_only: Whether to include only active categories
            
        Returns:
            List of child categories
        """
        logger.debug(f"Fetching child categories for parent {parent_id}")
        
        query = select(Category).where(Category.parent_id == parent_id)
        
        if active_only:
            query = query.where(Category.is_active == True)
        
        query = query.order_by(Category.name)
        
        result = await self.db.execute(query)
        children = result.scalars().all()
        
        logger.debug(f"Found {len(children)} child categories")
        return list(children)

    async def get_category_tree(
        self, 
        category_id: str, 
        max_depth: int = 5, 
        active_only: bool = True
    ) -> Optional[Category]:
        """
        Get a category with its complete subtree.
        
        Args:
            category_id: Root category ID
            max_depth: Maximum depth to retrieve
            active_only: Whether to include only active categories
            
        Returns:
            Category with nested children
        """
        logger.debug(f"Building category tree for {category_id}, max_depth={max_depth}")
        
        # Get root category
        category = await self.get_category_by_id(category_id)
        if not category:
            return None
        
        # Build tree recursively
        await self._build_category_tree(category, max_depth, active_only)
        
        return category

    async def get_root_categories(self, active_only: bool = True) -> List[Category]:
        """
        Get all root categories (categories without parent).
        
        Args:
            active_only: Whether to include only active categories
            
        Returns:
            List of root categories
        """
        logger.debug("Fetching root categories")
        
        query = select(Category).where(Category.parent_id.is_(None))
        
        if active_only:
            query = query.where(Category.is_active == True)
        
        query = query.order_by(Category.name)
        
        result = await self.db.execute(query)
        categories = result.scalars().all()
        
        logger.debug(f"Found {len(categories)} root categories")
        return list(categories)

    async def has_child_categories(self, category_id: str) -> bool:
        """
        Check if a category has child categories.
        
        Args:
            category_id: Category ID to check
            
        Returns:
            True if category has children, False otherwise
        """
        result = await self.db.execute(
            select(func.count(Category.id)).where(Category.parent_id == category_id)
        )
        count = result.scalar()
        return count > 0

    async def has_associated_products(self, category_id: str) -> bool:
        """
        Check if a category has associated products.
        
        Args:
            category_id: Category ID to check
            
        Returns:
            True if category has products, False otherwise
        """
        # TODO: Implement when Product model is available
        # For now, return False
        return False

    async def would_create_circular_reference(self, category_id: str, new_parent_id: str) -> bool:
        """
        Check if setting a new parent would create a circular reference.
        
        Args:
            category_id: Category being moved
            new_parent_id: Proposed new parent ID
            
        Returns:
            True if it would create a circular reference, False otherwise
        """
        logger.debug(f"Checking circular reference: category={category_id}, new_parent={new_parent_id}")
        
        # Traverse up the parent chain from new_parent_id
        current_id = new_parent_id
        visited = set()
        
        while current_id and current_id not in visited:
            if current_id == category_id:
                logger.warning(f"Circular reference detected: {category_id} -> {new_parent_id}")
                return True
            
            visited.add(current_id)
            
            # Get parent of current category
            result = await self.db.execute(
                select(Category.parent_id).where(Category.id == current_id)
            )
            parent_id = result.scalar()
            current_id = parent_id
        
        return False

    async def _build_category_tree(
        self, 
        category: Category, 
        max_depth: int, 
        active_only: bool,
        current_depth: int = 0
    ) -> None:
        """
        Recursively build category tree with children.
        
        Args:
            category: Category to build tree for
            max_depth: Maximum depth to traverse
            active_only: Whether to include only active categories
            current_depth: Current recursion depth
        """
        if current_depth >= max_depth:
            return
        
        children = await self.get_child_categories(category.id, active_only)
        category.children = children
        
        # Recursively build subtrees
        for child in children:
            await self._build_category_tree(child, max_depth, active_only, current_depth + 1)

    async def _deactivate_category_tree(self, category_id: str) -> None:
        """
        Recursively deactivate a category and all its descendants.
        
        Args:
            category_id: Root category ID to deactivate
        """
        logger.debug(f"Deactivating category tree starting from {category_id}")
        
        # Get all children
        children = await self.get_child_categories(category_id, active_only=False)
        
        # Recursively deactivate children
        for child in children:
            await self._deactivate_category_tree(child.id)
        
        # Deactivate this category
        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(is_active=False)
        )
