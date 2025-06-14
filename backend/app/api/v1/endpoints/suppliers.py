"""Supplier management endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
    SupplierPerformance,
)
from app.services.supplier import supplier_service

router = APIRouter()


@router.get("/", response_model=SupplierListResponse)
async def list_suppliers(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    status: str = Query(None),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """List suppliers with filtering and pagination."""
    suppliers, total = await supplier_service.get_suppliers(
        session=session,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
    )
    return SupplierListResponse(
        items=suppliers,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    *,
    session: AsyncSession = Depends(get_session),
    supplier_in: SupplierCreate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Create new supplier."""
    supplier = await supplier_service.create_supplier(
        session=session, supplier_in=supplier_in
    )
    return SupplierResponse.from_orm(supplier)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    *,
    session: AsyncSession = Depends(get_session),
    supplier_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get supplier by ID."""
    supplier = await supplier_service.get_supplier(
        session=session, supplier_id=supplier_id
    )
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    return SupplierResponse.from_orm(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    *,
    session: AsyncSession = Depends(get_session),
    supplier_id: UUID,
    supplier_in: SupplierUpdate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Update supplier."""
    supplier = await supplier_service.get_supplier(
        session=session, supplier_id=supplier_id
    )
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    supplier = await supplier_service.update_supplier(
        session=session, supplier=supplier, supplier_in=supplier_in
    )
    return SupplierResponse.from_orm(supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    *,
    session: AsyncSession = Depends(get_session),
    supplier_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> None:
    """Delete supplier (soft delete)."""
    supplier = await supplier_service.get_supplier(
        session=session, supplier_id=supplier_id
    )
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    await supplier_service.delete_supplier(session=session, supplier=supplier)


@router.get("/{supplier_id}/performance", response_model=SupplierPerformance)
async def get_supplier_performance(
    *,
    session: AsyncSession = Depends(get_session),
    supplier_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get supplier performance metrics."""
    performance = await supplier_service.get_supplier_performance(
        session=session, supplier_id=supplier_id
    )
    return performance