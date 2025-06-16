from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.shipment import (
    Shipment,
    ShipmentItem,
    ShipmentDocument
)
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentStatusUpdate
)

class ShipmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_shipment(
        self,
        shipment_data: ShipmentCreate,
        created_by: int
    ) -> Shipment:
        """Create a new shipment with items and documents."""
        # Create the shipment
        shipment_dict = shipment_data.model_dump(exclude={"items", "documents"})
        shipment = Shipment(**shipment_dict, created_by=created_by)
        self.db.add(shipment)
        await self.db.flush()

        # Create shipment items
        for item_data in shipment_data.items:
            item = ShipmentItem(
                **item_data.model_dump(),
                shipment_id=shipment.id
            )
            self.db.add(item)

        # Create shipment documents if provided
        if shipment_data.documents:
            for doc_data in shipment_data.documents:
                document = ShipmentDocument(
                    **doc_data.model_dump(),
                    shipment_id=shipment.id,
                    uploaded_by=created_by
                )
                self.db.add(document)

        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment

    async def get_shipment(
        self,
        shipment_id: int
    ) -> Optional[Shipment]:
        """Get a shipment by ID with items and documents."""
        result = await self.db.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.items),
                selectinload(Shipment.documents)
            )
            .where(Shipment.id == shipment_id)
        )
        return result.scalar_one_or_none()

    async def get_shipments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        purchase_order_id: Optional[int] = None
    ) -> List[Shipment]:
        """Get a list of shipments with optional filtering."""
        query = select(Shipment).options(
            selectinload(Shipment.items),
            selectinload(Shipment.documents)
        )
        
        if status:
            query = query.where(Shipment.status == status)
        if purchase_order_id:
            query = query.where(Shipment.purchase_order_id == purchase_order_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_shipment(
        self,
        shipment_id: int,
        shipment_data: ShipmentUpdate
    ) -> Optional[Shipment]:
        """Update a shipment."""
        await self.db.execute(
            update(Shipment)
            .where(Shipment.id == shipment_id)
            .values(**shipment_data.model_dump(exclude_unset=True))
        )
        await self.db.commit()
        return await self.get_shipment(shipment_id)

    async def update_shipment_status(
        self,
        shipment_id: int,
        status_data: ShipmentStatusUpdate
    ) -> Optional[Shipment]:
        """Update a shipment's status."""
        # Update shipment status
        await self.db.execute(
            update(Shipment)
            .where(Shipment.id == shipment_id)
            .values(
                status=status_data.status,
                notes=status_data.notes
            )
        )

        # Add status to history
        shipment = await self.get_shipment(shipment_id)
        if shipment:
            status_history = shipment.status_history or []
            status_history.append({
                "status": status_data.status,
                "notes": status_data.notes,
                "location": status_data.location,
                "timestamp": status_data.timestamp or datetime.utcnow().isoformat()
            })
            await self.db.execute(
                update(Shipment)
                .where(Shipment.id == shipment_id)
                .values(status_history=status_history)
            )

        await self.db.commit()
        return await self.get_shipment(shipment_id)

    async def add_shipment_document(
        self,
        shipment_id: int,
        document_data: dict,
        uploaded_by: int
    ) -> ShipmentDocument:
        """Add a document to a shipment."""
        document = ShipmentDocument(
            **document_data,
            shipment_id=shipment_id,
            uploaded_by=uploaded_by
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_shipment_documents(
        self,
        shipment_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ShipmentDocument]:
        """Get documents for a shipment."""
        result = await self.db.execute(
            select(ShipmentDocument)
            .where(ShipmentDocument.shipment_id == shipment_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_shipment_by_tracking(
        self,
        tracking_number: str
    ) -> Optional[Shipment]:
        """Get a shipment by tracking number."""
        result = await self.db.execute(
            select(Shipment)
            .options(
                selectinload(Shipment.items),
                selectinload(Shipment.documents)
            )
            .where(Shipment.tracking_number == tracking_number)
        )
        return result.scalar_one_or_none() 