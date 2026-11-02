from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlmodel import Session
from app.api.dependencies import get_current_admim, get_current_user
from app.db.database import db_session
from app.schemas.response import ApiResponse
from app.services.product import create_product, delete_product,get_all_products, get_product_by_id, update_product

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", status_code=status.HTTP_200_OK)
async def list_products(category_id: Optional[int] = None, db: Session = Depends(db_session)) -> ApiResponse[List[ProductRead]]:
    products = await get_all_products(db, category_id)

    return ApiResponse[List[ProductRead]](
        status=status.HTTP_200_OK,
        message="Produtos carregados com sucesso",
        data=products,
    )

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(db_session)) -> ApiResponse[ProductDetail]:
    product = await get_product_by_id(db, product_id)

    return ApiResponse[ProductDetail](
        status=status.HTTP_200_OK,
        message="Detalhes do Produto carregados com sucesso",
        data=product,
    )    

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_id: int = Form(...), 
    file: UploadFile = Form(...), 
    db: Session = Depends(db_session),
    admin = Depends(get_current_admin)
) -> ApiResponse[ProductRead]:
    product = await create_product(db, name, description, price, stock_quantity, category_id, file)

    return ApiResponse[ProductRead](
        status=status.HTTP_201_CREATED,
        message="Produto criado com sucesso",
        data=product,
    )       

@router.put("/update", status_code=status.HTTP_200_OK)
async def edit_product(
    id: str = Form(...),
    name: Optional[str] = Form(...),
    description: Optional[str]  = Form(...),
    price: Optional[float] = Form(...),
    stock_quantity: Optional[int] = Form(...),
    category_id: Optional[int] = Form(...), 
    file: Optional[UploadFile] = Form(...), 
    db: Session = Depends(db_session),
    admin = Depends(get_current_admin)
) -> ApiResponse[ProductRead]:
    update_data = ProductUpdate(
        id=id, name=name, description=description, price=price, stock_quantity=stock_quantity, category_id=category_id,
    )
    product = await update_product(db, update_data, file)

    return ApiResponse[ProductRead](
        status=status.HTTP_200_OK,
        message="Produto atualizado com sucesso",
        data=product,
    )       

@router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(db_session)) -> ApiResponse[None]:
    product = await get_product_by_id(db, product_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Produto removido com sucesso",
    )        