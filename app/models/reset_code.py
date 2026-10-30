from datetime import datetime, timedelta
from time import timezone
from typing import Optional

from sqlmodel import SQLModel, Field

class ResetCode(SQLModel, table=True):
    __tablename__ = "reset_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    code: str = Field(index=True, unique=True)
    
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)+ timedelta(hours=5))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))