#!/bin/bash
# Préparer le test: enregistrer un visage pour l'utilisateur courant

set -e

echo "=== Préparation du test PAM ==="
echo ""

cd /home/edtech/Documents/linux-hello-rust

# Démarrer le daemon
echo "1. Démarrage du daemon..."
./target/debug/hello-daemon --debug &
DAEMON_PID=$!
sleep 3

echo "2. Enregistrement d'un visage pour l'utilisateur courant..."
USERNAME=$(whoami)
USER_ID=$(id -u)

# Appeler RegisterFace via D-Bus
REQUEST="{\"user_id\":$USER_ID,\"context\":\"test\",\"timeout_ms\":5000,\"num_samples\":1}"
echo "   Requête: $REQUEST"
echo ""

RESPONSE=$(dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.RegisterFace string:"$REQUEST" 2>&1 | tail -1)
echo "   Réponse: $RESPONSE"
echo ""

echo "3. Vérification: énumération des visages..."
dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.ListFaces uint32:$USER_ID 2>&1 | tail -1 | head -c 100
echo "..."
echo ""

echo "4. Arrêt du daemon..."
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true

echo ""
echo "✓ Préparation terminée!"
echo "Vous pouvez maintenant exécuter: ./test-pam.sh"
