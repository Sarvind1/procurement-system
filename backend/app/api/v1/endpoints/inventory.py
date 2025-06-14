"""Inventory management endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.schemas.inventory import (
    InventoryResponse,
    InventoryListResponse,
    InventoryAdjustment,
    InventoryMovementResponse,
    StockAnalytics,
)
from app.services.inventory import inventory_service

router = APIRouter()


@router.get("/", response_model=InventoryListResponse)
async def list_inventory(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    location_id: UUID = Query(None),
    low_stock: bool = Query(False),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """List inventory items with filtering and pagination."""
    inventory_items, total = await inventory_service.get_inventory_items(
        session=session,
        skip=skip,
        limit=limit,
        location_id=location_id,
        low_stock=low_stock,
    )
    return InventoryListResponse(
        items=inventory_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/adjust", response_model=InventoryResponse)
async def adjust_inventory(
    *,
    session: AsyncSession = Depends(get_session),
    adjustment: InventoryAdjustment,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Adjust inventory levels."""
    inventory_item = await inventory_service.adjust_inventory(
        session=session,
        adjustment=adjustment,
        adjusted_by=current_user["id"],
    )
    return InventoryResponse.from_orm(inventory_item)


@router.get("/movements", response_model=List[InventoryMovementResponse])
async def get_inventory_movements(
    *,
    session: AsyncSession = Depends(get_session),
    product_id: UUID = Query(None),
    location_id: UUID = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get inventory movement history."""
    movements = await inventory_service.get_inventory_movements(
        session=session,
        product_id=product_id,
        location_id=location_id,
        skip=skip,
        limit=limit,
    )
    return [InventoryMovementResponse.from_orm(movement) for movement in movements]


@router.post("/count", response_model=InventoryResponse)
async def physical_count(
    *,
    session: AsyncSession = Depends(get_session),
    inventory_id: UUID,
    counted_quantity: int,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Record physical inventory count."""
    inventory_item = await inventory_service.physical_count(
        session=session,
        inventory_id=inventory_id,
        counted_quantity=counted_quantity,
        counted_by=current_user["id"],
    )
    return InventoryResponse.from_orm(inventory_item)


@router.get("/low-stock", response_model=InventoryListResponse)
async def get_low_stock_items(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get items with low stock levels."""
    inventory_items, total = await inventory_service.get_low_stock_items(
        session=session,
        skip=skip,
        limit=limit,
    )
    return InventoryListResponse(
        items=inventory_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/analytics", response_model=StockAnalytics)
async def get_inventory_analytics(
    *,
    session: AsyncSession = Depends(get_session),
    location_id: UUID = Query(None),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get inventory analytics and insights."""
    analytics = await inventory_service.get_inventory_analytics(
        session=session,
        location_id=location_id,
    )
    return analytics