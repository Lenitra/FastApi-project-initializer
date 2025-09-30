from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.utils.auth.auth import verify_password, create_access_token
from app.utils.core.config import settings
from app.utils.core.database import get_db
from app.repositories.auth.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])
user_repo = UserRepository()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = user_repo.get_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )

    access_token = create_access_token(
        user_id=user.id,
        active_role=user.active_role
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "active_role": user.active_role,
    }
