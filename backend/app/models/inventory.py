from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import String, Integer, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class InventoryAdjustmentType(str, SQLEnum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"

class Location(Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    inventory: Mapped[List["Inventory"]] = relationship(back_populates="location")

class Inventory(Base):
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"), nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_counted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_movement_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="inventory")
    location: Mapped[Location] = relationship(back_populates="inventory")
    adjustments: Mapped[List["InventoryAdjustment"]] = relationship(back_populates="inventory")

class InventoryAdjustment(Base):
    inventory_id: Mapped[UUID] = mapped_column(ForeignKey("inventory.id"), nullable=False)
    adjusted_by_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    adjustment_type: Mapped[InventoryAdjustmentType] = mapped_column(SQLEnum(InventoryAdjustmentType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    inventory: Mapped[Inventory] = relationship(back_populates="adjustments")
    adjusted_by: Mapped["User"] = relationship(back_populates="inventory_adjustments") 