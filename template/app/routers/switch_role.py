from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.utils.auth.auth import create_access_token
from app.utils.core.config import settings
from app.utils.core.database import get_db
from app.utils.auth.roles import get_current_user

router = APIRouter()


@router.post("/switch-role/{role_name}")
def switch_role(
    role_name: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch to a different role (must be one of user's available roles)"""
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if not current_user.has_role(role_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have the '{role_name}' role. Available roles: {current_user.get_roles()}"
        )
    
    # Update active role in database
    current_user.set_active_role(role_name)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # Create new token with the new active role
    access_token = create_access_token(
        user_id=current_user.id,
        email=current_user.email,
        role=role_name,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "active_role": role_name,
        "all_roles": current_user.get_roles(),
        "message": f"Successfully switched to {role_name} role"
    }


@router.get("/current-role")
def get_current_role_info(current_user=Depends(get_current_user)):
    """Get current user role information"""
    return {
        "active_role": current_user.active_role,
        "all_roles": current_user.get_roles(),
        "email": current_user.email
    }