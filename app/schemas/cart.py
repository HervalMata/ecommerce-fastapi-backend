from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CartItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    product_image: Optional[str]
    product_price: Decimal
    subtotal: Decimal
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
    
class CartRead(BaseModel):
    id: int
    user_id: int
    items: List[CartItemRead]
    total_price: Decimal
    total_quantity: int
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
    
class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )    