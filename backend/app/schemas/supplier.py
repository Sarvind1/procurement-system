from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

class SupplierContactBase(BaseModel):
    name: str
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_primary: bool = False

class SupplierContactCreate(SupplierContactBase):
    pass

class SupplierContactUpdate(SupplierContactBase):
    pass

class SupplierContactResponse(SupplierContactBase):
    id: int
    supplier_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupplierAddressBase(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool = False
    address_type: str = "shipping"  # shipping, billing, or both

class SupplierAddressCreate(SupplierAddressBase):
    pass

class SupplierAddressUpdate(SupplierAddressBase):
    pass

class SupplierAddressResponse(SupplierAddressBase):
    id: int
    supplier_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SupplierBase(BaseModel):
    name: str
    code: str
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    contacts: List[SupplierContactCreate]
    addresses: List[SupplierAddressCreate]

class SupplierUpdate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contacts: List[SupplierContactResponse]
    addresses: List[SupplierAddressResponse]

    class Config:
        from_attributes = True

class SupplierProductBase(BaseModel):
    supplier_id: int
    product_id: int
    supplier_product_code: str
    unit_price: float
    minimum_order_quantity: int = 1
    lead_time_days: Optional[int] = None
    is_preferred: bool = False

class SupplierProductCreate(SupplierProductBase):
    pass

class SupplierProductUpdate(SupplierProductBase):
    pass

class SupplierProductResponse(SupplierProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 