from time import strftime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel

from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[UserRole] = UserRole.CUSTOMER
    
class UserRead(BaseModel):
    
    id: int
    email: str
    name: str
    role: UserRole
    active: bool
    profile_picture: Optional[str] = None
    address: Optional[str] = None 
    
    model_config = ConfigDict(
        alias_generator=to_camel, 
        populate_by_name=True,
        from_attributes=True,
    )
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str    
    
class TokenData(BaseModel):
    token: str
    type: str = "bearer"
    user: UserRead  
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None    
    
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class ResetPasswordRequest(BaseModel):
    code: str
    password: str
        