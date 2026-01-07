#!/bin/bash
# Test du module PAM Linux Hello avec screenlock
# Simule le flux d'authentification d'un screenlock

set -e

echo "=== Test PAM Linux Hello avec KDE Screenlock ==="
echo ""

cd /home/edtech/Documents/linux-hello-rust

# Démarrer le daemon
echo "1. Démarrage du daemon..."
./target/debug/hello-daemon --debug &
DAEMON_PID=$!
sleep 3
echo "   ✓ Daemon lancé (PID: $DAEMON_PID)"
echo ""

USERNAME=$(whoami)
USER_ID=$(id -u)

echo "2. Configuration:"
echo "   Utilisateur: $USERNAME (UID: $USER_ID)"
echo "   Contexte: screenlock"
echo "   Timeout: 3000ms"
echo ""

# Vérifier/créer visages
echo "3. Préparation: visages enregistrés..."
FACES=$(dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.ListFaces uint32:"$USER_ID" 2>&1 | grep -o "face_id" | wc -l)
echo "   Visages trouvés: $FACES"

if [ "$FACES" -eq 0 ]; then
    echo "   → Enregistrement d'un nouveau visage..."
    dbus-send --session --print-reply \
      --dest=com.linuxhello.FaceAuth \
      /com/linuxhello/FaceAuth \
      com.linuxhello.FaceAuth.RegisterFace \
      "string:{\"user_id\":$USER_ID,\"context\":\"screenlock\",\"timeout_ms\":5000,\"num_samples\":1}" > /dev/null 2>&1
    echo "   ✓ Visage enregistré"
fi
echo ""

# Simulation de l'authentification screenlock
echo "4. Simulation: flux d'authentification screenlock..."
echo ""
echo "   Appel: dbus-send → Verify (context=screenlock)"
echo ""

VERIFY_REQUEST="{\"user_id\":$USER_ID,\"context\":\"screenlock\",\"timeout_ms\":3000}"
RESPONSE=$(dbus-send --session --print-reply \
  --dest=com.linuxhello.FaceAuth \
  /com/linuxhello/FaceAuth \
  com.linuxhello.FaceAuth.Verify \
  string:"$VERIFY_REQUEST" 2>&1)

echo "$RESPONSE" | tail -5
echo ""

# Vérifier la réponse
if echo "$RESPONSE" | grep -q "Success"; then
    echo "   ✅ AUTHENTIFICATION RÉUSSIE!"
    echo "      → L'écran serait déverrouillé"
    RESULT=0
else
    echo "   ❌ AUTHENTIFICATION ÉCHOUÉE"
    echo "      → L'utilisateur devrait entrer son mot de passe"
    RESULT=1
fi
echo ""

echo "5. Installation du module:"
echo "   Pour activer sur le système:"
echo ""
echo "   sudo install -m 644 target/debug/libpam_linux_hello.so /lib/x86_64-linux-gnu/security/"
echo "   sudo cp kde-screenlock-linux-hello.pam /etc/pam.d/kde"
echo ""
echo "   Ou pour KDE Plasma 5.27+:"
echo "   sudo cp kde-screenlock-linux-hello.pam /etc/pam.d/kde-screenlocker"
echo ""

# Arrêt du daemon
echo "6. Arrêt du daemon..."
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true
echo "   ✓ Daemon arrêté"
echo ""

if [ $RESULT -eq 0 ]; then
    echo "✅ Test screenlock réussi!"
    exit 0
else
    echo "❌ Test screenlock échoué"
    exit 1
fi
