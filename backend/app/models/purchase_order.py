from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import String, Numeric, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class PurchaseOrderStatus(str, SQLEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class ApprovalStatus(str, SQLEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PurchaseOrder(Base):
    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("supplier.id"), nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[PurchaseOrderStatus] = mapped_column(
        SQLEnum(PurchaseOrderStatus),
        default=PurchaseOrderStatus.DRAFT,
        nullable=False
    )
    order_date: Mapped[datetime] = mapped_column(nullable=False)
    expected_delivery_date: Mapped[datetime] = mapped_column(nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    terms_and_conditions: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approval_workflow: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
    created_by: Mapped["User"] = relationship(back_populates="purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship(back_populates="purchase_order")
    approvals: Mapped[List["PurchaseOrderApproval"]] = relationship(back_populates="purchase_order")
    shipments: Mapped[List["Shipment"]] = relationship(back_populates="purchase_order")

class PurchaseOrderItem(Base):
    purchase_order_id: Mapped[UUID] = mapped_column(ForeignKey("purchaseorder.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    received_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="purchase_order_items")

class PurchaseOrderApproval(Base):
    purchase_order_id: Mapped[UUID] = mapped_column(ForeignKey("purchaseorder.id"), nullable=False)
    approver_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        SQLEnum(ApprovalStatus),
        default=ApprovalStatus.PENDING,
        nullable=False
    )
    comments: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="approvals")
    approver: Mapped["User"] = relationship() 