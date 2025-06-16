from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, conint, constr

class ShipmentItemBase(BaseModel):
    purchase_order_item_id: int
    quantity: conint(gt=0)
    notes: Optional[str] = None

class ShipmentItemCreate(ShipmentItemBase):
    pass

class ShipmentItemUpdate(ShipmentItemBase):
    pass

class ShipmentItemResponse(ShipmentItemBase):
    id: int
    shipment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShipmentDocumentBase(BaseModel):
    document_type: str  # invoice, packing_slip, customs_document, etc.
    file_name: str
    file_path: str
    notes: Optional[str] = None

class ShipmentDocumentCreate(ShipmentDocumentBase):
    pass

class ShipmentDocumentUpdate(ShipmentDocumentBase):
    pass

class ShipmentDocumentResponse(ShipmentDocumentBase):
    id: int
    shipment_id: int
    uploaded_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShipmentBase(BaseModel):
    purchase_order_id: int
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    shipping_method: Optional[str] = None
    estimated_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    status: str = "pending"
    notes: Optional[str] = None

class ShipmentCreate(ShipmentBase):
    items: List[ShipmentItemCreate]
    documents: Optional[List[ShipmentDocumentCreate]] = None

class ShipmentUpdate(ShipmentBase):
    pass

class ShipmentResponse(ShipmentBase):
    id: int
    shipment_number: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: List[ShipmentItemResponse]
    documents: List[ShipmentDocumentResponse]
    status_history: List[dict]

    class Config:
        from_attributes = True

class ShipmentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[datetime] = None 