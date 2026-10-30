from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .order_item import OrderItem
    from .payment import Payment

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    total_price: Decimal = Field(default=0.00, max_digits=10, decimal_places=2)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    shipping_address: str = Field()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    user_id: int = Field(foreign_key="users.id")
    
    user: "User" = Relationship(back_populates="orders")
    payment: Optional["Payment"] = Relationship(back_populates="order")
    items: List["OrderItem"] = Relationship(back_populates="order")