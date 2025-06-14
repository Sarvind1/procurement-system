from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.security import get_password_hash

class UserRole(str, SQLEnum):
    ADMIN = "admin"
    PROCUREMENT_MANAGER = "procurement_manager"
    INVENTORY_MANAGER = "inventory_manager"
    FINANCE_APPROVER = "finance_approver"
    VIEWER = "viewer"

class User(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(back_populates="created_by")
    inventory_adjustments: Mapped[List["InventoryAdjustment"]] = relationship(back_populates="adjusted_by")

    def __init__(self, **kwargs):
        if "password" in kwargs:
            kwargs["hashed_password"] = get_password_hash(kwargs.pop("password"))
        super().__init__(**kwargs)

    def verify_password(self, password: str) -> bool:
        from app.core.security import verify_password
        return verify_password(password, self.hashed_password) 