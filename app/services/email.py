from pathlib import Path
from typing import Any

import aiosmtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.exceptions import ApiException
from app.models import Order

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

async def _send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: dict[str, Any],
    fallback_text: str | None = None,
    raise_on_error: bool = False,
) -> None:
    """Send an email using a Jinja2 template."""
    
        # Render the email template with the provided context
    template = jinja_env.get_template(template_name)
    html_content = template.render(context)

        # Create the email message
    message = EmailMessage()
    message["From"] = settings.MAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
        
    try:
        template = jinja_env.get_template(template_name)
        html_content = template.render(**context)
        message.add_alternative(html_content, subtype="html")
    except Exception as e:
        print(f" ⚠️ Template Error [{template_name}]: {e}")
        if fallback_text:
            message.set_content(fallback_text)
        else:
            if raise_on_error:
                raise ApiException(
                    message=f"Template rendering failed: {e}", status_code=500
                )
            return        
                

        # Send the email using aiosmtplib
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            start_tls=True,
        )
        print(f"✅ Email [{subject}] enviado com sucesso para {to_email}")
    except Exception as e:
        print(f"❌ SMTP Error enviando [{subject}] para {to_email}: {e}")
        if raise_on_error:
            raise ApiException(
                message=f"Failed to send email: {str(e)}",
                status_code=500,
            )
                
async def send_welcome_email(email: str, name: str) -> None:
    await _send_email(
        to_email=email,
        subject="Bemvindo para a Cris Laços",
        template_name="welcome.html",
        context={"name": name, "frontendUrl": settings.FRONTEND_URL},
        fallback_text=f"Olá {name}, Benvindo para a Cris Laços",
        raise_on_error=True,
    )      
    
async def send_reset_password_email(email: str, name: str, code: str, reset_url: str) -> None:
    await _send_email(
        to_email=email,
        subject="Requisição de recupaeração de Senha - Ação Requerida",
        template_name="reset_password.html",
        context={"name": name, "code": code, "reset_url": reset_url},
        fallback_text=f"Olá {name}, seu código para recuperar sua senha é: {code}, link: {reset_url}",
        raise_on_error=True,
    )   
    
async def send_order_status_update_email(email: str, name: str, order: Order) -> None:
    await _send_email(
        to_email=email,
        subject=f"Atualização: Ordem #{order.id} está agora {order.status.value}",
        template_name="order-status.html",
        context={
            "name": name, 
            "order_id": order.id,
            "status": order.status.value.upper(),
            "address": order.shipping_address,
            "total_price": order.total_price,
            "items": order.items,
        },
    )     
    
async def send_order_confirmation_email(email: str, name: str, order: Order) -> None:
    await _send_email(
        to_email=email,
        subject=f"Confirmação: Ordem #{order.id}",
        template_name="order-confirmation.html",
        context={
            "name": name, 
            "order_id": order.id,
            "address": order.shipping_address,
            "total": order.total_price,
        },
    )     
    
async def notify_delivery_team_of_order(customer_name: str, order: Order) -> None:
    payment_status = order.payment.status if order.payment else "unknown"
    order_date = order.created_at.strftime("%d-%m-%Y %H:%M") if order.created_at else ""
    
    await _send_email(
        to_email=settings.DELIVERY_PERSON_EMAIL,
        subject=f"🚨 Nova Ordem Receboda: #{order.id}",
        template_name="delivery_person_order_notification.html",
        context={
            "customer_name": customer_name, 
            "order_id": order.id,
            "order_status": order.status,
            "payment_status": payment_status,
            "address": order.shipping_address,
            "total": order.total_price,
            "items": order.items,
            "order_date": order_date,
        },
    )        
    
async def send_payment_notification(
    email: str, 
    name: str, 
    order_id: int, 
    status: str, 
    amount: str | None = None,
    error: str | None = None,
) -> None:
    is_success = status = "sucesso"
    template_name = "payment-success.html" if is_success else "payment-failed.html"
    subject = (
        f"Pagamento Realizado com sucesso - Ordem #{order_id}"
        if is_success
        else f"Pagamento Não Realizado - Ordem #{order_id}"
    )
    
    await _send_email(
        to_email=email,
        subject=subject,
        template_name=template_name,
        context={
            "name": name, 
            "order_id": order_id,
            "amount": amount,
            "currency": "BRL",
            "error_message": error,
        }
    )              