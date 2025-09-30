from sqlmodel import Session, select
from typing import Generic, TypeVar, Type

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, db: Session, id: int) -> T | None:
        return db.get(self.model, id)
    
    def get_by_id(self, db: Session, id: int) -> T | None:
        return db.get(self.model, id)

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> list[T]:
        return db.exec(select(self.model).offset(offset).limit(limit)).all()

    def save(self, db: Session, obj: T) -> T:
        """Create new object or update existing one based on presence of id"""
        # Check if object has an ID and if it exists in database
        obj_id = getattr(obj, 'id', None)

        if obj_id:
            # Update existing object
            existing_obj = self.get(db, obj_id)
            if existing_obj:
                # Update existing object with new values
                if hasattr(obj, 'model_dump'):
                    # For Pydantic v2 models
                    obj_data = obj.model_dump(exclude_unset=True, exclude={'id'})
                elif hasattr(obj, 'dict'):
                    # For Pydantic v1 models
                    obj_data = obj.dict(exclude_unset=True, exclude={'id'})
                else:
                    # For regular objects
                    obj_data = {k: v for k, v in obj.__dict__.items() if k != 'id'}

                for field, value in obj_data.items():
                    if hasattr(existing_obj, field):
                        setattr(existing_obj, field, value)

                db.commit()
                db.refresh(existing_obj)
                return existing_obj

        # Create new object (either no ID provided or ID doesn't exist)
        if hasattr(obj, 'model_dump'):
            # For Pydantic v2 models
            obj_data = obj.model_dump(exclude_unset=True)
        elif hasattr(obj, 'dict'):
            # For Pydantic v1 models
            obj_data = obj.dict(exclude_unset=True)
        else:
            # For regular objects
            obj_data = obj.__dict__.copy()

        # Remove id if it exists for new objects
        obj_data.pop('id', None)

        new_obj = self.model(**obj_data)
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        return new_obj

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get_by_id(db, id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
    
    def count(self, db: Session) -> int:
        return len(db.exec(select(self.model)).all())
