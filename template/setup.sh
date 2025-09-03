#!/usr/bin/env bash
set -euo pipefail

echo "[setup] Début du script d'installation (Linux / Bash)"

# --- Créer le venv s'il n'existe pas ---
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    if command -v python3 >/dev/null 2>&1; then
        echo "[setup] python3 détecté : création de l'environnement virtuel..."
        python3 -m venv venv
    elif command -v python >/dev/null 2>&1; then
        echo "[setup] python détecté : création de l'environnement virtuel..."
        python -m venv venv
    else
        echo "Erreur : python n'est pas installé. Installez python3 et réessayez." >&2
        exit 1
    fi
else
    echo "[setup] venv existe déjà, pas de création."
fi

# --- Activer le venv ---
# shellcheck source=/dev/null
. "venv/bin/activate"

echo "[setup] venv activé : $(which python) ($(python --version 2>&1))"

# --- Mettre à jour pip ---
python -m pip install --upgrade pip

# --- Installer les dépendances ---
if [ -f "requirements.txt" ]; then
    echo "[setup] Installation des dépendances depuis requirements.txt..."
    pip install -r requirements.txt
else
    echo "[setup] Aucun fichier requirements.txt trouvé, aucune dépendance installée."
fi

echo "[setup] Environnement virtuel activé et dépendances installées."

exit 0
