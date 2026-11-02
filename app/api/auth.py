from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import db_session

from app.schemas.response import ApiResponse
from app.schemas.user import (
    UserCreate,
    UserRead
)
from app.services.user import register_new_user



router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(db_session)) -> ApiResponse[UserRead]:
    
    user = await register_new_user(db=db, user_data=user_data)
    
    return ApiResponse[UserRead](
        status=status.HTTP_201_CREATED,
        message="Usuário registrado com sucesso",
        data=user,
    )