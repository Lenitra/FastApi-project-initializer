@echo off
setlocal

@REM === Se placer dans le dossier du projet ===
cd /d %~dp0/..


REM === Créer le venv s'il n'existe pas ===
if not exist ".venv\Scripts\activate.bat" (
    where uv >nul 2>nul
    if %errorlevel%==0 (
        echo [setup] uv detecte: creation de l'environnement virtuel...
        uv venv .venv --clear
    ) else (
        echo [setup] uv non detecté.
        echo [setup] Installation de uv avec pip...
        pip install uv
        if %errorlevel%==0 (
            echo [setup] uv installé.
        ) else (
            echo [setup] Erreur d'installation de uv avec pip...
            exit /b 1
        )
    )
)

REM === Activer le venv ===
call ".venv\Scripts\activate.bat"

REM === Installer les dependances ===
where uv >nul 2>nul
if %errorlevel%==0 (
    echo [setup] Installation des dependances avec uv...
    uv sync
) else (
    echo [setup] Erreur d'installation des dependances avec uv...*
    exit /b 1
)

echo [setup] Environnement virtuel active et dependances installees.
echo [setup] Pour demarrer le serveur, lancez run.bat
endlocal
