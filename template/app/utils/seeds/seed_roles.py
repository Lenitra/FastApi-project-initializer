from sqlmodel import Session
from app.utils.auth.auth import get_password_hash
from datetime import datetime
from app.repositories.auth.role_repository import RoleRepository


def seed_roles(db: Session):
    """Seed basic roles and admin user with multiple roles"""
    print("🌱 Starting simple roles and users seeding...")
    
    try:
        role_repo = RoleRepository()

    except Exception as e:
        print(f"❌ Error during roles seeding: {e}")
        return