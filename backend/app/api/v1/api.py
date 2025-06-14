from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    products,
    categories,
    inventory,
    suppliers,
    purchase_orders,
    shipments
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["purchase orders"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"]) 