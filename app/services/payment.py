from decimal import Decimal

from sqlmodel import Session, select
import stripe
from sqlalchemy.orm import selectinload
from fastapi import status
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.exceptions import ApiException
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment, PaymentStatus
from app.services.cart import clear_user_cart
from app.services.email import notify_delivery_team_of_order, send_order_confirmation_email, send_payment_notification

async def create_stripe_checkout_session(db: Session, order_id: int):
    statement = (select(Order).where(Order.id == order_id).options(selectinload(Order.items).selectinload(OrderItem.product)))
    result = await db.exec(statement)
    order = result.first()

    if not order:
        raise ApiException("Ordem não encontrada", 404)

    line_items = []
    for item in order.items:
        line_items.append(
            {
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": item.product.name},
                    "unit_amount": int(item.unit_price * 100),
                },
                "quantity": item.quantity,
            }
        )    

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        api_key=settings.STRIPE_SECRET_KEY,
        success_url=f"{settings.PAYMENT_CONFIRMATION_URL}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.PAYMENT_CANCEL_URL}?session_id={{CHECKOUT_SESSION_ID}}",
        metadata={"order_id": str(order.id)},
    )    
    return session.url, session.id

async def fullfil_order_payment(db: Session, session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(
            session_id, api_key=settings.STRIPE_SECRET_KEY
        )   
    except stripe.error.StripeError as e:
        raise ApiException(f"Erro na sessão do Stripe: {str(e)}", 400)    

    order_id = int(session.metadata["order_id"])

    statement = (select(Order).where(Order.id == order_id).options(selectinload(Order.user), selectinload(Order.payment), selectinload(Order.items)))
    result = await db.exec(statement)
    order = result.first()    

    if not order:
        raise ApiException("Ordem #{order_id} não encontrada nos arquivos", 404)

    if order.status == OrderStatus.PROCESSING:
        return order

    if session.payment_status == "paid":
        try:
            payment = Payment(
                amount=Decimal(session.amount_total / 100),
                provider_transaction_id=session.payment_intent,
                payment_method="card",
                status=PaymentStatus.COMPLETED,
                order_id=order.id,
            )        

            order_status = OrderStatus.PROCESSING

            db.add(payment)
            db.add(order)

            await clear_user_cart(db, order.user_id)
            await db.commit()
            await db.refresh(order)

        except IntegrityError:
            await db.rollback()
            raise ApiException(f"Opagamento para a ordem #{order.id} já foi finalizado com sucesso.", status.HTTP_400_BAD_REQUEST)    

        except Exception as e:
            await db.rollback()
            raise ApiException(f"Um inexperado erro cocorreu: {str(e)}", 500)     

        await send_order_confirmation_email(order.user.email, order.user.name, order)

        await send_payment_notification(
            email=order.user.email,
            name=order.user.name,
            order_id=order.id,
            status="success",
            amount=f"{payment.amount:.2f}",
        )    

        await notify_delivery_team_of_order(
            order, order.user.name
        )
        return order

    else:
        await send_payment_notification(
            email=order.user.email,
            name=order.user.name,
            order_id=order.id,
            status="failed",
            error="Seu cartão foi declinado ou a transação foi cancelada.",
        )

        raise ApiException("Pagamento não obteve êxito. Por favor tyente novamente.", 400)

async def cancel_order_payment(db: Session, session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(
            session_id, api_key=settings.STRIPE_SECRET_KEY
        )   
    except stripe.error.StripeError as e:
        raise ApiException(f"Erro na sessão do Stripe: {str(e)}", 400)       

    order_id = int(session.metadata["order_id"])

    statement = (select(Order).where(Order.id == order_id).options(selectinload(Order.user)))
    result = await db.exec(statement)
    order = result.first() 

    if not order:
        raise ApiException("Ordem #{order_id} não encontrada nos arquivos", 404)   


    if order.status == OrderStatus.PROCESSING:
        return order

    if session.payment_status != "paid":
        try: 
            payment_id = session.payment_intent or f"Cancelado_{session.id}"

            payment = Payment(
                amount=(Decimal(session.amount_total / 100) if session.amount_total else Decimal(0)),
                provider_transaction_id=session.payment_intent,
                payment_method="card",
                status=PaymentStatus.FAILED,
                order_id=order.id,
            )        
            
            order_status = OrderStatus.CANCELLED
            
            db.add(payment)
            db.add(order)    

            await db.commit()
            await db.refresh(order)

            await send_payment_notification(
                email=order.user.email,
                name=order.user.full_name,
                order_id=order.id,
                status="cancelled",
                error="O processo de pagamento foi cancelado ou sem sucesso.",
            )    

        except IntegrityError:
            await db.rollback()
            return order
        
        except Exception as e:
            await db.rollback()
            raise ApiException(f"Um inexperado erro cocorreu durante o cancelamento: {str(e)}", 500) 

    return order     