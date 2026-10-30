from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field
from enum import Enum

class NotificationType(str, Enum):
    WELCOME = "welcome"
    ORDER_UPDATE = "order_update"
    PAYMENT_UPDATE = "payment_update"
    PROMOTIONAL = "promotional"
    SECURITY = "security"

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    recipient_email: str = Field(index=True)
    
    title: str = Field()
    message: str = Field()
        
    notification_type: NotificationType = Field(default=NotificationType.ORDER_UPDATE)
    
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))