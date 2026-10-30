from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .order import Order
    from .product import Product

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1)
    
    unit_price: Decimal = Field(default=0.00, max_digits=10, decimal_places=2)
    
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")