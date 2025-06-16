from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.supplier import (
    Supplier,
    SupplierContact,
    SupplierAddress,
    SupplierProduct
)
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierContactCreate,
    SupplierAddressCreate,
    SupplierProductCreate
)

class SupplierService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_supplier(
        self,
        supplier_data: SupplierCreate
    ) -> Supplier:
        """Create a new supplier with contacts and addresses."""
        # Create the supplier
        supplier_dict = supplier_data.model_dump(exclude={"contacts", "addresses"})
        supplier = Supplier(**supplier_dict)
        self.db.add(supplier)
        await self.db.flush()

        # Create contacts
        for contact_data in supplier_data.contacts:
            contact = SupplierContact(
                **contact_data.model_dump(),
                supplier_id=supplier.id
            )
            self.db.add(contact)

        # Create addresses
        for address_data in supplier_data.addresses:
            address = SupplierAddress(
                **address_data.model_dump(),
                supplier_id=supplier.id
            )
            self.db.add(address)

        await self.db.commit()
        await self.db.refresh(supplier)
        return supplier

    async def get_supplier(
        self,
        supplier_id: int
    ) -> Optional[Supplier]:
        """Get a supplier by ID with contacts and addresses."""
        result = await self.db.execute(
            select(Supplier)
            .options(
                selectinload(Supplier.contacts),
                selectinload(Supplier.addresses),
                selectinload(Supplier.products)
            )
            .where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def get_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Supplier]:
        """Get a list of suppliers with optional filtering."""
        query = select(Supplier).options(
            selectinload(Supplier.contacts),
            selectinload(Supplier.addresses)
        )
        
        if status:
            query = query.where(Supplier.status == status)
        if search:
            query = query.where(Supplier.name.ilike(f"%{search}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_supplier(
        self,
        supplier_id: int,
        supplier_data: SupplierUpdate
    ) -> Optional[Supplier]:
        """Update a supplier."""
        await self.db.execute(
            update(Supplier)
            .where(Supplier.id == supplier_id)
            .values(**supplier_data.model_dump(exclude_unset=True))
        )
        await self.db.commit()
        return await self.get_supplier(supplier_id)

    async def delete_supplier(self, supplier_id: int) -> bool:
        """Delete a supplier."""
        result = await self.db.execute(
            delete(Supplier).where(Supplier.id == supplier_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def add_supplier_contact(
        self,
        supplier_id: int,
        contact_data: SupplierContactCreate
    ) -> SupplierContact:
        """Add a contact to a supplier."""
        contact = SupplierContact(
            **contact_data.model_dump(),
            supplier_id=supplier_id
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def add_supplier_address(
        self,
        supplier_id: int,
        address_data: SupplierAddressCreate
    ) -> SupplierAddress:
        """Add an address to a supplier."""
        address = SupplierAddress(
            **address_data.model_dump(),
            supplier_id=supplier_id
        )
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)
        return address

    async def add_supplier_product(
        self,
        supplier_id: int,
        product_data: SupplierProductCreate
    ) -> SupplierProduct:
        """Add a product to a supplier."""
        product = SupplierProduct(
            **product_data.model_dump(),
            supplier_id=supplier_id
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_supplier_products(
        self,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SupplierProduct]:
        """Get products for a supplier."""
        result = await self.db.execute(
            select(SupplierProduct)
            .where(SupplierProduct.supplier_id == supplier_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_supplier_by_code(self, code: str) -> Optional[Supplier]:
        """Get a supplier by code."""
        result = await self.db.execute(
            select(Supplier)
            .options(
                selectinload(Supplier.contacts),
                selectinload(Supplier.addresses)
            )
            .where(Supplier.code == code)
        )
        return result.scalar_one_or_none() 