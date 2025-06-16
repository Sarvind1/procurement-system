from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderApproval
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderApproval as PurchaseOrderApprovalSchema
)

class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_purchase_order(
        self,
        purchase_order_data: PurchaseOrderCreate,
        created_by: int
    ) -> PurchaseOrder:
        """Create a new purchase order."""
        # Create the purchase order
        po_data = purchase_order_data.model_dump(exclude={"items"})
        purchase_order = PurchaseOrder(**po_data, created_by=created_by)
        self.db.add(purchase_order)
        await self.db.flush()

        # Create purchase order items
        for item_data in purchase_order_data.items:
            item = PurchaseOrderItem(
                **item_data.model_dump(),
                purchase_order_id=purchase_order.id
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(purchase_order)
        return purchase_order

    async def get_purchase_order(
        self,
        purchase_order_id: int
    ) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.approvals)
            )
            .where(PurchaseOrder.id == purchase_order_id)
        )
        return result.scalar_one_or_none()

    async def get_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        supplier_id: Optional[int] = None
    ) -> List[PurchaseOrder]:
        """Get a list of purchase orders with optional filtering."""
        query = select(PurchaseOrder).options(
            selectinload(PurchaseOrder.items),
            selectinload(PurchaseOrder.approvals)
        )
        
        if status:
            query = query.where(PurchaseOrder.status == status)
        if supplier_id:
            query = query.where(PurchaseOrder.supplier_id == supplier_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_purchase_order(
        self,
        purchase_order_id: int,
        purchase_order_data: PurchaseOrderUpdate
    ) -> Optional[PurchaseOrder]:
        """Update a purchase order."""
        await self.db.execute(
            update(PurchaseOrder)
            .where(PurchaseOrder.id == purchase_order_id)
            .values(**purchase_order_data.model_dump(exclude_unset=True))
        )
        await self.db.commit()
        return await self.get_purchase_order(purchase_order_id)

    async def delete_purchase_order(self, purchase_order_id: int) -> bool:
        """Delete a purchase order."""
        result = await self.db.execute(
            delete(PurchaseOrder).where(PurchaseOrder.id == purchase_order_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def approve_purchase_order(
        self,
        purchase_order_id: int,
        approval_data: PurchaseOrderApprovalSchema,
        approved_by: int
    ) -> Optional[PurchaseOrderApproval]:
        """Approve or reject a purchase order."""
        # Create approval record
        approval = PurchaseOrderApproval(
            purchase_order_id=purchase_order_id,
            status=approval_data.status,
            notes=approval_data.notes,
            approved_by=approved_by
        )
        self.db.add(approval)

        # Update purchase order status
        await self.db.execute(
            update(PurchaseOrder)
            .where(PurchaseOrder.id == purchase_order_id)
            .values(status=approval_data.status)
        )

        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_purchase_order_approvals(
        self,
        purchase_order_id: int
    ) -> List[PurchaseOrderApproval]:
        """Get approval history for a purchase order."""
        result = await self.db.execute(
            select(PurchaseOrderApproval)
            .where(PurchaseOrderApproval.purchase_order_id == purchase_order_id)
            .order_by(PurchaseOrderApproval.created_at.desc())
        )
        return result.scalars().all() 