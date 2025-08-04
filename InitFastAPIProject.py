import os
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
    "app/schemas/__init__.py",
    "app/sqlmodels/__init__.py",
    "app/services/__init__.py",
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
    "pytest"
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
                f.write('''from fastapi import FastAPI\nfrom app.core.config import settings\n\napp = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)\n\n@app.get("/")\ndef read_root():\n    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}\n''')
        # Générer config.py avec valeurs par défaut
        elif file == "app/core/__init__.py":
            with open(file_path, "w", encoding="utf-8") as f:
                pass  # Laisser vide
            # Créer config.py dans core
            config_path = os.path.join(base_path, "app/core/config.py")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write('''from pydantic import BaseSettings\n\nclass Settings(BaseSettings):\n    PROJECT_NAME: str = "FastAPI Project"\n    VERSION: str = "0.1.0"\n    DEBUG: bool = True\n    DATABASE_URL: str = "sqlite:///./test.db"\n    SECRET_KEY: str = "changeme"\n\n    class Config:\n        env_file = ".env"\n\nsettings = Settings()\n''')
            print(f"📄 Fichier créé : {config_path}")
        # Générer un README.md avec infos sur l'architecture
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
        f.write("\n".join(requirements))
    print(f"✅ requirements.txt rempli ({len(requirements)} packages)")

    # Créer un environnement virtuel
    venv_path = os.path.join(base_path, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path])
    print(f"🧪 Environnement virtuel créé à : {venv_path}")


    print("🔧 Structure du projet créée avec succès !")


    # Installer les requirements avec le bon chemin pip
    if os.name == "nt":
        pip_executable = os.path.join(venv_path, "Scripts", "pip.exe")
        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip_executable = os.path.join(venv_path, "bin", "pip")
        python_executable = os.path.join(venv_path, "bin", "python")
    os.system(f'"{pip_executable}" install -r "{req_path}"')

    # Lancer l'application FastAPI avec le python du venv
    main_py = os.path.join(base_path, "app", "main.py")
    os.system(f'"{python_executable}" "{main_py}"')


if __name__ == "__main__":
    create_structure(input("Entrez le chemin du projet (par défaut: /project_fastapi): ") or "project_fastapi")
    print("🚀 Projet FastAPI initialisé avec succès !")
