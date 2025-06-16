from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get a list of products with optional filtering."""
        query = select(Product).options(selectinload(Product.category))
        
        if category_id:
            query = query.where(Product.category_id == category_id)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update a product."""
        await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**product_data.model_dump(exclude_unset=True))
        )
        await self.db.commit()
        return await self.get_product(product_id)

    async def delete_product(self, product_id: int) -> bool:
        """Delete a product."""
        result = await self.db.execute(
            delete(Product).where(Product.id == product_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_products_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by category."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all() 