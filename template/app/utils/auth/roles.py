from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from app.utils.auth.auth import decode_access_token
from app.utils.core.database import get_db
from app.repositories.auth.user_repository import UserRepository
from app.entities.auth.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Récupère l'utilisateur actuel à partir du sub (mail) du token JWT.
    """
    try:
        payload = decode_access_token(token)
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        user_repo = UserRepository()
        user = user_repo.get_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )




def require_role(permited_role: List[str]):
    """Decorator to require one of multiple roles from JWT token"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.active_role not in permited_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: one of {permited_role} roles required, got {current_user.active_role}",
            )
        return current_user.active_role

    return role_checker



