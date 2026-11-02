import traceback

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from urllib.parse import urlencode
from app.core.config import settings
from app.db.database import db_session
from app.schemas.response import ApiResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenData,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.google_auth import generate_user_token, process_google_callback_workflow
from app.services.user import login_user, process_forgot_password, process_reset_password, register_new_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(db_session)) -> ApiResponse[UserRead]:
    user = await register_new_user(db, user_data)

    return ApiResponse[UserRead](
        status=status.HTTP_201_CREATED,
        message="Usuário registrado com sucesso",
        data=user,
    )

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_data: UserLogin, db: Session = Depends(db_session)) -> ApiResponse[TokenData]:
    token_info = await login_user(db, login_data)

    return ApiResponse[TokenData](
        status=status.HTTP_200_OK,
        message="Usuário logado com sucesso",
        data=token_info,
    )   

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(db_session)) -> ApiResponse[None]:
    await process_forgot_password(db, request.email)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Link de Recuperação de Senha enviado com sucesso",
    )     

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(db_session)) -> ApiResponse[None]:
    await process_reset_password(db, request)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Senha Recuperada com sucesso",
    )     

@router.get("/google")
async def google_login():
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_url': f"{settings.BACKEND_URL}/api/auth/google/callback",
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'offline',
    }     

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    print(f"🔐 Google login iniciado")
    print(f" Redirect URI: {params['redirect_url']}")

    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_callbck(request: Request, code: str = None, db: Session = Depends(db_session)):
    print("=" * 60)
    print("📞 Google Chamada Recebida")

    error = request.query_params.get('error')

    if error:
        print(f"❌ Google Erro Retornado: {error}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error={error}")    

    if error:
        print(f"❌ Nenhum código de autorização recebido")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error=Nenhum código de autorização")

    try:
        user = await process_google_callback_workflow(db, code)

        auth_token = await generate_user_token(user)
        print(f"🔑 JWT Token gerado para o ID do Usuário: {user.id}, Função: {user.role}")

        redirect_url = f"{settings.FRONTEND_URL}/auth-success/token={auth_token}&role={user.role}"
        print(f"🔄 Redirecionando para: {redirect_url}")
        print("=" * 60)          
        return  RedirectResponse(url=redirect_url)

    except ValueError as val_err:
        print(f"⚠️ Erro de validação encontrado durante OAuth: {val_err}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error={str(val_err)}")   

    except ValueError as e:
        print(f"❌ Erro Em fluxo de Chamada da Google: {str(e)}")
        traceback.print.exec()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error=Inexperado falha no processo de requisição de autenticação")       