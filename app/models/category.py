from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .product import Product

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    
    products: list["Product"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )