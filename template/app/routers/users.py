from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status

from sqlmodel import Session
from app.entities.auth.user import User
from app.repositories.auth.user_repository import UserRepository
from app.utils.core.database import get_db
from app.utils.auth.roles import get_current_user
from app.utils.auth.auth import create_access_token


router = APIRouter(prefix="/users", tags=["Users"])
user_repo = UserRepository()



@router.post("/switch-role/{role_id}")
def switch_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch to a different role (must be one of user's available roles)"""
    

    
    if not current_user.roles.__contains__(role_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have the '{role_id}' role. Available roles: {current_user.get_roles()}"
        )
    
    # Update active role in database
    current_user.active_role = role_id
    user_repo.save(db, current_user)  
    
    # Create new token with the new active role
    access_token = create_access_token(
        user_id=current_user.id,
        active_role=role_id
    )
    

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "all_roles": current_user.get_roles(),
        "message": f"Successfully switched to {role_id} role"
    }


@router.get("/me", response_model=User)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


# @router.get("/{id}", response_model=User)
# def get_user_by_id(
#     id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_roles(["admin", "manager"])),
# ):
#     """Get user by ID - Admin/Manager only"""
#     user = repo.get_by_id(db, id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


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
