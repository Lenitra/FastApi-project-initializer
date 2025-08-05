# FastAPI Project Initializer

Un script Python pour générer automatiquement la structure complète d’un projet FastAPI, avec tous les dossiers, fichiers essentiels, un système d'authentification JWT basique, environnement virtuel et dépendances de base.

## 🚀 À quoi sert ce script ?

Ce script automatise :
- La création de la structure de dossiers recommandée pour FastAPI
- La génération des fichiers principaux (`main.py`, `config.py`, etc.)
- L’ajout d’un environnement virtuel Python
- L’installation des dépendances nécessaires (FastAPI, Uvicorn, SQLAlchemy, etc.)
- La mise en place d'une authentification JWT basique (email et mot de passe)

## 📁 Structure générée

```
app/
  core/
    __init__.py
    config.py
  routes/
    __init__.py
    auth.py
  schemas/
    __init__.py
    user.py
    token.py
  sqlmodels/
    __init__.py
    user.py
  services/
    __init__.py
    auth.py
  utils/
    __init__.py
    dataset/
      __init__.py
      users.py
  middleware/__init__.py
  main.py
venv/
.env
requirements.txt
README.md
```

## 🛠️ Utilisation

1. Exécutez le script :
   ```bash
   python InitFastAPIProject.py
   ```
2. Indiquez le chemin du projet (ou laissez vide pour le dossier courant)
3. Le script crée la structure, installe les dépendances et prépare le projet

## 📦 Dépendances installées
- fastapi
- uvicorn[standard]
- sqlalchemy
- pydantic
- alembic
- python-dotenv
- httpx
- pytest
- python-jose[cryptography]
- passlib[bcrypt]

## ⚡ Démarrage rapide
Après l’initialisation :

```bash
# Activez l’environnement virtuel
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Lancez le serveur
uvicorn app.main:app --reload
```

Votre API sera accessible sur http://localhost:8000

---

*Ce script vous fait gagner du temps et vous permet de démarrer rapidement un projet FastAPI professionnel !*
