from sqlmodel import SQLModel, Field
from datetime import datetime


class Role(SQLModel, table=True):
    """Database table model for Role"""

    __tablename__ = "roles"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    permissions: str | None = Field(default=None)  # JSON string of permissions
    is_active: bool = Field(default=True)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
