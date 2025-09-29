@echo off
@REM Se placer dans le répertoire du script
cd /d "%~dp0/.."


@REM Supprimer le dossier /generated s'il existe déjà avec droits admin et récursivité forcée
if exist "generated" (
    echo Suppression du dossier generated existant...

    @REM Tentative 1: Suppression standard
    rmdir /s /q "generated" 2>nul

    if exist "generated" (
        echo Tentative de suppression avec attributs modifies...
        @REM Retirer tous les attributs de protection (lecture seule, système, caché)
        attrib -r -s -h "generated\*.*" /s /d 2>nul
        rmdir /s /q "generated" 2>nul
    )

    if exist "generated" (
        echo Tentative de suppression avec takeown et icacls...
        @REM Prendre possession du dossier et donner contrôle total
        takeown /f "generated" /r /d y >nul 2>&1
        icacls "generated" /grant %USERNAME%:F /t /c /q >nul 2>&1
        rmdir /s /q "generated" 2>nul
    )

    if exist "generated" (
        echo Tentative de suppression avec rd et del forces...
        @REM Forcer la suppression de tous les fichiers puis du dossier
        del /f /s /q "generated\*.*" 2>nul
        for /d %%i in ("generated\*") do rd /s /q "%%i" 2>nul
        rd /s /q "generated" 2>nul
    )

    if exist "generated" (
        echo Tentative de suppression avec powershell...
        @REM Utiliser PowerShell pour suppression forcée
        powershell -Command "try { Remove-Item -Path 'generated' -Recurse -Force -ErrorAction SilentlyContinue } catch { }" 2>nul
    )

    if exist "generated" (
        echo Attente et nouvelle tentative...
        timeout /t 3 /nobreak >nul
        rmdir /s /q "generated" 2>nul
    )

    if exist "generated" (
        echo ERREUR CRITIQUE: Le dossier 'generated' ne peut pas etre supprime.
        echo Causes possibles:
        echo - Fichiers ouverts dans un editeur ou explorateur
        echo - Processus utilisant des fichiers du dossier
        echo - Permissions insuffisantes
        echo.
        echo Solutions:
        echo 1. Fermez tous les programmes susceptibles d'utiliser ce dossier 
        echo     Containers docker
        echo 2. Redemarrez l'ordinateur si necessaire
        echo.
        pause
        exit /b 1
    )

    echo Dossier generated supprime avec succes.
)
echo Lancement de l'initialisation du projet FastAPI...
python InitFastAPIProject.py
pause