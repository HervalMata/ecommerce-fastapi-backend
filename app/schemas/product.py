from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.review import ReviewResponse

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    category_id: int
    
    image_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        exclude_none=True,
        alias_generator=to_camel,
        populate_by_name=True
    )
    
class ProductDetail(BaseModel):
    reviews: List[ReviewResponse] = []  
    
class ProductUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None

 