#!/bin/bash
# Test du module PAM Linux Hello avec sudo

set -e

echo "=== Test PAM Linux Hello avec sudo ==="
echo ""

cd /home/edtech/Documents/linux-hello-rust

# Démarrer le daemon
echo "1. Démarrage du daemon..."
./target/debug/hello-daemon --debug &
DAEMON_PID=$!
sleep 3
echo "   ✓ Daemon lancé (PID: $DAEMON_PID)"
echo ""

# Préparation
USERNAME=$(whoami)
USER_ID=$(id -u)
echo "2. Test Setup:"
echo "   Utilisateur: $USERNAME"
echo "   UID: $USER_ID"
echo ""

# Vérifier qu'un visage est enregistré
echo "3. Vérification: visages enregistrés..."
FACES=$(dbus-send --session --print-reply --dest=com.linuxhello.FaceAuth /com/linuxhello/FaceAuth com.linuxhello.FaceAuth.ListFaces uint32:"$USER_ID" 2>&1 | grep -o "face_id" | wc -l)
echo "   Visages trouvés: $FACES"

if [ "$FACES" -eq 0 ]; then
    echo ""
    echo "   ⚠️  Aucun visage enregistré! Enregistrement..."
    dbus-send --session --print-reply \
      --dest=com.linuxhello.FaceAuth \
      /com/linuxhello/FaceAuth \
      com.linuxhello.FaceAuth.RegisterFace \
      string:"{\"user_id\":$USER_ID,\"context\":\"sudo\",\"timeout_ms\":5000,\"num_samples\":1}" > /dev/null 2>&1
    echo "   ✓ Visage enregistré"
fi
echo ""

# Test 1: Appel Verify direct via D-Bus
echo "4. Test 1: Vérification via D-Bus direct..."
VERIFY_REQUEST="{\"user_id\":$USER_ID,\"context\":\"sudo\",\"timeout_ms\":3000}"
if dbus-send --session --print-reply \
  --dest=com.linuxhello.FaceAuth \
  /com/linuxhello/FaceAuth \
  com.linuxhello.FaceAuth.Verify \
  string:"$VERIFY_REQUEST" 2>&1 | grep -q "Success"; then
    echo "   ✓ Vérification réussie via D-Bus"
else
    echo "   ✗ Vérification échouée"
fi
echo ""

# Test 2: Test avec sudo (nécessite configuration PAM)
echo "5. Test 2: Tentative avec sudo..."
echo "   Note: Cela dépend de la configuration PAM système"
echo ""
echo "   Pour tester avec la configuration PAM locale:"
echo "   sudo -p 'Mot de passe: ' -v"
echo ""
echo "   Ou copier la config PAM:"
echo "   sudo cp sudo-linux-hello.pam /etc/pam.d/sudo"
echo "   sudo cp sudo-linux-hello.pam /etc/pam.d/sudo-i"
echo ""

# Test avec PAM direct si on peut
if command -v pamtester &> /dev/null; then
    echo "6. Test 3: Avec pamtester (si config disponible)..."
    # Créer une config PAM de test
    if [ -f /etc/pam.d/linux-hello-test ]; then
        echo "   Utilisation config /etc/pam.d/linux-hello-test"
        # Note: pamtester lit depuis stdin, on lui passe le password vide
        echo "" | pamtester -v linux-hello-test "$USERNAME" authenticate 2>&1 | head -5 || true
    else
        echo "   Config /etc/pam.d/linux-hello-test non trouvée (ok pour test basique)"
    fi
    echo ""
fi

# Arrêt du daemon
echo "7. Arrêt du daemon..."
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true
echo "   ✓ Daemon arrêté"
echo ""

echo "=== Test terminé ==="
echo ""
echo "Prochaines étapes:"
echo "1. Compiler en release: cargo build --release"
echo "2. Installer: sudo install -m 644 target/release/libpam_linux_hello.so /lib/x86_64-linux-gnu/security/"
echo "3. Configurer PAM: sudo cp sudo-linux-hello.pam /etc/pam.d/sudo"
echo "4. Tester: sudo -v (première authentification faciale!)"
