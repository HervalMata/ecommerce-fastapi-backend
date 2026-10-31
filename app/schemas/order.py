from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, compute_field, model_validator
from pydantic.alias_generators import to_camel

from sqlmodel import Field

from app.models.order import OrderStatus

class CheckoutRequest(BaseModel):
    shipping_address: str
    
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    
    
class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = Field(default=None, alias="productName")
    quantity: int
    unit_price: Decimal
    is_reviewed: bool
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )      
    
    @model_validator(mode="before")
    @classmethod
    def map_fields_from_relationship(cls, data):
        if hasattr(data, "product"):
            return {
                "id": data.id,
                "product_id": data.product_id,
                "product_name": data.product.name if data.product else "unknown",
                "quantity": data.quantity,
                "unit_price": data.unit_price,
                "is_reviewed": data.is_reviewed
            }
        return data
    
    @compute_field
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
    
class OrderRead(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_price: Decimal
    shipping_address: str
    created_at: datetime
    items: List[OrderItemRead] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )   