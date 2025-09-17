from sqlmodel import Session
from typing import Generic, TypeVar, Type

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, db: Session, id: int) -> T | None:
        return db.get(self.model, id)

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> list[T]:
        return db.exec(self.model).offset(offset).limit(limit).all()

    def save(self, db: Session, obj_in: dict) -> T:
        """Create new object or update existing one based on presence of id"""
        obj_id = obj_in.get("id")

        if obj_id:
            # Update existing object
            obj = self.get(db, obj_id)
            if obj:
                for field, value in obj_in.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
            else:
                # ID provided but object doesn't exist, create new one
                obj = self.model(**obj_in)
                db.add(obj)
        else:
            # No ID provided, create new object
            obj = self.model(**obj_in)
            db.add(obj)

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get(db, id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
