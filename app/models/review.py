from datetime import datetime
from time import timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .product import Product

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int = Field(default=5, ge=1, le=5)
    comment: str
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    user_id: int = Field(foreign_key="users.id")
    product_id: int = Field(foreign_key="products.id")
    
    user: "User" = Relationship(back_populates="reviews")
    product: "Product" = Relationship(back_populates="reviews")