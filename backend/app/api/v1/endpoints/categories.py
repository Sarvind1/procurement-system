"""Product categories API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import CategoryService

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[CategoryRead])
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    parent_id: Optional[str] = Query(None, description="Filter by parent category ID"),
    active_only: bool = Query(True, description="Show only active categories"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CategoryRead]:
    """
    Retrieve a list of product categories.
    
    This endpoint supports filtering by parent category and active status.
    All authenticated users can view categories.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        parent_id: Filter categories by parent category ID
        active_only: Whether to show only active categories
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        List of category records
    """
    logger.info(f"User {current_user.id} requesting category list")
    
    category_service = CategoryService(db)
    categories = await category_service.get_categories(
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        active_only=active_only
    )
    
    logger.info(f"Retrieved {len(categories)} categories")
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """
    Get a specific category by ID.
    
    Args:
        category_id: The ID of the category to retrieve
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Category data
        
    Raises:
        HTTPException: If category not found
    """
    logger.info(f"User {current_user.id} requesting category {category_id}")
    
    category_service = CategoryService(db)
    category = await category_service.get_category_by_id(category_id)
    
    if not category:
        logger.warning(f"Category {category_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    logger.info(f"Retrieved category {category_id}")
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """
    Create a new product category.
    
    Only users with admin or manager roles can create categories.
    
    Args:
        category_data: Category creation data
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Created category data
        
    Raises:
        HTTPException: If user lacks permission or category name exists
    """
    logger.info(f"User {current_user.id} creating new category: {category_data.name}")
    
    # Check if user has permission to create categories
    if not (current_user.is_admin or current_user.role in ["manager", "procurement_manager"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create categories"
        )
    
    category_service = CategoryService(db)
    
    # Check if category name already exists in the same parent
    existing_category = await category_service.get_category_by_name(
        category_data.name, 
        parent_id=category_data.parent_id
    )
    if existing_category:
        logger.warning(f"Attempt to create category with existing name: {category_data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists in this parent category"
        )
    
    # Validate parent category if provided
    if category_data.parent_id:
        parent_category = await category_service.get_category_by_id(category_data.parent_id)
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    category = await category_service.create_category(category_data)
    logger.info(f"Created new category: {category.id}")
    
    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """
    Update a category's information.
    
    Only users with admin or manager roles can update categories.
    
    Args:
        category_id: The ID of the category to update
        category_data: Updated category data
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Updated category data
        
    Raises:
        HTTPException: If category not found or access denied
    """
    logger.info(f"User {current_user.id} updating category {category_id}")
    
    # Check if user has permission to update categories
    if not (current_user.is_admin or current_user.role in ["manager", "procurement_manager"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update categories"
        )
    
    category_service = CategoryService(db)
    category = await category_service.get_category_by_id(category_id)
    
    if not category:
        logger.warning(f"Attempt to update non-existent category: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if new name conflicts with existing categories
    if category_data.name and category_data.name != category.name:
        existing_category = await category_service.get_category_by_name(
            category_data.name,
            parent_id=category_data.parent_id or category.parent_id
        )
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists in this parent category"
            )
    
    # Validate parent category if being changed
    if category_data.parent_id and category_data.parent_id != category.parent_id:
        parent_category = await category_service.get_category_by_id(category_data.parent_id)
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
        
        # Prevent circular references
        if await category_service.would_create_circular_reference(category_id, category_data.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set parent category: would create circular reference"
            )
    
    updated_category = await category_service.update_category(category_id, category_data)
    logger.info(f"Updated category: {category_id}")
    
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    force: bool = Query(False, description="Force delete even if category has children or products"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a category (soft delete).
    
    Only administrators can delete categories. Categories with children or
    associated products cannot be deleted unless force is True.
    
    Args:
        category_id: The ID of the category to delete
        force: Whether to force delete despite dependencies
        db: Database session dependency
        current_user: Currently authenticated user
        
    Raises:
        HTTPException: If category not found, access denied, or has dependencies
    """
    logger.info(f"User {current_user.id} attempting to delete category {category_id}")
    
    # Check if user has permission to delete categories
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete categories"
        )
    
    category_service = CategoryService(db)
    category = await category_service.get_category_by_id(category_id)
    
    if not category:
        logger.warning(f"Attempt to delete non-existent category: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check for dependencies if not forcing
    if not force:
        has_children = await category_service.has_child_categories(category_id)
        has_products = await category_service.has_associated_products(category_id)
        
        if has_children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with child categories. Use force=true to override."
            )
        
        if has_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with associated products. Use force=true to override."
            )
    
    await category_service.delete_category(category_id, force=force)
    logger.info(f"Deleted category: {category_id}")


@router.get("/{category_id}/children", response_model=List[CategoryRead])
async def get_category_children(
    category_id: str,
    active_only: bool = Query(True, description="Show only active categories"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CategoryRead]:
    """
    Get all child categories of a specific category.
    
    Args:
        category_id: The ID of the parent category
        active_only: Whether to show only active categories
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        List of child categories
        
    Raises:
        HTTPException: If parent category not found
    """
    logger.info(f"User {current_user.id} requesting children of category {category_id}")
    
    category_service = CategoryService(db)
    
    # Verify parent category exists
    category = await category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found"
        )
    
    children = await category_service.get_child_categories(category_id, active_only=active_only)
    logger.info(f"Retrieved {len(children)} child categories for {category_id}")
    
    return children


@router.get("/{category_id}/tree", response_model=CategoryRead)
async def get_category_tree(
    category_id: str,
    max_depth: int = Query(5, ge=1, le=10, description="Maximum depth to retrieve"),
    active_only: bool = Query(True, description="Show only active categories"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    """
    Get a category and its entire subtree.
    
    This endpoint returns a category with all its descendants in a tree structure.
    
    Args:
        category_id: The ID of the root category
        max_depth: Maximum depth of the tree to retrieve
        active_only: Whether to include only active categories
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        Category tree with nested children
        
    Raises:
        HTTPException: If category not found
    """
    logger.info(f"User {current_user.id} requesting tree for category {category_id}")
    
    category_service = CategoryService(db)
    category_tree = await category_service.get_category_tree(
        category_id,
        max_depth=max_depth,
        active_only=active_only
    )
    
    if not category_tree:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    logger.info(f"Retrieved category tree for {category_id}")
    return category_tree


@router.get("/", response_model=List[CategoryRead])
async def get_root_categories(
    active_only: bool = Query(True, description="Show only active categories"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CategoryRead]:
    """
    Get all root categories (categories without parent).
    
    Args:
        active_only: Whether to show only active categories
        db: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        List of root categories
    """
    logger.info(f"User {current_user.id} requesting root categories")
    
    category_service = CategoryService(db)
    root_categories = await category_service.get_root_categories(active_only=active_only)
    
    logger.info(f"Retrieved {len(root_categories)} root categories")
    return root_categories
