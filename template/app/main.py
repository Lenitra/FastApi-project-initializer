from fastapi import FastAPI
from sqlmodel import SQLModel
from app.utils.core.config import settings
from app.utils.core.database import engine
from app.utils.seeds.seed_users import seed_users
# from app.middleware.auth_middleware import AuthMiddleware  # Removed to preserve Swagger docs

import pkgutil
import importlib
import pathlib

# Import all entities to register them with SQLModel
from app.entities import user, role

# Create database tables (drop and recreate to ensure schema is up to date)
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

# Seed initial data
seed_users()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI application with role-based authentication",
)

# Note: Authentication middleware removed to preserve Swagger documentation
# Routes are protected individually using Depends(get_current_user)

# Include authentication router manually
from app.routers.auth import router as auth_router

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include user and role management routers
from app.routers.users import router as users_router
from app.routers.roles import router as roles_router

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(roles_router, prefix="/roles", tags=["Roles"])

# Auto-discover other routers
routers_dir = pathlib.Path(__file__).parent / "routers"
for module_info in pkgutil.iter_modules([str(routers_dir)]):
    name = module_info.name
    if name.startswith("_") or name in ["auth", "users", "roles"]:
        continue

    try:
        module = importlib.import_module(f"app.routers.{name}")
        router = getattr(module, "router", None)
        if router:
            prefix = f"/{name}"
            if not name.endswith("s"):
                prefix += "s"
            app.include_router(router, prefix=prefix, tags=[name.capitalize()])
    except ImportError as e:
        print(f"Warning: Could not import router {name}: {e}")


@app.get("/")
def read_root():
    return {
        "message": "FastAPI with Role-Based Authentication",
        "version": settings.VERSION,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
