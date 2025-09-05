from sqlmodel import Session
from app.entities.auth.user import User
from app.repositories.auth.user_repository import UserRepository
from app.utils.auth.auth import get_password_hash
from datetime import datetime


def seed_users(db: Session):
    """Seed basic roles and admin user with multiple roles"""
    print("🌱 Starting simple roles and users seeding...")
    
    try:
        user_repo = UserRepository()

        # Create admin user if doesn't exist
        admin_email = "admin@example.com"
        existing_admin = user_repo.get_by_email(db, admin_email)
        if existing_admin:
            print(f"📝 Admin user already exists: {admin_email}")
            return

        admin_data = {
            "email": admin_email,
            "hashed_password": get_password_hash("admin123"),
            "roles": "user,manager,admin",  # Admin has all roles
            "active_role": "admin",  # Default active role
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        admin_user = user_repo.save(db, admin_data)
        print(f"✅ Created admin user: {admin_email} with roles: {admin_user.get_roles()}")

        # Create manager user
        manager_email = "manager@example.com"
        existing_manager = user_repo.get_by_email(db, manager_email)
        
        if not existing_manager:
            manager_data = {
                "email": manager_email,
                "hashed_password": get_password_hash("manager123"),
                "roles": "user,manager",  # Manager has user and manager roles
                "active_role": "manager",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            manager_user = user_repo.save(db, manager_data)
            print(f"✅ Created manager user: {manager_email} with roles: {manager_user.get_roles()}")
        else:
            print(f"📝 Manager user already exists: {manager_email}")

        # Create regular user
        user_email = "user@example.com"
        existing_user = user_repo.get_by_email(db, user_email)
        
        if not existing_user:
            user_data = {
                "email": user_email,
                "hashed_password": get_password_hash("user123"),
                "roles": "user",  # Only user role
                "active_role": "user",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            regular_user = user_repo.save(db, user_data)
            print(f"✅ Created regular user: {user_email} with roles: {regular_user.get_roles()}")
        else:
            print(f"📝 Regular user already exists: {user_email}")

        print("🎉 Users seeding completed!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
        raise