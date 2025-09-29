from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from typing import List
from sqlalchemy import JSON


class User(SQLModel, table=True):
    """Database table model for User"""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    roles_ids: List[int] = Field(default=[1], sa_column=Column(JSON))  # List of role IDs
    active_role: int = Field(default=1)  # Current active role ID
    is_active: bool = Field(default=True)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)

    def has_role(self, role_id: int) -> bool:
        """Check if user has a specific role"""
        return role_id in self.roles_ids

