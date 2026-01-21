from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.api.dependencies import get_current_admin, get_current_user
from app.services import product_service
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Create a new product (Admin only)."""
    return await product_service.create_product(db, product_in)

@router.get("/", response_model=List[ProductResponse])
async def list_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all products (Public)."""
    products, total = await product_service.list_products(db, skip, limit)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def fetch(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific product by ID."""
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Update a product (Admin only)."""
    product = await product_service.update_product(db, product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a product (Admin only)."""
    success = await product_service.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
