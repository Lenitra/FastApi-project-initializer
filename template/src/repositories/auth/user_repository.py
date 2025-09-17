from sqlmodel import Session, select
from app.entities.auth.user import User
from app.repositories.base_repository import BaseRepository
from typing import List


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    def get_by_role(self, db: Session, role_name: str) -> List[User]:
        """Get users by role name"""
        statement = select(User).where(User.roles.__contains__(role_name))
        return list(db.exec(statement).all())


