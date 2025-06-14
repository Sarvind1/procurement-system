from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import String, Numeric, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class ProductStatus(str, SQLEnum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"

class Category(Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("category.id"),
        nullable=True
    )

    # Relationships
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        backref="subcategories"
    )
    products: Mapped[List["Product"]] = relationship(back_populates="category")

class Product(Base):
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("category.id"), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    specifications: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[ProductStatus] = mapped_column(
        SQLEnum(ProductStatus),
        default=ProductStatus.ACTIVE,
        nullable=False
    )

    # Relationships
    category: Mapped[Category] = relationship(back_populates="products")
    inventory: Mapped[List["Inventory"]] = relationship(back_populates="product")
    purchase_order_items: Mapped[List["PurchaseOrderItem"]] = relationship(back_populates="product") 