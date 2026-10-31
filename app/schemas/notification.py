from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.notification import NotificationType

class NotificationRead(BaseModel):
    id: int
    recipient_email: str
    notification_type: NotificationType
    message: str
    title: str
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )