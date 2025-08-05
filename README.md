
# FastAPI Project Initializer

A Python script to automatically generate the complete structure of a FastAPI project, with all folders, essential files, a basic JWT authentication system, virtual environment, and basic dependencies.

## 🚀 What is this script for?

### This script automates:
- The creation of the recommended folder structure for FastAPI
- The generation of main files (`main.py`, `config.py`, etc.)
- The addition of a Python virtual environment
- The installation of required dependencies (FastAPI, Uvicorn, SQLAlchemy, etc.)
- The setup of a basic JWT authentication system (email and password)
### Upcoming features:
- Role system (admin, user)
- Creation of SQLAlchemy models based on an entities file
- Automatic generation of Pydantic schemas for data validation

## 📁 Generated structure

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

## 🛠️ Usage

1. Run the script:
   ```bash
   python InitFastAPIProject.py
   ```
2. Enter the project path (or leave empty for the current folder)
3. The script creates the structure, installs dependencies, and prepares the project

## 📦 Installed dependencies
- fastapi
- uvicorn[standard]
- sqlalchemy
- pydantic
- alembic
- python-dotenv
- httpx
- pytest
- python-jose[cryptography]
- passlib[argon2]
- python-multipart
- pydantic-settings

## ⚡ Quick start
After initialization:

```bash
# Activate the virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Start the server
uvicorn app.main:app --reload
```

Your API will be available at http://localhost:8000

---

*This script saves you time and lets you quickly start a professional FastAPI project!*
