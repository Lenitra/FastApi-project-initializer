import os
import random
from re import sub
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
    "app/middleware",
]

# Fichiers à créer
files = [
    "app/main.py",
    "app/core/__init__.py",
    "app/routes/__init__.py",
    "app/routes/auth.py",
    "app/schemas/__init__.py",
    "app/sqlmodels/__init__.py",
    "app/services/__init__.py",
    "app/services/auth.py",
    "app/utils/__init__.py",
    "app/middleware/__init__.py",
    ".env",
    "requirements.txt",
    "README.md"
]

# Contenu des requirements
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
    "passlib[bcrypt]"
]

def create_structure(base_path="."):

    print("🔧 Initialisation du projet FastAPI...")

    # Créer les dossiers
    for folder in folders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        print(f"📁 Dossier créé : {path}")

    # Créer les fichiers
    for file in files:
        file_path = os.path.join(base_path, file)
        # Remplir main.py automatiquement
        if file == "app/main.py":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('''from fastapi import FastAPI\nfrom app.core.config import settings\nfrom app.routes.auth import router as auth_router\n\napp = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)\napp.include_router(auth_router, prefix="/auth")\n\n@app.get("/")\ndef read_root():\n    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}\n''')
        # Générer config.py avec valeurs par défaut
        elif file == "app/core/__init__.py":
            with open(file_path, "w", encoding="utf-8") as f:
                pass  # Laisser vide
            # Créer config.py dans core
            config_path = os.path.join(base_path, "app/core/config.py")
            secret_key = random.SystemRandom().getrandbits(256)  # Générer une clé secrète aléatoire
            db_username = "postgres"
            db_password = "postgres"
            db_database = "postgres"
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(f'''from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    PROJECT_NAME: str = "FastAPI Project"\n    VERSION: str = "0.1.0"\n    DEBUG: bool = True\n    DATABASE_URL: str = "localhost:5432"\n    SECRET_KEY: str = "{secret_key}"\n    ALGORITHM: str = "HS256"\n    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30\n    DB_USERNAME: str = "{db_username}"\n    DB_PASSWORD: str = "{db_password}"\n    DB_DATABASE: str = "{db_database}"\n\n    class Config:\n        env_file = ".env"\n\nsettings = Settings()\n''')
            print(f"📄 Fichier créé : {config_path}")

            # Générer database.py dans core
            database_path = os.path.join(base_path, "app/core/database.py")
            with open(database_path, "w", encoding="utf-8") as f:
                f.write('''from sqlalchemy import create_engine\nfrom sqlalchemy.orm import sessionmaker\nfrom app.core.config import settings\n\n# Construction de l\'URL de connexion à la BDD de façon générique\nDATABASE_URL = settings.DATABASE_URL\nif hasattr(settings, "DB_USERNAME") and hasattr(settings, "DB_PASSWORD") and hasattr(settings, "DB_DATABASE"):\n    # Si DATABASE_URL ne contient pas déjà les infos, on construit une URL PostgreSQL par défaut\n    if "postgresql" not in DATABASE_URL:\n        DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DATABASE_URL}/{settings.DB_DATABASE}"\n\nengine = create_engine(DATABASE_URL, echo=settings.DEBUG)\nSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n\ndef get_db():\n    db = SessionLocal()\n    try:\n        yield db\n    finally:\n        db.close()\n''')
            print(f"📄 Fichier créé : {database_path}")
        # Générer un README.md avec infos sur l'architecture
        elif file == "app/routes/auth.py":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('''from datetime import timedelta\nfrom fastapi import APIRouter, Depends, HTTPException, status\nfrom fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm\nfrom jose import JWTError\nfrom pydantic import BaseModel\nfrom app.services.auth import (\n    verify_password,\n    get_password_hash,\n    create_access_token,\n    decode_access_token,\n)\nfrom app.core.config import settings\n\nrouter = APIRouter()\noauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")\n\nclass Token(BaseModel):\n    access_token: str\n    token_type: str\n\nclass User(BaseModel):\n    email: str\n\nclass UserInDB(User):\n    hashed_password: str\n\nfake_users_db = {\n    "user@example.com": {\n        "email": "user@example.com",\n        "hashed_password": get_password_hash("secret"),\n    }\n}\n\ndef get_user(email: str):\n    user_dict = fake_users_db.get(email)\n    if user_dict:\n        return UserInDB(**user_dict)\n\ndef authenticate_user(email: str, password: str):\n    user = get_user(email)\n    if not user or not verify_password(password, user.hashed_password):\n        return False\n    return user\n\n@router.post("/token", response_model=Token)\nasync def login(form_data: OAuth2PasswordRequestForm = Depends()):\n    user = authenticate_user(form_data.username, form_data.password)\n    if not user:\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail="Incorrect email or password",\n        )\n    access_token = create_access_token(\n        data={"sub": user.email},\n        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),\n    )\n    return {"access_token": access_token, "token_type": "bearer"}\n\n@router.get("/users/me", response_model=User)\nasync def read_users_me(token: str = Depends(oauth2_scheme)):\n    credentials_exception = HTTPException(\n        status_code=status.HTTP_401_UNAUTHORIZED,\n        detail="Could not validate credentials",\n        headers={"WWW-Authenticate": "Bearer"},\n    )\n    try:\n        token_data = decode_access_token(token)\n    except JWTError:\n        raise credentials_exception\n    user = get_user(token_data.email)\n    if user is None:\n        raise credentials_exception\n    return user\n''')
        elif file == "app/services/auth.py":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('''from datetime import datetime, timedelta\nfrom typing import Optional\nfrom jose import jwt, JWTError\nfrom passlib.context import CryptContext\nfrom pydantic import BaseModel\nfrom app.core.config import settings\n\npwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")\n\nclass TokenData(BaseModel):\n    email: Optional[str] = None\n\ndef verify_password(plain_password: str, hashed_password: str) -> bool:\n    return pwd_context.verify(plain_password, hashed_password)\n\ndef get_password_hash(password: str) -> str:\n    return pwd_context.hash(password)\n\ndef create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:\n    to_encode = data.copy()\n    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))\n    to_encode.update({"exp": expire})\n    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)\n\ndef decode_access_token(token: str) -> TokenData:\n    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])\n    email: str = payload.get("sub")\n    if email is None:\n        raise JWTError("Missing subject")\n    return TokenData(email=email)\n''')
        elif file == "README.md":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"""# FastAPI Project\n\nCe projet a été généré automatiquement.\n\n## Architecture\n\n- **app/** : Contient l'application FastAPI\n    - **main.py** : Point d'entrée de l'application\n    - **core/** : Configuration et paramètres globaux\n        - **config.py** : Paramètres de configuration (Pydantic)\n    - **routes/** : Définition des routes de l'API\n    - **schemas/** : Schémas Pydantic pour validation des données\n    - **sqlmodels/** : Modèles SQLAlchemy ou SQLModel\n    - **services/** : Logique métier et services\n    - **utils/** : Fonctions utilitaires\n    - **middleware/** : Middlewares personnalisés\n- **requirements.txt** : Dépendances Python\n- **.env** : Variables d'environnement\n- **README.md** : Ce fichier\n\n## Lancement rapide\n\n```bash\npython InitFastAPIProject.py\n```\n\n## Démarrer le serveur\n\n```bash\nuvicorn app.main:app --reload\n```\n\n""")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                pass
        print(f"📄 Fichier créé : {file_path}")

    # Remplir requirements.txt
    req_path = os.path.join(base_path, "requirements.txt")
    with open(req_path, "w") as f:
            f.write("\n".join(requirements + ["pydantic-settings"]))
    print(f"✅ requirements.txt rempli ({len(requirements)} packages)")

    # Générer un .gitignore
    gitignore_path = os.path.join(base_path, ".gitignore")
    gitignore_content = """# Python
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
    """
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print(f"📄 Fichier créé : {gitignore_path}")

    # Créer un environnement virtuel
    venv_path = os.path.join(base_path, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path])
    print(f"🧪 Environnement virtuel créé à : {venv_path}")

    # Récupérer le chemin de l'exécutable python
    if os.name == "nt":
        python_executable = os.path.join("../",venv_path, "Scripts", "python.exe")
    else:
        python_executable = os.path.join("../",venv_path, "bin", "python")


    # Création d'un fichier .bat pour lancer le projet
    bat_content = f'@echo off\n"{python_executable}" -m uvicorn app.main:app --reload'
    bat_path = os.path.join(base_path, "run.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"📄 Fichier de lancement créé : {bat_path}")


    # Création d'un fichier .sh pour lancer le projet sur Unix
    sh_content = f'#!/bin/bash\n"{python_executable}" -m uvicorn app.main:app --reload'
    sh_path = os.path.join(base_path, "run.sh")
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(sh_content)
    print(f"📄 Fichier de lancement créé : {sh_path}")


    # Création d'un fichier setup.bat qui installe les dépendances et qui active l'environnement
    setup_bat_path = os.path.join(base_path, "setup.bat")
    setup_bat_content = (
        "@echo off\r\n"
        "call venv\\Scripts\\activate.bat\r\n"
        "pip install -r requirements.txt\r\n"
        "echo Environnement virtuel activé et dépendances installées.\r\n"
    )
    with open(setup_bat_path, "w", encoding="utf-8") as f:
        f.write(setup_bat_content)
    print(f"📄 Fichier setup.bat créé : {setup_bat_path}")


    print("🔧 Structure du projet créée avec succès !")


if __name__ == "__main__":
    create_structure(input("Entrez le chemin du projet (par défaut: /project_fastapi): ") or "project_fastapi")
    print("🚀 Projet FastAPI initialisé avec succès !")
