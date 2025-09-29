from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Role(SQLModel, table=True):
    """Database table model for Role"""

    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    updated_at: Optional[datetime] = Field(default=datetime.utcnow)
    created_at: datetime = Field(default=datetime.utcnow)