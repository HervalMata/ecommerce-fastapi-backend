from app.core.exceptions import ApiException
from app.models.user import User
from app.schemas.user import (
    UserCreate
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status
from app.services.email import send_welcome_email
from pwdlib import PasswordHash  # pyright: ignore[reportMissingImports]

password_hasher = PasswordHash.recommended()


async def register_new_user(db: AsyncSession, user_data: UserCreate):
    statement = select(User).where(User.email == user_data.email)
    existing_user = await db.scalar(statement)
    
    if existing_user:
        raise ApiException(
            message="Usuário com este email já existe",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    hashed_password = password_hasher.hash(user_data.password)    
    
    user_object = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        role=user_data.role,
    )
    
    db.add(user_object)
    await db.commit()
    await db.refresh(user_object)
    
    await send_welcome_email(user_object.email, user_object.name)
    return user_object
    