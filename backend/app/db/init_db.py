import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.supplier import Supplier, SupplierCategory, SupplierStatus

logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    # Create initial admin user
    admin = await create_admin_user(db)
    if admin:
        logger.info("Created initial admin user")

    # Create initial categories
    categories = await create_initial_categories(db)
    if categories:
        logger.info("Created initial categories")

    # Create initial suppliers
    suppliers = await create_initial_suppliers(db)
    if suppliers:
        logger.info("Created initial suppliers")

async def create_admin_user(db: AsyncSession) -> User | None:
    # Check if admin user already exists
    result = await db.execute(
        "SELECT id FROM users WHERE email = :email",
        {"email": "admin@example.com"}
    )
    if result.scalar_one_or_none():
        return None

    # Create admin user
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),  # Change in production
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin

async def create_initial_categories(db: AsyncSession) -> list[Category]:
    # Check if categories already exist
    result = await db.execute("SELECT COUNT(*) FROM category")
    if result.scalar_one() > 0:
        return []

    # Create root categories
    categories = [
        Category(name="Raw Materials", description="Basic materials used in manufacturing"),
        Category(name="Components", description="Pre-manufactured parts and assemblies"),
        Category(name="Finished Goods", description="Ready-to-sell products"),
        Category(name="Packaging", description="Materials used for product packaging"),
        Category(name="Office Supplies", description="General office materials and equipment"),
        Category(name="IT Equipment", description="Computers, servers, and networking equipment"),
        Category(name="Maintenance", description="Tools and supplies for maintenance"),
        Category(name="Services", description="Professional and technical services")
    ]

    for category in categories:
        db.add(category)
    await db.commit()

    for category in categories:
        await db.refresh(category)
    return categories

async def create_initial_suppliers(db: AsyncSession) -> list[Supplier]:
    # Check if suppliers already exist
    result = await db.execute("SELECT COUNT(*) FROM supplier")
    if result.scalar_one() > 0:
        return []

    # Create initial suppliers
    suppliers = [
        Supplier(
            name="Global Manufacturing Inc.",
            code="GMI001",
            category=SupplierCategory.MANUFACTURER,
            status=SupplierStatus.ACTIVE,
            tax_id="123456789",
            payment_terms=30,
            credit_limit=100000.00,
            currency="USD",
            is_preferred=True
        ),
        Supplier(
            name="Tech Distributors Ltd.",
            code="TDL002",
            category=SupplierCategory.DISTRIBUTOR,
            status=SupplierStatus.ACTIVE,
            tax_id="987654321",
            payment_terms=45,
            credit_limit=50000.00,
            currency="USD",
            is_preferred=False
        ),
        Supplier(
            name="Office Supplies Co.",
            code="OSC003",
            category=SupplierCategory.WHOLESALER,
            status=SupplierStatus.ACTIVE,
            tax_id="456789123",
            payment_terms=30,
            credit_limit=25000.00,
            currency="USD",
            is_preferred=False
        )
    ]

    for supplier in suppliers:
        db.add(supplier)
    await db.commit()

    for supplier in suppliers:
        await db.refresh(supplier)
    return suppliers 