from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import List


class User(SQLModel, table=True):
    """Database table model for User"""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    roles: str = Field(default="user")  # Comma-separated roles: "user,admin,manager"
    active_role: str = Field(default="user")  # Current active role for JWT
    is_active: bool = Field(default=True)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        user_roles = [r.strip() for r in self.roles.split(",")]
        return role_name in user_roles

    def get_roles(self) -> List[str]:
        """Get all user roles as list"""
        return [r.strip() for r in self.roles.split(",")]

    def set_active_role(self, role_name: str) -> bool:
        """Set active role (must be one of user's roles)"""
        if self.has_role(role_name):
            self.active_role = role_name
            return True
        return False

    def add_role(self, role_name: str) -> None:
        """Add a role to the user"""
        current_roles = self.get_roles()
        if role_name not in current_roles:
            current_roles.append(role_name)
            self.roles = ",".join(current_roles)

    def remove_role(self, role_name: str) -> None:
        """Remove a role from the user"""
        current_roles = self.get_roles()
        if role_name in current_roles:
            current_roles.remove(role_name)
            self.roles = ",".join(current_roles) if current_roles else "user"
            # If removing active role, set to first available or "user"
            if self.active_role == role_name:
                self.active_role = current_roles[0] if current_roles else "user"

    def __repr__(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "roles": self.get_roles(),
            "active_role": self.active_role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }