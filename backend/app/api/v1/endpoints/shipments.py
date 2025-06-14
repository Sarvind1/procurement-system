"""Shipment tracking endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentListResponse,
    ShipmentTracking,
)
from app.services.shipment import shipment_service

router = APIRouter()


@router.get("/", response_model=ShipmentListResponse)
async def list_shipments(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    purchase_order_id: UUID = Query(None),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """List shipments with filtering and pagination."""
    shipments, total = await shipment_service.get_shipments(
        session=session,
        skip=skip,
        limit=limit,
        status=status,
        purchase_order_id=purchase_order_id,
    )
    return ShipmentListResponse(
        items=shipments,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    *,
    session: AsyncSession = Depends(get_session),
    shipment_in: ShipmentCreate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Create new shipment."""
    shipment = await shipment_service.create_shipment(
        session=session, shipment_in=shipment_in
    )
    return ShipmentResponse.from_orm(shipment)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    *,
    session: AsyncSession = Depends(get_session),
    shipment_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get shipment by ID."""
    shipment = await shipment_service.get_shipment(
        session=session, shipment_id=shipment_id
    )
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )
    return ShipmentResponse.from_orm(shipment)


@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    *,
    session: AsyncSession = Depends(get_session),
    shipment_id: UUID,
    shipment_in: ShipmentUpdate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Update shipment."""
    shipment = await shipment_service.get_shipment(
        session=session, shipment_id=shipment_id
    )
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )
    
    shipment = await shipment_service.update_shipment(
        session=session, shipment=shipment, shipment_in=shipment_in
    )
    return ShipmentResponse.from_orm(shipment)


@router.get("/{shipment_id}/tracking", response_model=List[ShipmentTracking])
async def get_shipment_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    shipment_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get shipment tracking history."""
    tracking = await shipment_service.get_shipment_tracking(
        session=session, shipment_id=shipment_id
    )
    return tracking


@router.post("/{shipment_id}/track", response_model=ShipmentResponse)
async def update_tracking(
    *,
    session: AsyncSession = Depends(get_session),
    shipment_id: UUID,
    tracking: ShipmentTracking,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Update shipment tracking information."""
    shipment = await shipment_service.update_tracking(
        session=session, shipment_id=shipment_id, tracking=tracking
    )
    return ShipmentResponse.from_orm(shipment)