from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from app.utils.auth.auth import decode_access_token
from app.utils.core.database import get_db
from app.repositories.auth.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Get current authenticated user"""
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


def get_current_user_role(token: str = Depends(oauth2_scheme)):
    """Get current user role from JWT token directly (no DB query)"""
    try:
        payload = decode_access_token(token)
        role = payload.get("role")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no role found",
            )
        return role
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


def require_role(required_role: str):
    """Decorator to require specific role from JWT token"""
    def role_checker(current_role: str = Depends(get_current_user_role)):
        if current_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: {required_role} role required, got {current_role}",
            )
        return current_role

    return role_checker


def require_roles(required_roles: List[str]):
    """Decorator to require one of multiple roles from JWT token"""
    def role_checker(current_role: str = Depends(get_current_user_role)):
        if current_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: one of {required_roles} roles required, got {current_role}",
            )
        return current_role

    return role_checker


def require_admin(current_role: str = Depends(get_current_user_role)):
    """Shortcut for admin role requirement"""
    if current_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin access required, got {current_role}",
        )
    return current_role


def require_active_user(current_user=Depends(get_current_user)):
    """Require user to be active (needs DB query)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
