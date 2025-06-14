from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import String, Numeric, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class SupplierStatus(str, SQLEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    PENDING = "pending"

class SupplierCategory(str, SQLEnum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    WHOLESALER = "wholesaler"
    SERVICE_PROVIDER = "service_provider"

class Supplier(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    category: Mapped[SupplierCategory] = mapped_column(SQLEnum(SupplierCategory), nullable=False)
    status: Mapped[SupplierStatus] = mapped_column(
        SQLEnum(SupplierStatus),
        default=SupplierStatus.PENDING,
        nullable=False
    )
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_terms: Mapped[int] = mapped_column(default=30, nullable=False)  # days
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    performance_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    contacts: Mapped[List["SupplierContact"]] = relationship(back_populates="supplier")
    addresses: Mapped[List["SupplierAddress"]] = relationship(back_populates="supplier")
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(back_populates="supplier")
    products: Mapped[List["SupplierProduct"]] = relationship(back_populates="supplier")

class SupplierContact(Base):
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("supplier.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    supplier: Mapped[Supplier] = relationship(back_populates="contacts")

class SupplierAddress(Base):
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("supplier.id"), nullable=False)
    address_type: Mapped[str] = mapped_column(String(50), nullable=False)  # billing, shipping, etc.
    street_address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    supplier: Mapped[Supplier] = relationship(back_populates="addresses")

class SupplierProduct(Base):
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("supplier.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    supplier_sku: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    lead_time_days: Mapped[int] = mapped_column(default=0, nullable=False)
    minimum_order_quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    supplier: Mapped[Supplier] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship() 