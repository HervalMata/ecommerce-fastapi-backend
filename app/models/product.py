from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .category import Category
    from .order_item import OrderItem
    from .review import Review


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: Decimal = Field(default=0.00, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0)
    
    image_url: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    category_id: Optional[int] = Field(foreign_key="categories.id")
    
    category: Optional["Category"] = Relationship(back_populates="products")
    
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    
    reviews: List["Review"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
        