import os
import random
import subprocess
import sys

from utils import get_entities

# --- Constantes ---
FOLDERS = [
    "app", "app/core", "app/routes", "app/schemas", "app/sqlmodels",
    "app/services", "app/utils", "app/utils/seeds", "app/middleware"
]

FILES = [
    "app/main.py", "app/core/__init__.py", "app/core/config.py", "app/core/database.py",
    "app/routes/__init__.py", "app/routes/auth.py", "app/schemas/__init__.py",
    "app/schemas/user.py", "app/schemas/token.py", "app/sqlmodels/__init__.py",
    "app/sqlmodels/user.py", "app/services/__init__.py", "app/services/auth.py",
    "app/services/roles.py", "app/utils/__init__.py", "app/utils/seeds/__init__.py",
    "app/utils/seeds/seed_users.py", "app/middleware/__init__.py", ".env", "requirements.txt", "README.md",
    "app/middleware/auth_checker.py", ".env.example"
]

REQUIREMENTS = [
    "fastapi", "uvicorn[standard]", "sqlalchemy", "pydantic", "alembic", "python-dotenv",
    "httpx", "pytest", "python-jose[cryptography]", "passlib[argon2]", "python-multipart", "psycopg2",
]

def get_file_content(file, secret_key=None):
    if file == "app/main.py":
        return '''from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine
from app.sqlmodels import Base
from app.utils.seeds.seed_users import seed_users
from app.middleware.auth_checker import AuthMiddleware

import pkgutil
import importlib
import pathlib

# Création de la base de données
Base.metadata.create_all(bind=engine)  # recrée toutes les tables
seed_users()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.add_middleware(AuthMiddleware)

# inclusion manuelle du router d'auth
from app.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# découverte dynamique de tous les autres routers
routes_dir = pathlib.Path(__file__).parent / "routes"
for module_info in pkgutil.iter_modules([str(routes_dir)]):
    name = module_info.name
    if name.startswith("_") or name == "auth":
        continue
    module = importlib.import_module(f"app.routes.{name}")
    router = getattr(module, "router", None)
    if router:
        prefix = f"/{name}s"
        app.include_router(router, prefix=prefix, tags=[name])


'''
    elif file == "app/middleware/auth_checker.py":
        return """# app/middleware/auth_checker.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jose import JWTError
from app.services.auth import decode_access_token
from dotenv import load_dotenv
import os

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        load_dotenv()
        if os.getenv("DEBUG", "False").lower() == "true":
            authorized_routes = ["/docs", "/redoc", "/openapi.json"]
            if request.url.path in authorized_routes:
                return await call_next(request)
        if request.url.path.startswith("/auth"):  # Ne pas vérifier les routes d'auth
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
            status_code=401, content={"detail": "Missing or invalid Authorization header"}
            )

        token = auth_header[7:]  # Supprime "Bearer "
        try:
            user = decode_access_token(token)
            request.state.user = user
        except JWTError:
            return JSONResponse(
            status_code=401, content={"detail": "Invalid token"}
            )

        response = await call_next(request)
        return response
    """

    elif file == "app/sqlmodels/__init__.py":
        return '''from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importe automatiquement tous les modules du dossier (magique)
import pkgutil
import importlib
import pathlib

for module in pkgutil.iter_modules([str(pathlib.Path(__file__).parent)]):
    if module.name != "__init__":
        importlib.import_module(f"{__package__}.{module.name}")
'''
    elif file == "app/core/config.py":
        return '''from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Configuration de base de données
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    
    # Configuration de sécurité
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()
'''
    elif file == "app/core/database.py":
        return '''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Construction de l'URL de connexion à partir des variables d'environnement
DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

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
        return '''from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from app.services.auth import verify_password, create_access_token, decode_access_token
from app.core.config import settings
from app.schemas.user import User
from app.schemas.token import Token
from app.sqlmodels.user import UserInDB

