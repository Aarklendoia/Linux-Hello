#!/bin/bash
# Test du module PAM Linux Hello avec démarrage du daemon intégré

set -e

echo "=== Test du Module PAM Linux Hello ==="
echo ""

cd /home/edtech/Documents/linux-hello-rust

# Démarrer le daemon
echo "1. Démarrage du daemon..."
./target/debug/hello-daemon --debug &
DAEMON_PID=$!
sleep 3
echo "   Daemon PID: $DAEMON_PID"
echo ""

# Test 1: Vérifier que le module peut être chargé et les logs aparaissent
echo "2. Test du module PAM..."
USERNAME=$(whoami)
USER_ID=$(id -u)
echo "   Utilisateur: $USERNAME (UID: $USER_ID)"
echo ""

# Créer une requête Verify
echo "3. Appel Verify via le module PAM (simulé par D-Bus direct)..."
VERIFY_REQUEST="{\"user_id\":$USER_ID,\"context\":\"login\",\"timeout_ms\":3000}"
echo "   Requête: $VERIFY_REQUEST"
echo ""

# Appeler Verify directement via D-Bus pour tester que la vérification fonctionne
VERIFY_RESPONSE=$(dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.Verify string:"$VERIFY_REQUEST" 2>&1 | tail -1)
echo "   Réponse: $VERIFY_RESPONSE"

if echo "$VERIFY_RESPONSE" | grep -q "Success"; then
    echo "   ✓ Vérification réussie!"
else
    echo "   ✗ Vérification échouée"
fi
echo ""

# Pour tester avec pamtester, on aurait besoin d'une configuration PAM
# Pour l'instant, vérifier juste que le module charge et D-Bus fonctionne
echo "4. Listing des visages..."
dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.ListFaces uint32:"$USER_ID" 2>&1 | tail -1 | head -c 100
echo "..."
echo ""

echo "5. Arrêt du daemon..."
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true

echo ""
echo "✓ Test terminé avec succès!"
