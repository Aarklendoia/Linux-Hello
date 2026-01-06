#!/bin/bash
# Installation du module PAM Linux Hello
# À exécuter avec sudo

set -e

echo "Installation du module PAM Linux Hello"

# Vérifier qu'on est root
if [ "$EUID" -ne 0 ]; then 
    echo "Ce script doit être exécuté avec sudo"
    exit 1
fi

# Chemins
SOURCE="/home/edtech/Documents/linux-hello-rust/target/release/libpam_linux_hello.so"
DEST="/lib/x86_64-linux-gnu/security/pam_linux_hello.so"

if [ ! -f "$SOURCE" ]; then
    echo "Erreur: $SOURCE not found"
    echo "Veuillez d'abord compiler: cargo build --release"
    exit 1
fi

# Installer le module
echo "Copie du module PAM..."
cp "$SOURCE" "$DEST"
chmod 644 "$DEST"

# Vérifier l'installation
if [ -f "$DEST" ]; then
    echo "✓ Module PAM installé: $DEST"
    ls -la "$DEST"
else
    echo "✗ Installation échouée"
    exit 1
fi

# Afficher la configuration PAM actuelle
echo ""
echo "Configuration PAM actuellement active:"
echo "----"
cat /etc/pam.d/sudo | grep -E "^auth|#" || true
echo "----"

echo ""
echo "Installation complète!"
echo "Pour tester:"
echo "  sudo ls /"
