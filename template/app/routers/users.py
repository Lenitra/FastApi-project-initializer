from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from app.entities.auth.user import User
from app.repositories.auth.user_repository import UserRepository
from app.utils.core.database import get_db
from app.utils.auth.roles import require_admin, require_roles, get_current_user
from typing import List

router = APIRouter()
repo = UserRepository()


@router.get("/", response_model=List[User])
def get_all_users(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_admin)
):
    """Get all users - Admin only"""
    return repo.get_all(db)


@router.get("/me", response_model=User)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.get("/{id}", response_model=User)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "manager"])),
):
    """Get user by ID - Admin/Manager only"""
    user = repo.get_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# @router.post("/", response_model=User, status_code=201)
# def create_user(
#     user_data: dict = Body(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_admin),
# ):
#     """Create user - Admin only"""
#     return repo.create(db, user_data)


# @router.put("/{id}", response_model=User)
# def update_user(
#     id: int,
#     user_data: dict = Body(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_admin),
# ):
#     """Update user - Admin only"""
#     user = repo.get_by_id(db, id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return repo.update(db, id, user_data)


# @router.delete("/{id}")
# def delete_user(
#     id: int, 
#     db: Session = Depends(get_db), 
#     current_user: User = Depends(require_admin)
# ):
#     """Delete user - Admin only"""
#     user = repo.get_by_id(db, id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     repo.delete(db, id)
#     return {"message": "User deleted successfully"}
