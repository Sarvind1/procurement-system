from typing import Optional
from datetime import datetime
from pydantic import BaseModel, conint, condecimal
from decimal import Decimal

class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: conint(ge=0)
    minimum_quantity: conint(ge=0) = 0
    maximum_quantity: Optional[conint(gt=0)] = None
    notes: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_restock_date: Optional[datetime] = None
    last_count_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class InventoryAdjustmentBase(BaseModel):
    inventory_id: int
    adjustment_type: str  # "addition" or "subtraction"
    quantity: conint(gt=0)
    reason: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass

class InventoryAdjustmentResponse(InventoryAdjustmentBase):
    id: int
    created_by: int
    created_at: datetime
    previous_quantity: int
    new_quantity: int

    class Config:
        from_attributes = True

class InventoryCount(BaseModel):
    inventory_id: int
    counted_quantity: conint(ge=0)
    notes: Optional[str] = None

class InventoryCountResponse(InventoryCount):
    id: int
    created_by: int
    created_at: datetime
    system_quantity: int
    difference: int

    class Config:
        from_attributes = True 