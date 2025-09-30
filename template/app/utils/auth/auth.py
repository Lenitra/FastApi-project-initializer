from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.utils.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: int, active_role: int) -> str:
    to_encode = {"sub": str(user_id), "active_role": str(active_role)}
    expire = datetime.utcnow() + (
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    print(f"Decoding token: {token}")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_id = payload.get("sub")
    active_role = payload.get("active_role")
    if user_id is None or active_role is None:
        print(f"Decoded payload missing user_id or active_role: {payload}")
        raise JWTError("Missing user_id or active_role in token")

    print(f"Decoded token for user_id: {user_id}, active_role: {active_role}")
    return {"active_role": active_role, "sub": user_id}