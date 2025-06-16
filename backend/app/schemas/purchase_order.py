from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, conint, condecimal
from decimal import Decimal

class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: conint(gt=0)
    unit_price: condecimal(gt=0, decimal_places=2)
    notes: Optional[str] = None

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemUpdate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int
    total_price: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    expected_delivery_date: datetime
    notes: Optional[str] = None
    status: str = "draft"

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderUpdate(PurchaseOrderBase):
    pass

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    order_number: str
    total_amount: Decimal
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseOrderItemResponse]
    status_history: List[dict]

    class Config:
        from_attributes = True

class PurchaseOrderApproval(BaseModel):
    purchase_order_id: int
    status: str
    notes: Optional[str] = None

class PurchaseOrderApprovalResponse(PurchaseOrderApproval):
    id: int
    approved_by: int
    created_at: datetime

    class Config:
        from_attributes = True 