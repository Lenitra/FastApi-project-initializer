@echo off
echo ========================================
echo     Deployment Docker FastAPI Project
echo ========================================


@REM Navigate to the project's directory
cd /d %~dp0\..

@REM Mise à jour des variables d'environnement
copy "envs\docker.txt" ".env" >nul

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ERREUR: Le fichier .env n'existe pas.
    echo Veuillez créer un fichier .env ou utiliser un fichier d'environnement spécifique.
    echo.
    echo Fichiers d'environnement disponibles:
    if exist "envs\dev.txt" echo   - envs\dev.txt ^(développement^)
    if exist "envs\docker.txt" echo   - envs\docker.txt ^(docker^)
    echo   - .env.example ^(exemple^)
    echo.
    echo Pour utiliser un fichier d'environnement spécifique:
    echo   deploy_docker.bat envs\dev.txt
    pause
    exit /b 1
)

REM Si un paramètre est fourni, utiliser ce fichier d'environnement
if not "%1"=="" (
    if exist "%1" (
        echo Utilisation du fichier d'environnement: %1
        copy "%1" ".env" >nul
        echo Fichier .env mis à jour avec %1
    ) else (
        echo ERREUR: Le fichier %1 n'existe pas.
        pause
        exit /b 1
    )
)

echo Chargement des variables d'environnement depuis .env...

REM Sauvegarder le docker-compose.yml original
if not exist "docker-compose.yml.bak" (
    copy "docker-compose.yml" "docker-compose.yml.bak" >nul
    echo Sauvegarde du docker-compose.yml original créée
)

REM Restaurer le docker-compose.yml original
copy "docker-compose.yml.bak" "docker-compose.yml" >nul

REM Créer un fichier temporaire avec les nouvelles variables d'environnement
echo Ajout automatique des variables d'environnement au docker-compose.yml...
echo. > temp_env.txt

REM Lire les variables du fichier .env et créer les entrées pour docker-compose
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if not "%%a"=="" (
        REM Ignorer les commentaires
        echo %%a | findstr /r "^#" >nul
        if errorlevel 1 (
            REM Ignorer les variables déjà présentes dans docker-compose.yml
            echo %%a | findstr /i "DEBUG DB_HOST DB_PORT DB_USERNAME DB_PASSWORD DB_DATABASE SECRET_KEY ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES" >nul
            if errorlevel 1 (
                echo       - %%a=${%%a} >> temp_env.txt
            )
        )
    )
)

REM Insérer les nouvelles variables dans docker-compose.yml après ACCESS_TOKEN_EXPIRE_MINUTES
powershell -Command "& { $content = Get-Content 'docker-compose.yml'; $output = @(); $found = $false; foreach ($line in $content) { $output += $line; if ($line -match 'ACCESS_TOKEN_EXPIRE_MINUTES' -and -not $found) { $found = $true; if (Test-Path 'temp_env.txt') { $newVars = Get-Content 'temp_env.txt'; foreach ($var in $newVars) { if ($var.Trim() -ne '') { $output += $var } } } } }; $output | Set-Content 'docker-compose.yml' }"

REM Nettoyer les fichiers temporaires
del temp_env.txt >nul 2>&1
del docker-compose.yml.bak >nul 2>&1
echo Variables d'environnement ajoutées automatiquement
echo.

REM Arrêter les conteneurs existants
echo Arrêt des conteneurs existants...
docker-compose down

REM Supprimer les images et volumes orphelins (optionnel)
echo Nettoyage des ressources Docker...
docker system prune -f

REM Construire et démarrer les services
echo Construction et démarrage des conteneurs...
docker-compose --env-file .env up --build -d

REM Vérifier le statut des conteneurs
echo.
echo Statut des conteneurs:
docker-compose ps

REM Afficher les logs en temps réel (optionnel)
echo.
echo ========================================
echo   Déploiement terminé avec succès!
echo ========================================
echo.
echo Pour voir les logs en temps réel:
echo   docker-compose logs -f
echo.
echo Pour arrêter les conteneurs:
echo   docker-compose down
echo.
echo Application accessible sur: http://localhost:8055
echo.


pause