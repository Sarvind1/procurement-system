from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import String, Numeric, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class ShipmentStatus(str, SQLEnum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PARTIALLY_DELIVERED = "partially_delivered"
    CANCELLED = "cancelled"
    EXCEPTION = "exception"

class ShipmentType(str, SQLEnum):
    AIR = "air"
    SEA = "sea"
    LAND = "land"
    RAIL = "rail"
    MULTIMODAL = "multimodal"

class Shipment(Base):
    shipment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    purchase_order_id: Mapped[UUID] = mapped_column(ForeignKey("purchaseorder.id"), nullable=False)
    carrier: Mapped[str] = mapped_column(String(100), nullable=False)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipment_type: Mapped[ShipmentType] = mapped_column(SQLEnum(ShipmentType), nullable=False)
    status: Mapped[ShipmentStatus] = mapped_column(
        SQLEnum(ShipmentStatus),
        default=ShipmentStatus.PENDING,
        nullable=False
    )
    shipping_date: Mapped[datetime] = mapped_column(nullable=False)
    estimated_delivery_date: Mapped[datetime] = mapped_column(nullable=False)
    actual_delivery_date: Mapped[datetime | None] = mapped_column(nullable=True)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    customs_declaration: Mapped[dict] = mapped_column(JSON, nullable=True)
    tracking_updates: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="shipments")
    items: Mapped[List["ShipmentItem"]] = relationship(back_populates="shipment")
    documents: Mapped[List["ShipmentDocument"]] = relationship(back_populates="shipment")

class ShipmentItem(Base):
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipment.id"), nullable=False)
    purchase_order_item_id: Mapped[UUID] = mapped_column(ForeignKey("purchaseorderitem.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    customs_value: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    customs_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    shipment: Mapped[Shipment] = relationship(back_populates="items")
    purchase_order_item: Mapped["PurchaseOrderItem"] = relationship()

class ShipmentDocument(Base):
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipment.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bill of lading, packing list, etc.
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(nullable=False)
    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    shipment: Mapped[Shipment] = relationship(back_populates="documents")
    uploaded_by: Mapped["User"] = relationship() 