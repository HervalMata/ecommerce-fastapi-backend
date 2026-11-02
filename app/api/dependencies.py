from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.exceptions import ApiException
from app.core.security import decode_access_token
from app.db.database import db_session
from app.models.user import User, UserRole

http_bearer = HTTPBearer()

async def get_current_user(
    db: Session = Depends(db_session),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> User:
    payload = decode_access_token(token.credentials)
    user_id: str = payload.get("sub")

    if not user_id:
        raise ApiException("Não foi possivel validar suas credênciais", status.HTTP_401_UNAUTHORIZED)

    statement = select(User).where(User.id == int(user_id))
    result = await db.exec(statement)
    user = result.first()    

    if not user:
        raise ApiException("Usuário não encontrado", status.HTTP_404_NOT_FOUND)

    if not user.active:
        raise ApiException("Usuário inativo", status.HTTP_400_BAD_REQUEST)    

    return user    

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:    
    if current_user.role != UserRole.ADMIN:
        raise ApiException("Você não tem privilégios administrativos", status.HTTP_403_FORBIDDEN)

    return current_user

async def get_current_admin_or_delivery(
    current_user: User = Depends(get_current_user)
) -> User:    
    if current_user.role not in [UserRole.ADMIN, UserRole.DELIVERY]:
        raise ApiException("Você não tem permissão para acessar este recurso", status.HTTP_403_FORBIDDEN)

    return current_user    