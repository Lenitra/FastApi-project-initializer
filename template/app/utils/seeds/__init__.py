# Seeds module initialization
# This module contains database seeding functions for initial data

from .seed_users import seed_users

__all__ = ["seed_users"]
