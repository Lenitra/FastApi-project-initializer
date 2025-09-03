from sqlmodel import Session
from app.repositories.base_repository import BaseRepository
from app.entities.auth.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.exec(User).filter(User.email == email).first()

    def get_active_users(self, db: Session) -> list[User]:
        return db.exec(User).filter(User.is_active).all()

    def get_by_role(self, db: Session, role: str) -> list[User]:
        return db.exec(User).filter(User.role == role).all()
