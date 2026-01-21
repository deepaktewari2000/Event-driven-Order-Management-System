from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Tuple, Any
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.redis import redis_client
import logging

logger = logging.getLogger(__name__)

async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
    """Create a new product."""
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

async def get_product(db: AsyncSession, product_id: int, use_cache: bool = True) -> Optional[Any]:
    """Get product by ID with optional caching."""
    cache_key = f"product:{product_id}"
    
    if use_cache:
        cached_product = await redis_client.get(cache_key)
        if cached_product:
            logger.debug(f"Redis cache hit for product {product_id}")
            return ProductResponse.model_validate(cached_product)

    product = await db.get(Product, product_id)
    
    if product and use_cache:
        product_data = ProductResponse.model_validate(product).model_dump(mode='json')
        await redis_client.set(cache_key, product_data)
        logger.debug(f"Redis cache miss for product {product_id}. Cached data.")
        
    return product

async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
    """Update a product and invalidate cache."""
    product = await get_product(db, product_id, use_cache=False)
    if not product:
        return None
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    await db.commit()
    await db.refresh(product)
    
    # Invalidate cache
    await redis_client.delete(f"product:{product_id}")
    return product

async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Delete a product and invalidate cache."""
    product = await get_product(db, product_id, use_cache=False)
    if not product:
        return False
    
    await db.delete(product)
    await db.commit()
    
    # Invalidate cache
    await redis_client.delete(f"product:{product_id}")
    return True

async def list_products(db: AsyncSession, skip: int = 0, limit: int = 20) -> Tuple[List[Product], int]:
    """List products with pagination."""
    query = select(Product).offset(skip).limit(limit).order_by(Product.name)
    result = await db.execute(query)
    products = result.scalars().all()
    
    count_query = select(func.count()).select_from(Product)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return list(products), total

async def check_stock(db: AsyncSession, product_id: int, quantity: int) -> bool:
    """Check if product has enough stock."""
    product = await get_product(db, product_id, use_cache=False)
    if not product or product.stock_quantity < quantity:
        return False
    return True

async def deduct_stock(db: AsyncSession, product_id: int, quantity: int) -> bool:
    """Deduct stock from product."""
    product = await get_product(db, product_id, use_cache=False)
    if not product or product.stock_quantity < quantity:
        return False
    
    product.stock_quantity -= quantity
    await db.commit()
    
    # Invalidate cache
    await redis_client.delete(f"product:{product_id}")
    return True