from app.core.database import SessionLocal

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def authenticate_user(email: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(UserInDB).filter(UserInDB.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    finally:
        db.close()

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
'''
    elif file == "app/schemas/user.py":
        return '''from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True
'''
    elif file == "app/schemas/token.py":
        return '''from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = "user"
'''
    elif file == "app/sqlmodels/user.py":
        return '''from sqlalchemy import Column, Integer, String
from app.sqlmodels import Base

class UserInDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
'''
    elif file == "app/services/auth.py":
        return '''from datetime import datetime, timedelta
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
        return '''from fastapi import Depends, HTTPException, status
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
    elif file == "app/utils/seeds/seed_users.py":
        return '''from app.sqlmodels.user import UserInDB
from app.core.database import SessionLocal
from app.services.auth import get_password_hash

def seed_users():
    db = SessionLocal()
    try:
        email = "admin@admin.com"
        existing = db.query(UserInDB).filter_by(email=email).first()
        if not existing:
            db_user = UserInDB(
                email=email,
                hashed_password=get_password_hash("admin"),
                role="admin",
            )
            db.add(db_user)
            print(f"Utilisateur ajouté : {email}")
        else:
            print(f"Utilisateur déjà existant : {email}")
        db.commit()
    finally:
        db.close()
'''
    elif file == "README.md":
        # Utilise la clé secrète générée pour insérer une valeur d'exemple dans le README
        secret_display = format(secret_key, 'x') if secret_key is not None else "change_me"
        return f"""# Projet FastAPI généré

Ce projet a été généré automatiquement par `InitFastAPIProject.py`.

## Aperçu

- Structure modulaire (routes, services, modèles, schémas)
- Authentification JWT (exemple avec Argon2)
- Fichier `.env.example` fourni et `.env` généré
- Environnement virtuel `venv` et `requirements.txt`

> Clé secrète générée pour cet environnement (exemple) : `{secret_display}`

## Démarrer (Windows)

1. Ouvrez PowerShell dans le dossier du projet généré.
2. Faites l'installation des packages requis :

```powershell
setup.bat
```

4. Lancez le serveur 

```powershell
run.bat
```

L'API sera disponible sur http://127.0.0.1:8000 et la documentation interactive sur http://127.0.0.1:8000/docs

## Fichiers importants générés

- `app/main.py` — point d'entrée de l'application
- `app/core/config.py` — lecture des variables d'environnement
- `app/core/database.py` — configuration SQLAlchemy
- `app/routes/` — endpoints (ex. `auth.py`)
- `app/sqlmodels/` — modèles SQLAlchemy
- `app/schemas/` — schémas Pydantic
- `.env.example` et `.env` — variables d'environnement
- `requirements.txt` — dépendances

## Variables d'environnement recommandées

Remplissez `.env` (ou copiez depuis `.env.example`) avec :

```
DEBUG=True
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=db_fastapi_project
SECRET_KEY={secret_display}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Remplacez `SECRET_KEY` par une valeur secrète et robuste en production.
"""
    elif file == "requirements.txt":
        return "\n".join(REQUIREMENTS + ["pydantic-settings"])
    elif file == ".env" or file == ".env.example":
        if secret_key is None:
            import random
            secret_key = random.SystemRandom().getrandbits(256)
        return """# Variables d'environnement - remplir selon besoin
DEBUG=True

# Informations de connexion à la base de données
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=db_fastapi_project

# Configuration de sécurité
SECRET_KEY={}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
""".format(secret_key)
    else:
        return ""

def create_folders(base_path=".", folders=None):
    for folder in (folders or FOLDERS):
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        print(f"📁 Dossier créé : {path}")

def create_files(base_path=".", files=None, secret_key=None):
    for file in (files or FILES):
        file_path = os.path.join(base_path, file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = get_file_content(file, secret_key=secret_key)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Fichier créé : {file_path}")

def create_gitignore(base_path="."):
    gitignore_path = os.path.join(base_path, ".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
venv/
.env
.env.*
*.sqlite3
*.db
*.log
*.pot
*.pyc
*.mypy_cache/
.pytest_cache/
.vscode/
dist/
build/
*.egg-info/
*.egg
.DS_Store
node_modules/
coverage/
htmlcov/
.idea/
/.history/
""")
    print(f"📄 .gitignore créé")

def create_virtualenv(base_path="."):
    venv_path = os.path.join(base_path, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path])
    print(f"🧪 Environnement virtuel créé : {venv_path}")
    return venv_path

def create_launch_scripts(base_path="."):
    python_exec = os.path.join("venv", "Scripts" if os.name == "nt" else "bin", "python")
    with open(os.path.join(base_path, "run.bat"), "w") as f:
        f.write(f'@echo off\n"{python_exec}" -m uvicorn app.main:app --reload')
    with open(os.path.join(base_path, "run.sh"), "w") as f:
        f.write(f'#!/bin/bash\n"{python_exec}" -m uvicorn app.main:app --reload')
    print("🚀 Fichiers de lancement créés")

def create_setup_script(base_path="."):
    setup_path = os.path.join(base_path, "setup.bat")
    with open(setup_path, "w", encoding="utf-8") as f:
        f.write("""@echo off
call venv\\Scripts\\activate.bat
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
echo Environnement virtuel activé et dépendances installées.
""")
    print("📄 setup.bat créé")

def create_custom_entities(base_path="."):
    entities = get_entities()
    for entity in entities:
        filename = entity.lower() + ".py"
        sqlmodels_path = os.path.join(base_path, "app", "sqlmodels", filename)
        schemas_path = os.path.join(base_path, "app", "schemas", filename)
        routes_path = os.path.join(base_path, "app", "routes", filename)
        with open(sqlmodels_path, "w", encoding="utf-8") as f:
            f.write(generate_sql_schema(entity, entities[entity]))
            print(f"📄 Fichier généré : {sqlmodels_path}")
        with open(schemas_path, "w", encoding="utf-8") as f:
            f.write(generate_schema(entity, entities[entity]))
            print(f"📄 Fichier généré : {schemas_path}")
        
        with open(routes_path, "w", encoding="utf-8") as f:
            f.write(generate_getters_routes(entity, entities[entity]))
            print(f"📄 Fichier généré : {routes_path}")



def generate_schema(entity_name:str, attributes:list):
    schema_content = f"from pydantic import BaseModel\n"
    for attr in attributes:
        if is_custom_type(attr.split()[1]):
            schema_content += f"\nfrom app.schemas.{attr.split()[1].lower()} import {attr.split()[1]}\n"
    schema_content+=f"""from datetime import datetime, date, time

class {entity_name}(BaseModel):
"""
    for attr in attributes:
        var_name = attr.split()[0] 
        var_type = attr.split()[1] if len(attr.split()) > 1 else "str"
        schema_content += f"    {var_name}: {var_type}\n"

    schema_content += "\n    class Config:\n        from_attributes = True\n"
    return schema_content

def is_custom_type(py_type: str) -> bool:
    not_custom = ["int", "str", "float", "date", "bool", "list", "dict"]
    return not any(py_type.startswith(simple_type) for simple_type in not_custom)

def parse_py_types_to_sql_type(py_type: str) -> str:
    if py_type.lower() in ["int", "integer"]:
        return "Integer"
    elif py_type.lower() in ["str", "string"]:
        return "String"
    elif py_type.lower() in ["float", "decimal"]:
        return "Float"
    elif py_type.lower() in ["date", "datetime"]:
        return "Date"
    elif py_type.lower() in ["bool", "boolean"]:
        return "Boolean"
    else:
        print()
        print("❓❓❓ Type non reconnu pour l'enregistrement dans la BDD : ")
        print("❓❓❓ " + py_type + "\n")
        return py_type

def generate_sql_schema(entity_name:str, attributes:list):
    sql_content = f"""from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey
from app.sqlmodels import Base

class {entity_name}(Base):
    __tablename__ = "{entity_name.lower()}"
    id = Column(Integer, primary_key=True, autoincrement=True)
"""
    for attr in attributes:
        var_name = attr.split()[0]
        var_type = attr.split()[1] if len(attr.split()) > 1 else "str"
        
        not_null = ".nn" in attr
        unique = ".unique" in attr
        fk = ".fk" in attr
        max = None
        var_type = parse_py_types_to_sql_type(var_type)
        
        if ".max" in attr:
            max = attr.split(".max")[1].split()[0].strip()


        if max is not None and var_type == "String":
            var_type = f"String({max})"

        if ".fk" in attr:
            fk_table = var_type.lower()
            sql_content += f"    {var_name} = Column(Integer, ForeignKey('{fk_table.lower()}.id'), nullable={str(not_null)}, unique={str(unique)})\n"
            continue

        sql_content += f"    {var_name} = Column({var_type}, nullable={str(not_null)}, unique={str(unique)})\n"

    sql_content += "\n"
    return sql_content

def generate_getters_routes(entity_name: str, attributes: list) -> str:
    return f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.sqlmodels.{entity_name.lower()} import {entity_name}
from app.schemas.{entity_name.lower()} import {entity_name} as {entity_name}Schema

router = APIRouter()

@router.get("/", response_model=list[{entity_name}Schema])
def get_all_{entity_name.lower()}s(db: Session = Depends(get_db)):
    return db.query({entity_name}).all()

@router.get("/{{id}}", response_model={entity_name}Schema)
def get_{entity_name.lower()}_by_id(id: int, db: Session = Depends(get_db)):
    obj = db.query({entity_name}).filter({entity_name}.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{entity_name} not found")
    return obj
'''
    return getters_content

def init_fastapi_project(base_path="."):
    print("🔧 Initialisation du projet FastAPI avec rôles…")
    secret_key = random.SystemRandom().getrandbits(256)
    create_folders(base_path)
    create_files(base_path, secret_key=secret_key)
    create_gitignore(base_path)
    create_virtualenv(base_path)
    create_launch_scripts(base_path)
    create_setup_script(base_path)
    create_custom_entities(base_path)
    print("✅ Projet FastAPI initialisé avec succès !")

def main():
    base_path = "C:\\Users\\thoma\\Desktop\\NyxImperiumBackend"
    init_fastapi_project(base_path)

if __name__ == "__main__":
    main()
