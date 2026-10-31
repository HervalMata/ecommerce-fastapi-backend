from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CheckoutSessionRequest(BaseModel):
    order_id: int
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
    
class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )    