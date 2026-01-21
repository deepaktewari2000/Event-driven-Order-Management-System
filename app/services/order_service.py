from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Tuple, Any
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderFilter, OrderResponse
from app.core.exceptions import OrderNotFoundException, ForbiddenException
from app.core.config import settings
from app.core.kafka import kafka_producer
from app.core.redis import redis_client
from app.services import product_service
import logging

logger = logging.getLogger(__name__)


async def create_order(
    db: AsyncSession,
    order_data: OrderCreate,
    user: User
) -> Order:
    """
    Create a new order.
    
    Args:
        db: Database session
        order_data: Order creation data
        user: Current user
        
    Returns:
        Created order
    """
    # 1. Validate Product and Check Stock
    try:
        product_id = int(order_data.product_id)
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid product_id format. Must be an integer.")

    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    if product.stock_quantity < order_data.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock_quantity}, Requested: {order_data.quantity}"
        )

    # 2. Use Product Price and Calculate Total
    total_price = product.price * order_data.quantity
    
    # 3. Create Order
    order = Order(
        user_id=user.id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        total_price=total_price,
        customer_email=order_data.customer_email,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.CREATED
    )
    
    db.add(order)
    
    # 4. Deduct Stock (Transactional)
    success = await product_service.deduct_stock(db, product_id, order_data.quantity)
    if not success:
        # This shouldn't happen because we checked stock, but for safety:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Stock deduction failed.")

    await db.commit()
    await db.refresh(order)
    
    # Send event to Kafka
    order_event = {
        "event": "ORDER_CREATED",
        "order_id": order.id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "status": order.status.value,
        "customer_email": order.customer_email
    }
    await kafka_producer.send_message(settings.KAFKA_TOPIC_ORDER_EVENTS, order_event)
    
    return order


async def get_order(
    db: AsyncSession,
    order_id: int,
    use_cache: bool = True
) -> Optional[Any]:
    """
    Get order by ID. Checks Redis cache first if use_cache is True.
    """
    cache_key = f"order:{order_id}"
    
    if use_cache:
        cached_order = await redis_client.get(cache_key)
        if cached_order:
            logger.debug(f"Redis cache hit for order {order_id}")
            return OrderResponse.model_validate(cached_order)
            
    order = await db.get(Order, order_id)
    
    if order and use_cache:
        # Cache the order data for 1 hour
        order_data = OrderResponse.model_validate(order).model_dump(mode='json')
        await redis_client.set(cache_key, order_data)
        logger.debug(f"Redis cache miss for order {order_id}. Cached data.")
        
    return order


async def update_order(
    db: AsyncSession,
    order_id: int,
    order_data: OrderUpdate,
    user: User
) -> Order:
    """
    Update an order.
    
    Args:
        db: Database session
        order_id: Order ID
        order_data: Update data
        user: Current user
        
    Returns:
        Updated order
        
    Raises:
        OrderNotFoundException: If order not found
        ForbiddenException: If user doesn't own the order
    """
    # Bypass cache for update
    order = await get_order(db, order_id, use_cache=False)
    
    if not order:
        raise OrderNotFoundException(order_id)
    
    # Check ownership (unless admin)
    from app.models.user import UserRole
    if order.user_id != user.id and user.role != UserRole.ADMIN:
        raise ForbiddenException("You don't have permission to update this order")
    
    # Update fields
    if order_data.quantity is not None:
        order.quantity = order_data.quantity
    if order_data.shipping_address is not None:
        order.shipping_address = order_data.shipping_address
    if order_data.total_price is not None:
        order.total_price = order_data.total_price
    
    await db.commit()
    await db.refresh(order)
    
    # Invalidate cache
    await redis_client.delete(f"order:{order_id}")
    
    return order


async def delete_order(
    db: AsyncSession,
    order_id: int,
    user: User
) -> None:
    """
    Delete an order (admin only).
    
    Args:
        db: Database session
        order_id: Order ID
        user: Current user (must be admin)
        
    Raises:
        OrderNotFoundException: If order not found
    """
    # Bypass cache for deletion
    order = await get_order(db, order_id, use_cache=False)
    
    if not order:
        raise OrderNotFoundException(order_id)
    
    await db.delete(order)
    await db.commit()
    
    # Invalidate cache
    await redis_client.delete(f"order:{order_id}")


async def update_order_status(
    db: AsyncSession,
    order_id: int,
    status: OrderStatus
) -> Order:
    """
    Update order status (admin only).
    
    Args:
        db: Database session
        order_id: Order ID
        status: New status
        
    Returns:
        Updated order
        
    Raises:
        OrderNotFoundException: If order not found
    """
    # Bypass cache for update
    order = await get_order(db, order_id, use_cache=False)
    
    if not order:
        raise OrderNotFoundException(order_id)
    
    order.status = status
    await db.commit()
    await db.refresh(order)
    
    # Invalidate cache
    await redis_client.delete(f"order:{order_id}")
    
    return order


async def list_orders(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    filters: Optional[OrderFilter] = None,
    user: Optional[User] = None
) -> Tuple[List[Order], int]:
    """
    List orders with pagination and filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        filters: Optional filters
        user: Current user (if not admin, only returns their orders)
        
    Returns:
        Tuple of (orders list, total count)
    """
    query = select(Order)
    
    # Build filter conditions
    conditions = []
    
    # Non-admin users can only see their own orders
    if user and user.role.value != "ADMIN":
        conditions.append(Order.user_id == user.id)
    
    if filters:
        if filters.status:
            conditions.append(Order.status == filters.status)
        if filters.product_id:
            conditions.append(Order.product_id == filters.product_id)
        if filters.user_id:
            conditions.append(Order.user_id == filters.user_id)
        if filters.min_price is not None:
            conditions.append(Order.total_price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(Order.total_price <= filters.max_price)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(Order)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return list(orders), total


async def get_user_orders(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[Order], int]:
    """
    Get orders for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (orders list, total count)
    """
    query = select(Order).where(Order.user_id == user_id)
    
    # Get total count
    count_query = select(func.count()).select_from(Order).where(Order.user_id == user_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return list(orders), total

