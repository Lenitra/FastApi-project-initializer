from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from app.entities.auth.role import Role
from app.repositories.auth.role_repository import RoleRepository
from app.utils.core.database import get_db
from app.utils.auth.roles import require_admin

router = APIRouter()
repo = RoleRepository()


@router.get("/", response_model=list[Role])
def get_all_roles(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Get all roles - Admin only"""
    return repo.list(db)


@router.get("/active", response_model=list[Role])
def get_active_roles(db: Session = Depends(get_db)):
    """Get active roles - Public endpoint"""
    return repo.get_active_roles(db)


@router.get("/{id}", response_model=Role)
def get_role_by_id(
    id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    """Get role by ID - Admin only"""
    obj = repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return obj


@router.post("/", response_model=Role, status_code=201)
def save_role(
    role_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create or update role - Admin only"""
    return repo.save(db, role_data)


@router.delete("/{id}", status_code=204)
def delete_role(
    id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    """Delete role - Admin only"""
    ok = repo.delete(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Role not found")
