from sqlmodel import Session
from app.repositories.base_repository import BaseRepository
from app.entities.auth.role import Role


class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Role | None:
        return db.exec(Role).filter(Role.name == name).first()

    def get_active_roles(self, db: Session) -> list[Role]:
        return db.exec(Role).filter(Role.is_active).all()
