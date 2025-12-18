#!/bin/bash
set -e

VENV="/opt/linux-hello/venv"
PYTHON="/usr/bin/python3"
WHEEL_DIR="/usr/share/linux-hello"

echo "[linux-hello] Vérification du venv…"

# Créer le venv s'il n'existe pas
if [ ! -d "$VENV" ]; then
    echo "[linux-hello] Création du venv…"
    $PYTHON -m venv --system-site-packages "$VENV"
fi

# Installer / réinstaller les dépendances Python
echo "[linux-hello] Installation des dépendances…"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install insightface opencv-python matplotlib numpy click psutil rich

# Installer le paquet linux_hello depuis le wheel
echo "[linux-hello] Installation du paquet linux_hello…"
if [ -f "$WHEEL_DIR"/linux_hello-*.whl ]; then
    WHEEL=$(ls "$WHEEL_DIR"/linux_hello-*.whl | head -n 1)
    echo "[linux-hello] Utilisation du wheel: $WHEEL"
    "$VENV/bin/pip" install --force-reinstall "$WHEEL"
else
    echo "[linux-hello] ERREUR: wheel linux_hello introuvable dans $WHEEL_DIR"
    exit 1
fi

echo "[linux-hello] Venv réparé."