from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_auth_data
from app.crud.users import user_crud
from app.models import User


def create_access_token(data: dict) -> str:
    """Возвращает токен."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=366)
    to_encode.update({'exp': expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm']
    )
    return encode_jwt


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    """Возвращает хешированый пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    email: EmailStr, password: str, session: AsyncSession
) -> User | None:
    """
    Проверка наличия юзера в базе и соответствия пароля.
    """
    user = await user_crud.find_one_or_none(email=email, session=session)
    if not user or verify_password(
        plain_password=password, hashed_password=user.password
    ) is False:
        return None
    return user
