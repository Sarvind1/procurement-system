"""Purchase Order management endpoints."""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.database import get_session
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderListResponse,
    PurchaseOrderApproval,
)
from app.services.purchase_order import purchase_order_service

router = APIRouter()


@router.get("/", response_model=PurchaseOrderListResponse)
async def list_purchase_orders(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    supplier_id: UUID = Query(None),
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """List purchase orders with filtering and pagination."""
    purchase_orders, total = await purchase_order_service.get_purchase_orders(
        session=session,
        skip=skip,
        limit=limit,
        status=status,
        supplier_id=supplier_id,
    )
    return PurchaseOrderListResponse(
        items=purchase_orders,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    *,
    session: AsyncSession = Depends(get_session),
    po_in: PurchaseOrderCreate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Create new purchase order."""
    purchase_order = await purchase_order_service.create_purchase_order(
        session=session, po_in=po_in, created_by=current_user["id"]
    )
    return PurchaseOrderResponse.from_orm(purchase_order)


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    *,
    session: AsyncSession = Depends(get_session),
    po_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get purchase order by ID."""
    purchase_order = await purchase_order_service.get_purchase_order(
        session=session, po_id=po_id
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )
    return PurchaseOrderResponse.from_orm(purchase_order)


@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    *,
    session: AsyncSession = Depends(get_session),
    po_id: UUID,
    po_in: PurchaseOrderUpdate,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Update purchase order."""
    purchase_order = await purchase_order_service.get_purchase_order(
        session=session, po_id=po_id
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )
    
    # Check if user can update this PO
    if purchase_order.status not in ["draft", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update purchase order in current status",
        )
    
    purchase_order = await purchase_order_service.update_purchase_order(
        session=session, purchase_order=purchase_order, po_in=po_in
    )
    return PurchaseOrderResponse.from_orm(purchase_order)


@router.post("/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    *,
    session: AsyncSession = Depends(get_session),
    po_id: UUID,
    approval: PurchaseOrderApproval,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Approve or reject purchase order."""
    purchase_order = await purchase_order_service.get_purchase_order(
        session=session, po_id=po_id
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )
    
    purchase_order = await purchase_order_service.approve_purchase_order(
        session=session,
        purchase_order=purchase_order,
        approval=approval,
        approved_by=current_user["id"],
    )
    return PurchaseOrderResponse.from_orm(purchase_order)


@router.post("/{po_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_purchase_order(
    *,
    session: AsyncSession = Depends(get_session),
    po_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Cancel purchase order."""
    purchase_order = await purchase_order_service.get_purchase_order(
        session=session, po_id=po_id
    )
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )
    
    purchase_order = await purchase_order_service.cancel_purchase_order(
        session=session, purchase_order=purchase_order
    )
    return PurchaseOrderResponse.from_orm(purchase_order)


@router.get("/{po_id}/history", response_model=List[dict])
async def get_purchase_order_history(
    *,
    session: AsyncSession = Depends(get_session),
    po_id: UUID,
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """Get purchase order history."""
    history = await purchase_order_service.get_purchase_order_history(
        session=session, po_id=po_id
    )
    return history