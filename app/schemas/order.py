from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    product_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=1000)
    customer_email: EmailStr
    shipping_address: Optional[str] = Field(None, max_length=500)
    total_price: Optional[float] = Field(None, ge=0)


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    quantity: Optional[int] = Field(None, gt=0, le=1000)
    shipping_address: Optional[str] = Field(None, max_length=500)
    total_price: Optional[float] = Field(None, ge=0)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    user_id: int
    product_id: str
    quantity: int
    total_price: float
    status: OrderStatus
    customer_email: str
    shipping_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for paginated order list response."""
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int


class OrderFilter(BaseModel):
    """Schema for filtering orders."""
    status: Optional[OrderStatus] = None
    product_id: Optional[str] = None
    user_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

