from datetime import datetime, timedelta, timezone

import jwt

from fastapi import status
from app.core.config import settings
from app.core.exceptions import ApiException

ALGORITHM = "HS256"
SECRET_JWT_KEY = settings.SECRET_JWT_KEY
ACCESS_TOKEN_EXPIRE_DAYS = 30

if not SECRET_JWT_KEY:
    raise ApiException(
        message="SECRET_JWT_KEY is not set in the environment variables.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt    

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ApiException(
            message="Token has expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.InvalidTokenError:
        raise ApiException(
            message="Invalid token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )