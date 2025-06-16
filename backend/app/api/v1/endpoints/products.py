"""Product management endpoints."""

from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.schemas.auth import UserResponse
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services.product import product_service, ProductService

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    category_id: UUID = Query(None),
    status: str = Query(None),
) -> Any:
    """List products with filtering and pagination."""
    products, total = await product_service.get_products(
        session=session,
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        status=status,
    )
    return ProductListResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new product.
    """
    product_service = ProductService(db)
    product = await product_service.create_product(product_data)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get product by ID.
    """
    product_service = ProductService(db)
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update product.
    """
    product_service = ProductService(db)
    product = await product_service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete product.
    """
    product_service = ProductService(db)
    product = await product_service.delete_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )


@router.get("/search/", response_model=ProductListResponse)
async def search_products(
    *,
    session: AsyncSession = Depends(get_session),
    q: str = Query(..., min_length=3),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """Advanced product search."""
    products, total = await product_service.search_products(
        session=session,
        query=q,
        skip=skip,
        limit=limit,
    )
    return ProductListResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/bulk/", response_model=List[ProductResponse])
async def bulk_create_products(
    *,
    session: AsyncSession = Depends(get_session),
    products_in: List[ProductCreate],
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Bulk create products."""
    products = await product_service.bulk_create_products(
        session=session, products_in=products_in
    )
    return [ProductResponse.from_orm(product) for product in products]


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get product by SKU.
    """
    product_service = ProductService(db)
    product = await product_service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product