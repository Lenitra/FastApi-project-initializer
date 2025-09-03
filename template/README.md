# Projet FastAPI généré

Ce projet a été généré automatiquement par `InitFastAPIProject.py`.

## Aperçu

- Structure modulaire (routes, services, modèles, schémas)
- Authentification JWT (exemple avec Argon2)
- Fichier `.env.example` fourni et `.env` généré
- Environnement virtuel `venv` et `requirements.txt`

> Clé secrète générée pour cet environnement (exemple) : `766b48fcbbd43713141be4abc26b96c4eb0da25f2cbcaff6e8b38dd10490a5d0`

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
SECRET_KEY=766b48fcbbd43713141be4abc26b96c4eb0da25f2cbcaff6e8b38dd10490a5d0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Remplacez `SECRET_KEY` par une valeur secrète et robuste en production.
