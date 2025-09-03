from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from app.entities.auth.user import User
from app.repositories.auth.user_repository import UserRepository
from app.utils.core.database import get_db
from app.utils.auth.roles import require_admin, require_roles, get_current_user

router = APIRouter()
repo = UserRepository()


@router.get("/", response_model=list[User])
def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """Get all users - Admin only"""
    return repo.list(db)


@router.get("/me", response_model=User)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.get("/by-role/{role}", response_model=list[User])
def get_users_by_role(
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get users by role - Admin only"""
    return repo.get_by_role(db, role)


@router.get("/{id}", response_model=User)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "manager"])),
):
    """Get user by ID - Admin/Manager only"""
    obj = repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="User not found")
    return obj


@router.post("/", response_model=User, status_code=201)
def save_user(
    user_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create or update user - Admin only"""
    return repo.save(db, user_data)


@router.delete("/{id}", status_code=204)
def delete_user(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """Delete user - Admin only"""
    ok = repo.delete(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
