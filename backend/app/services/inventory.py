from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory, InventoryAdjustment, InventoryCount
from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryAdjustmentCreate,
    InventoryCount as InventoryCountSchema
)

class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inventory(
        self,
        inventory_data: InventoryCreate
    ) -> Inventory:
        """Create a new inventory record."""
        inventory = Inventory(**inventory_data.model_dump())
        self.db.add(inventory)
        await self.db.commit()
        await self.db.refresh(inventory)
        return inventory

    async def get_inventory(
        self,
        inventory_id: int
    ) -> Optional[Inventory]:
        """Get an inventory record by ID."""
        result = await self.db.execute(
            select(Inventory)
            .options(
                selectinload(Inventory.product),
                selectinload(Inventory.location)
            )
            .where(Inventory.id == inventory_id)
        )
        return result.scalar_one_or_none()

    async def get_inventory_by_product_location(
        self,
        product_id: int,
        location_id: int
    ) -> Optional[Inventory]:
        """Get inventory by product and location."""
        result = await self.db.execute(
            select(Inventory)
            .where(
                Inventory.product_id == product_id,
                Inventory.location_id == location_id
            )
        )
        return result.scalar_one_or_none()

    async def get_inventory_list(
        self,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[int] = None,
        location_id: Optional[int] = None
    ) -> List[Inventory]:
        """Get a list of inventory records with optional filtering."""
        query = select(Inventory).options(
            selectinload(Inventory.product),
            selectinload(Inventory.location)
        )
        
        if product_id:
            query = query.where(Inventory.product_id == product_id)
        if location_id:
            query = query.where(Inventory.location_id == location_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_inventory(
        self,
        inventory_id: int,
        inventory_data: InventoryUpdate
    ) -> Optional[Inventory]:
        """Update an inventory record."""
        await self.db.execute(
            update(Inventory)
            .where(Inventory.id == inventory_id)
            .values(**inventory_data.model_dump(exclude_unset=True))
        )
        await self.db.commit()
        return await self.get_inventory(inventory_id)

    async def create_inventory_adjustment(
        self,
        adjustment_data: InventoryAdjustmentCreate,
        created_by: int
    ) -> InventoryAdjustment:
        """Create an inventory adjustment."""
        # Get current inventory
        inventory = await self.get_inventory(adjustment_data.inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        # Create adjustment record
        adjustment = InventoryAdjustment(
            **adjustment_data.model_dump(),
            created_by=created_by,
            previous_quantity=inventory.quantity
        )
        self.db.add(adjustment)

        # Update inventory quantity
        new_quantity = (
            inventory.quantity + adjustment_data.quantity
            if adjustment_data.adjustment_type == "addition"
            else inventory.quantity - adjustment_data.quantity
        )
        await self.db.execute(
            update(Inventory)
            .where(Inventory.id == inventory.id)
            .values(quantity=new_quantity)
        )

        await self.db.commit()
        await self.db.refresh(adjustment)
        return adjustment

    async def create_inventory_count(
        self,
        count_data: InventoryCountSchema,
        created_by: int
    ) -> InventoryCount:
        """Create an inventory count record."""
        # Get current inventory
        inventory = await self.get_inventory(count_data.inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")

        # Create count record
        count = InventoryCount(
            **count_data.model_dump(),
            created_by=created_by,
            system_quantity=inventory.quantity,
            difference=count_data.counted_quantity - inventory.quantity
        )
        self.db.add(count)

        # Update inventory quantity if there's a difference
        if count.difference != 0:
            await self.db.execute(
                update(Inventory)
                .where(Inventory.id == inventory.id)
                .values(
                    quantity=count_data.counted_quantity,
                    last_count_date=datetime.utcnow()
                )
            )

        await self.db.commit()
        await self.db.refresh(count)
        return count

    async def get_inventory_adjustments(
        self,
        inventory_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryAdjustment]:
        """Get adjustment history for an inventory item."""
        result = await self.db.execute(
            select(InventoryAdjustment)
            .where(InventoryAdjustment.inventory_id == inventory_id)
            .order_by(InventoryAdjustment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_inventory_counts(
        self,
        inventory_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryCount]:
        """Get count history for an inventory item."""
        result = await self.db.execute(
            select(InventoryCount)
            .where(InventoryCount.inventory_id == inventory_id)
            .order_by(InventoryCount.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all() 