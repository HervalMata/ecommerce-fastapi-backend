from datetime import datetime, timezone, tzinfo
from pathlib import Path
import secrets
import string
from unittest import result

from pwdlib import PasswordHash
from requests import delete
from sqlmodel import Session, desc, select
from fastapi import UploadFile, status
from app.core.config import settings

from app.core.exceptions import ApiException
from app.core.security import create_access_token
from app.models.reset_code import ResetCode
from app.models.user import User
from app.schemas.user import PasswordUpdate, ResetPasswordRequest, TokenData, UserCreate, UserLogin, UserUpdate
from app.services.email import send_reset_password_email, send_welcome_email
from app.services.upload import upload_file, upload_file_to_frontend, upload_to_s3

password_hasher = PasswordHash.recommended()

async def register_new_user(db: Session, user_data: UserCreate):
    statement = select(User).where(User.email == user_data.email)

    result = await db.exec(statement)

    if result.first():
        raise ApiException(
            message="Usuário já existe com este email",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    hashed_password = password_hasher.hash(user_data.password)    

    user_to_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        role=user_data.role,
    )

    db.add(user_to_user)
    await db.commit()
    await db.refresh(user_to_user)

    await send_welcome_email(user_to_user.email, user_to_user.name)

    return user_to_user

async def login_user(db: Session, login_data: UserLogin):
    statement = select(User).where(User.email == login_data.email)    
    result = await db.exec(statement)
    user = result.first()

    if not user or not password_hasher.verify(login_data.password, user.hashed_password):
        raise ApiException(
            message="Email e/ou senha invalidos",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenData(token=token, user=user)    

async def process_forgot_password(db: Session, email: str):
    statement = select(User).where(User.email == email)    
    result = await db.exec(statement)
    user = result.first()

    if not user:
        raise ApiException("Usuário não encontrado com este email", status.HTTP_404_NOT_FOUND)

    unique_code = False
    code = ""

    while not unique_code:
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        code_statement = select(ResetCode).where(ResetCode.code == code)
        existing_code = (await db.exec(code_statement)).first()

        if not existing_code:
            unique_code = True

    reset_entry = ResetCode(email=email, code=code)
    db.add(reset_entry)
    await db.commit()

    reset_url = f"{settings.RESET_PASSWORD_URL}{code}"

    await send_reset_password_email(email, user.name, code, reset_url)
    return True

async def process_reset_password(db: Session, reset_data: ResetPasswordRequest):
    statement = select(ResetCode).where(ResetCode.code == reset_data.code)
    reset_entry = (await db.exec(statement)).first()

    if not reset_entry:
        print(f"DEBUG: Reset Code '{reset_data.code}' not found in database.")
        raise ApiException("Código de recuperação invalido", status.HTTP_404_BAD_REQUEST)

    print(f"DEBUG: Found Code. Expires at: {reset_entry.expires_at}, Current time: {datetime.now(timezone.utc)}")

    current_time = datetime.now(timezone.utc)
    expiry_time = reset_entry.expires_at

    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    if current_time > expiry_time:
        print(f"DEBUG: Reset Code '{reset_data.code}' expired")
        raise ApiException("Código de recuperação expirado", status.HTTP_404_BAD_REQUEST)    

    user_stmt = select(User).where(User.email == reset_entry.email)    
    user = (await db.exec(user_stmt)).first()

    if not user:
        print(f"DEBUG: User with email {reset_entry.email} no longer exists")
        raise ApiException("Usuário não existe mais", status.HTTP_404_NOT_FOUND)

    user.hashed_password = password_hasher.hash(reset_data.password)
    await db.execute(delete(ResetCode).where(ResetCode.email == reset_entry.email))

    await db.commit()
    return True    

async def get_all_users_latest(db: Session):
    statement = (await db.exec(User)).order_by(desc(User.id))
    result = await db.exec(statement)
    return result.all()

async def update_user_profile(db:Session, user: User, update_data: UserUpdate):
    if update_data.name:
        user.name = update_data.name

    if update_data.address:
        user.address = update_data.address   

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def change_user_password(db: Session, user: User, password_data: PasswordUpdate):
    if not password_hasher.verify(password_data.old_password, user.hashed_password):
        raise ApiException("Senha Antiga está incorreta", status.HTTP_400_BAD_REQUEST)

    user.hashed_password = password_hasher.hash(password_data.new_password)
    db.add(user)
    await db.commit()
    return True

async def upload_profile_pix(db:Session, user: User, file: UploadFile):
    UPLOAD_DIR_FRONTEND = Path("E:/Projects/ecommerce-fastapi-backend/public/profile")

    UPLOAD_DIR = Path("uploads/profile")

    image_path = await upload_file(file, UPLOAD_DIR)

    # image_path = await upload_to_s3(file, UPLOAD_DIR)    

    # image_path = await upload_file_to_frontend(file, UPLOAD_DIR_FRONTEND)

    user.profile_picture = image_path

    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return image_path

                    