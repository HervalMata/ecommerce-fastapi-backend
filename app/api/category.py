from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin
from app.db.database import db_session
from app.models.user import User
from app.schemas.category import CategorySchema
from app.schemas.response import ApiResponse
from app.services.category import (
    create_category,
    delete_category,
    get_all_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", status_code=status.HTTP_200_OK)
async def list_categories(db: Session = Depends(db_session)) -> ApiResponse[List[CategorySchema]]:
    categories = await get_all_categories(db)

    return ApiResponse[List[CategorySchema]](
        status=status.HTTP_200_OK,
        message="Categorias carregadas com sucesso",
        data=categories,
    )

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_category(
    category_data: CategorySchema,
    db: Session = Depends(db_session),
    _: User = Depends(get_current_admin)
) -> ApiResponse[CategorySchema]:
    created_category = await create_category(db, category_data)

    return ApiResponse[CategorySchema](
        status=status.HTTP_201_CREATED,
        message="Categorias criada com sucesso",
        data=created_category,
    )    

@router.put("", status_code=status.HTTP_200_OK)
async def edit_category(
    update_data_to_update: CategorySchema,
    db: Session = Depends(db_session),
    _: User = Depends(get_current_admin)
) -> ApiResponse[List[CategorySchema]]:
    updated_category_result = await update_category(db, update_data_to_update)

    return ApiResponse[CategorySchema](
        status=status.HTTP_200_OK,
        message="Categorias atualizada com sucesso",
        data=updated_category_result,
    )       

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def remove_category(
    category_id: int,
    db: Session = Depends(db_session),
    _: User = Depends(get_current_admin)
) -> ApiResponse[None]:
    await delete_category(db, category_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Categorias removida com sucesso",
    )       