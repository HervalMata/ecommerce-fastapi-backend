from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin, get_current_user
from app.db.database import db_session
from app.models.user import User
from app.schemas.user import PasswordUpdate, UserRead, UserUpdate
from app.schemas.response import ApiResponse
from app.services.user import (
    change_user_password,
    get_all_users_latest,
    update_user_profile,
    upload_profile_pix,
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> ApiResponse[UserRead]:

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Perfil carregado com sucesso",
        data=current_user,
    )

@router.get("/all-users", status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(db_session),
    admin: User = Depends(get_current_admin)
) -> ApiResponse[List[UserRead]]:
    users = await get_all_users_latest(db)

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Usuáriod carregados com sucesso",
        data=users,
    )    

@router.put("/update-profile", status_code=status.HTTP_200_OK)
async def update_my_profile(
    body_data = UserUpdate,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user)
) -> ApiResponse[UserRead]:
    update_user = await update_user_profile(db, current_user, body_data)

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Perfil atualizado com sucesso",
        data=update_user,
    )      

@router.put("/change-password", status_code=status.HTTP_200_OK)
async def update_my_password(
    body_data = PasswordUpdate,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user)
) -> ApiResponse[None]:
    await change_user_password(db, current_user, body_data)

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Senha atualizada com sucesso",
    )  

@router.post("/upload-avatar", status_code=status.HTTP_201_CREATED)
async def upload_profile_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user)
) -> ApiResponse[str]:
    file_path = await upload_profile_pix(db, current_user, file)

    return ApiResponse[str](
        status=status.HTTP_201_CREATED,
        message="Foto do Perfil atualizada com sucesso",
        data=file_path,
    )          