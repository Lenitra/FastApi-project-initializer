from fastapi import FastAPI
from sqlmodel import SQLModel
from app.utils.core.config import settings
from app.utils.core.database import engine
from app.utils.seeds.seed_users import seed_users
from app.utils.seeds.seed_roles import seed_roles
from sqlmodel import Session
# from app.middleware.auth_middleware import AuthMiddleware  # Removed to preserve Swagger docs

import pkgutil
import importlib
import pathlib

# Import all entities to register them with SQLModel
from app.entities.auth import user

# Create database tables (drop and recreate to ensure schema is up to date)
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

# Seed initial data
with Session(engine) as session:
    seed_roles(session)
    seed_users(session)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI application with role-based authentication",
)

# Note: Authentication middleware removed to preserve Swagger documentation
# Routes are protected individually using Depends(get_current_user)

# Auto-discover all routers
routers_dir = pathlib.Path(__file__).parent / "routers"

# Define special router configurations
special_routers = {
    "auth": {"prefix": "/auth", "tags": ["Authentication"]},
    "users": {"prefix": "/users", "tags": ["Users"]},  
    "roles": {"prefix": "/roles", "tags": ["Roles"]}
}

for module_info in pkgutil.iter_modules([str(routers_dir)]):
    name = module_info.name
    if name.startswith("_"):
        continue

    try:
        module = importlib.import_module(f"app.routers.{name}")
        router = getattr(module, "router", None)
        if router:
            # Use special configuration if exists, otherwise use generic
            if name in special_routers:
                config = special_routers[name]
                app.include_router(router, prefix=config["prefix"], tags=config["tags"])
            else:
                tags = [name.replace("_", " ").title()]
                app.include_router(router)
    except ImportError as e:
        print(f"Warning: Could not import router {name}: {e}")



@app.get("/health")
def health_check():
    return {"status": "healthy"}