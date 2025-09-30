from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.entities.auth.role import Role
from sqlmodel import Session
from app.utils.auth.auth import decode_access_token
from app.utils.core.database import get_db
from app.repositories.auth.user_repository import UserRepository
from app.entities.auth.user import User
from app.repositories.auth.role_repository import RoleRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

role_repo = RoleRepository()

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur actuel à partir du sub (user_id) du token JWT.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        user_repo = UserRepository()
        print(f"Recherche utilisateur avec ID: {user_id}")  # Debug
        user = user_repo.get_by_id(db, int(user_id))
        print(f"Utilisateur trouvé: {user}")  # Debug
        if user is None:
            print(f"Aucun utilisateur trouvé pour l'ID: {user_id}")  # Debug
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        print(f"Retour de l'utilisateur: {user.email}")  # Debug
        return user
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




def require_role(permited_role: List[str]) -> int:
    """Decorator to require one of multiple roles from JWT token"""

    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

        if not permited_role or "*" in permited_role or "any" in permited_role or len(permited_role) == 0:
            return current_user.active_role

        active_user_role:Role = role_repo.get_by_id(db, current_user.active_role)
        if active_user_role.name not in permited_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: one of {permited_role} roles required, got {active_user_role.name}",
            )
        return current_user.active_role

    return role_checker

