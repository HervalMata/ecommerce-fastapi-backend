from typing import Any

from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.db.database import db_session
from app.schemas.response import ApiResponse
from app.services.payment import fullfil_order_payment, cancel_order_payment

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/confirm", status_code=status.HTTP_200_OK)
async def confirm_payment(session_id: str, db: Session = Depends(db_session)) -> ApiResponse[Any]:
    order = await fullfil_order_payment(db, session_id)

    return ApiResponse[Any](
        status=status.HTTP_200_OK,
        message="Pagamento verificado e a ordem está agora sendo processada.",
        data=order,
    )

@router.get("/cancel", status_code=status.HTTP_200_OK)
async def cancel_payment(session_id: str, db: Session = Depends(db_session)) -> ApiResponse[Any]:
    order = await fullfil_order_payment(db, session_id)

    return ApiResponse[dict[str, int]](
        status=status.HTTP_200_OK,
        message="Pagamento foi cancelado. Você pode tentar novamente no seu historico de ordens.",
        data={"order_id": order.id},
    )    