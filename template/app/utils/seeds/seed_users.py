from sqlmodel import Session
from app.entities.auth.role import Role
from app.entities.auth.user import User
from app.utils.core.database import engine
from app.utils.auth.auth import get_password_hash
from datetime import datetime, timezone


def seed_users():
    """Seed initial roles and users"""
    with Session(engine) as db:
        try:
            # Create default roles
            roles_data = [
                {
                    "name": "admin",
                    "description": "Full system access",
                    "permissions": '["*"]',
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                },
                {
                    "name": "manager",
                    "description": "Management access",
                    "permissions": '["read:*", "write:users", "write:content"]',
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                },
                {
                    "name": "user",
                    "description": "Standard user access",
                    "permissions": '["read:own", "write:own"]',
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                },
            ]

            for role_data in roles_data:
                existing_role = db.query(Role).filter_by(name=role_data["name"]).first()
                if not existing_role:
                    role = Role(**role_data)
                    db.add(role)
                    print(f"Rôle créé : {role_data['name']}")
                else:
                    print(f"Rôle existant : {role_data['name']}")

            # Create admin user
            admin_email = "admin@admin.com"
            existing_user = db.query(User).filter_by(email=admin_email).first()
            if not existing_user:
                admin_user = User(
                    email=admin_email,
                    hashed_password=get_password_hash("admin"),
                    role="admin",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(admin_user)
                print(f"Utilisateur admin créé : {admin_email}")
            else:
                print(f"Utilisateur admin existant : {admin_email}")

            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Erreur lors du seeding : {e}")
            raise
