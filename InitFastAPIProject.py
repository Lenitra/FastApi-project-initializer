import os
import random
import subprocess
import sys

# Dossiers à créer
folders = [
    "app",
    "app/core",
    "app/routes",
    "app/schemas",
    "app/sqlmodels",
    "app/services",
    "app/utils",
    "app/utils/dataset",
    "app/middleware",
]

# Fichiers à créer
files = [
    "app/main.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/database.py",
    "app/routes/__init__.py",
    "app/routes/auth.py",
    "app/schemas/__init__.py",
    "app/schemas/user.py",
    "app/schemas/token.py",
    "app/sqlmodels/__init__.py",
    "app/sqlmodels/user.py",
    "app/services/__init__.py",
    "app/services/auth.py",
    "app/services/roles.py",
    "app/utils/__init__.py",
    "app/utils/dataset/__init__.py",
    "app/utils/dataset/users.py",
    "app/middleware/__init__.py",
    ".env",
    "requirements.txt",
    "README.md",
]

# Contenu des requirements avec Argon2
requirements = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "pydantic",
    "alembic",
    "python-dotenv",
    "httpx",
    "pytest",
    "python-jose[cryptography]",
    "passlib[argon2]",
    "python-multipart",
]

def create_structure(base_path="."):
    print("🔧 Initialisation du projet FastAPI avec rôles…")

    # Créer les dossiers
    for folder in folders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        print(f"📁 Dossier créé : {path}")

    # Créer les fichiers
    for file in files:
        file_path = os.path.join(base_path, file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Génération de chaque fichier
        if file == "app/main.py":
            content = '''from fastapi import FastAPI
from app.core.config import settings
from app.routes.auth import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}
'''
        elif file == "app/sqlmodels/__init__.py":
            content = '''from sqlalchemy.orm import declarative_base

Base = declarative_base()
'''

        
        elif file == "app/core/config.py":
            secret_key = random.SystemRandom().getrandbits(256)
            content = f'''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "localhost:5432"
    SECRET_KEY: str = "{secret_key}"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_DATABASE: str = "postgres"

    class Config:
        env_file = ".env"

settings = Settings()
'''
        elif file == "app/core/database.py":
            content = '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
if hasattr(settings, "DB_USERNAME"):
    if "postgresql" not in DATABASE_URL:
        DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DATABASE_URL}/{settings.DB_DATABASE}"

engine = create_engine(DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        elif file == "app/routes/auth.py":
            content = '''from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from app.services.auth import verify_password, create_access_token, decode_access_token
from app.core.config import settings
from app.schemas.user import User
from app.schemas.token import Token
from app.sqlmodels.user import UserInDB
from app.utils.dataset.users import get_users

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

fake_users_db = get_users()

def get_user(email: str):
    return fake_users_db.get(email)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = decode_access_token(token)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.email)
    if user is None:
        raise credentials_exception
    return User(email=user.email, role=user.role)
'''
        elif file == "app/schemas/user.py":
            content = '''from pydantic import BaseModel

class User(BaseModel):
    email: str
    role: str
'''
        elif file == "app/schemas/token.py":
            content = '''from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = "user"
'''
        elif file == "app/sqlmodels/user.py":
            content = '''from sqlalchemy import Column, Integer, String
from app.sqlmodels import Base

class UserInDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
'''
        elif file == "app/services/auth.py":
            content = '''from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.schemas.token import TokenData

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    email = payload.get("sub")
    role = payload.get("role", "user")
    if email is None:
        raise JWTError("Missing subject")
    return TokenData(email=email, role=role)
'''
        elif file == "app/services/roles.py":
            content = '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.services.auth import decode_access_token
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        return decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

def require_role(required_role: str):
    def role_checker(user: TokenData = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: {required_role} role required",
            )
        return user
    return role_checker
'''
        elif file == "app/utils/dataset/users.py":
            content = '''from app.services.auth import get_password_hash
from app.sqlmodels.user import UserInDB

"""Dataset de test contenant un compte admin par défaut."""

def get_users():
    return {
        "admin@admin.com": UserInDB(
            email="admin@admin.com",
            hashed_password=get_password_hash("admin"),
            role="admin",
        ),
        "user@example.com": UserInDB(
            email="user@example.com",
            hashed_password=get_password_hash("secret"),
            role="user",
        ),
    }
'''
        elif file == "README.md":
            content = """# FastAPI Project

Projet généré automatiquement avec gestion des rôles et authentification JWT (Argon2)."""
        elif file == "requirements.txt":
            content = "\n".join(requirements + ["pydantic-settings"])
        elif file == ".env":
            content = "# Variables d'environnement - remplir selon besoin"
        else:
            content = ""

        # Écrire le contenu
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Fichier créé : {file_path}")

    # .gitignore
    gitignore_path = os.path.join(base_path, ".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("""__pycache__/
*.py[cod]
venv/
.env
*.db
*.log
.vscode/
.idea/
""")
    print(f"📄 .gitignore créé")

    # Virtualenv
    venv_path = os.path.join(base_path, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path])
    print(f"🧪 Environnement virtuel créé : {venv_path}")

    # Scripts de lancement
    python_exec = os.path.join("venv", "Scripts" if os.name == "nt" else "bin", "python")
    with open(os.path.join(base_path, "run.bat"), "w") as f:
        f.write(f'@echo off\n"{python_exec}" -m uvicorn app.main:app --reload')
    with open(os.path.join(base_path, "run.sh"), "w") as f:
        f.write(f'#!/bin/bash\n"{python_exec}" -m uvicorn app.main:app --reload')
    print("🚀 Fichiers de lancement créés")

    # setup.bat
    setup_path = os.path.join(base_path, "setup.bat")
    with open(setup_path, "w", encoding="utf-8") as f:
        f.write("""@echo off
call venv\\Scripts\\activate.bat
pip install -r requirements.txt
echo Environnement virtuel activé et dépendances installées.
""")
    print("📄 setup.bat créé")

    print("✅ Projet FastAPI initialisé avec Argon2 et rôles !")

if __name__ == "__main__":
    create_structure("C:\\Users\\thoma\\Desktop\\NyxImperiumBackend")
