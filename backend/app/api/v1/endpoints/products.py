"""Product management endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services.product import product_service

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
    *,
    session: AsyncSession = Depends(get_session),
    product_in: ProductCreate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Create new product."""
    product = await product_service.create_product(
        session=session, product_in=product_in
    )
    return ProductResponse.from_orm(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: UUID,
) -> Any:
    """Get product by ID."""
    product = await product_service.get_product(session=session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return ProductResponse.from_orm(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: UUID,
    product_in: ProductUpdate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Update product."""
    product = await product_service.get_product(session=session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    product = await product_service.update_product(
        session=session, product=product, product_in=product_in
    )
    return ProductResponse.from_orm(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> None:
    """Delete product (soft delete)."""
    product = await product_service.get_product(session=session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    await product_service.delete_product(session=session, product=product)


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