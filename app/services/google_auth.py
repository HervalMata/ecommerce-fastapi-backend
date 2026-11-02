import secrets
import string
import httpx

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User, UserRole

async def process_google_callback_workflow(db: Session, code: str) -> User:
    print("🔄 Preparando código para token de acesso...")
    token_data = await exchange_code_for_token(code)
    access_token = token_data.get("access_token")

    if not access_token:
        raise ApiException(
            f"Falha em conseguir um token de acesso de resposta do Google: {token_data}"
        )

    print(f"✅ Token de Acesso Obtido")    
    print("🔄 Carregandon informações do usuário")
    user_info = await get_user_info(access_token)

    print(f"📧 Email do Usuário: {user_info.get('email')}")

    if not user_info.get('email'):
        raise ApiException(
            "Usuário do Google com perfil carregado teve chave de verificação de email perdida"
        )

    user = await get_or_create_user_from_google(db, user_info)

    return user

async def exchange_code_for_token(code: str):
    """Exchange authorization code for access token"""

    token_url = "https://oauht2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_url": f"{settings.BACKEND_URL}/api/auth/google/callback",
        "grant_type": "authorization_code",
    }        

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        return response.json()


async def get_user_info(access_token: str):
    """Get User info from Google using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()

async def get_or_create_user_from_google(db: Session, user_data: dict):
    """Get Existing User or Create new one from Google data"""
    email = user_data.get("email")
    name = user_data.get("name")
    picture = user_data.get("picture")

    print(f"Processando dados do usuário do Google - Email: {email}, Nome: {name}")

    if not email:
        raise ApiException("Nenhum email entregue pelo Google")        

    statement = select(User).where(User.email == email)    
    result = await db.exec(statement)
    user = result.first()

    if not user:
        random_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
        from app.services.user import password_hasher
        hashed_password = password_hasher.hash(random_password)

        user = User(
            email=email,
            name=name or email.split("@")[0],
            hashed_password=hashed_password,
            role=UserRole.CUSTOMER,
            profile_picture=picture,
            active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ Criado novo usuário: {email} (ID: {user.id})")
    else:
        print(f"✅ Encontrado usuário existente: {email} (ID: {user.id})")    

    return user    

async def generate_user_token(user: User):
    """Generate JWT token for user"""
    return create_access_token(data={"sub": str(user.id), "role": user.role})    