@echo off
setlocal


@REM Installer UV et uvicorn s'ils ne sont pas installés
where uv >nul 2>nul
if %errorlevel%==0 (
    echo [setup] Installation de uv...
    uv install uvicorn
) else (
    echo [setup] Installation de uv via pip...
    python -m pip install --upgrade pip
    pip install uvicorn
)

REM === Créer le venv s'il n'existe pas ===
if not exist "venv\Scripts\activate.bat" (
    where uv >nul 2>nul
    if %errorlevel%==0 (
        echo [setup] uv detecte: creation de l'environnement virtuel...
        uv venv venv
    ) else (
        echo [setup] uv non detecte: creation via python -m venv...
        python -m venv venv
    )
)

REM === Activer le venv ===
call "venv\Scripts\activate.bat"

REM === Installer les dependances ===
where uv >nul 2>nul
if %errorlevel%==0 (
    echo [setup] Installation des dependances avec uv...
    uv pip install -r requirements.txt
) else (
    echo [setup] Installation des dependances avec pip...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

echo [setup] Environnement virtuel active et dependances installees.
endlocal
