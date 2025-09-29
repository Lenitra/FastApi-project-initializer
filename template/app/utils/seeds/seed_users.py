from sqlmodel import Session
from app.entities.auth.user import User
from app.repositories.auth.user_repository import UserRepository
from app.utils.auth.auth import get_password_hash
from datetime import datetime


def seed_users(db: Session):
    """Seed basic roles and admin user with multiple roles"""
    print("🌱 Starting user:admin seeding...")
    
    try:
        user_repo = UserRepository()

        if user_repo.count(db) > 0:
            print("⚠️ Users already seeded, skipping.")
            return

        # Create admin user if doesn't exist
        admin_email = "admin@example.com"
        existing_admin = user_repo.get_by_email(db, admin_email)
        if existing_admin:
            print(f"📝 Admin user already exists: {admin_email}")
            return

        user = User()
        user.email = admin_email
        user.hashed_password = get_password_hash("admin123")
        user.roles_ids = [1]
        user.active_role = 1
        user.is_active = True
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()


        admin_user = user_repo.save(db, user)
        print(f"✅ Created admin user: {admin_email} with roles: {admin_user.roles_ids}")

        print("🎉 Users seeding completed!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
        raise