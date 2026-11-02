from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_user
from app.db.database import db_session
from app.models.user import User
from app.schemas.cart import AddToCartRequest, CartRead
from app.schemas.response import ApiResponse
from app.services.cart import (
    add_item_to_cart,
    clear_user_cart,
    decrement_item_quantity,
    get_user_cart,
    remove_item_from_cart,
)

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("", status_code=status.HTTP_200_OK)
async def view_cart(db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ApiResponse[CartRead]:
    cart = await get_user_cart(db, user.id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Carrinho carregado", data=cart,
    )

@router.post("/add", status_code=status.HTTP_200_OK)
async def add_to_cart(req: AddToCartRequest, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ApiResponse[CartRead]:
    await add_item_to_cart(db, user.id, req.product_id, req.quantity)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Itens adicionados ao Carrinho"
    )    

@router.post("/decrement/{product_id}", status_code=status.HTTP_200_OK)
async def decrement_cart_item(product_id: int, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ApiResponse[CartRead]:
    await decrement_item_quantity(db, user.id, product_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Itens com quantidade diminuida no Carrinho"
    )     

@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
async def remove_from_cart(product_id: int, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ApiResponse[CartRead]:
    await remove_item_from_cart(db, user.id, product_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Itens removido do Carrinho"
    )    

@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_cart(db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ApiResponse[CartRead]:
    await clear_user_cart(db, user.id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Carrinho está vazio"
    )          