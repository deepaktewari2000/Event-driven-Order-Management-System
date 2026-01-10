from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderFilter,
    OrderStatusUpdate
)
from app.services.order_service import (
    create_order,
    get_order,
    update_order,
    delete_order,
    update_order_status,
    list_orders
)
from app.api.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.core.exceptions import OrderNotFoundException

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new order.
    
    Requires authentication.
    
    - **product_id**: Product identifier
    - **quantity**: Number of items (1-1000)
    - **customer_email**: Customer email address
    - **shipping_address**: Optional shipping address
    - **total_price**: Optional total price (auto-calculated if not provided)
    """
    return await create_order(db, order, current_user)


@router.get("/", response_model=OrderListResponse)
async def list_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    product_id: Optional[str] = None,
    user_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List orders with pagination and filtering.
    
    Requires authentication.
    - Regular users see only their own orders
    - Admins see all orders
    
    **Filters:**
    - **status**: Filter by order status
    - **product_id**: Filter by product ID
    - **user_id**: Filter by user ID (admin only)
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    
    **Pagination:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 10, max: 100)
    """
    from app.models.order import OrderStatus
    
    # Build filters
    filters = OrderFilter(
        status=OrderStatus(status) if status else None,
        product_id=product_id,
        user_id=user_id,
        min_price=min_price,
        max_price=max_price
    )
    
    orders, total = await list_orders(db, skip, limit, filters, current_user)
    
    return OrderListResponse(
        orders=orders,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def fetch(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific order by ID.
    
    Requires authentication.
    - Regular users can only access their own orders
    - Admins can access any order
    """
    order = await get_order(db, order_id)
    
    if not order:
        raise OrderNotFoundException(order_id)
    
    # Check ownership (unless admin)
    from app.models.user import UserRole
    if order.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("You don't have permission to view this order")
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an order.
    
    Requires authentication.
    - Users can update their own orders
    - Admins can update any order
    
    **Updatable fields:**
    - **quantity**: Number of items
    - **shipping_address**: Shipping address
    - **total_price**: Total price
    """
    return await update_order(db, order_id, order_data, current_user)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    order_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an order.
    
    **Admin only** - Requires admin role.
    """
    await delete_order(db, order_id, current_admin)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status.
    
    **Admin only** - Requires admin role.
    
    **Available statuses:**
    - CREATED
    - PAYMENT_PENDING
    - CONFIRMED
    - SHIPPED
    - DELIVERED
    - CANCELLED
    - FAILED
    """
    return await update_order_status(db, order_id, status_data.status)

