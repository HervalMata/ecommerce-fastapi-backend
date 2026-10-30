from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .product import Product

class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    
    user: "User" = Relationship(back_populates="orders")
    items: List["CartItem"] = Relationship(back_populates="cart")

class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1)
    
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    
    cart: "Cart" = Relationship(back_populates="items")
    product: "Product" = Relationship()    