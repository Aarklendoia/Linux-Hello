#!/bin/bash
# Test du module PAM Linux Hello

set -e

echo "=== Test du Module PAM Linux Hello ==="
echo ""

# Démarrer le daemon
echo "1. Démarrage du daemon..."
cd /home/edtech/Documents/linux-hello-rust
./target/debug/hello-daemon --debug &
DAEMON_PID=$!
sleep 3
echo "   Daemon PID: $DAEMON_PID"
echo ""

# Test avec pamtester
echo "2. Test PAM avec l'utilisateur courant..."
USERNAME=$(whoami)
echo "   Utilisateur: $USERNAME"
echo ""

echo "3. Appel pamtester..."
# pamtester demande le mot de passe, on passe vide ou on utilise --version
# pour juste voir si le module peut être chargé
pamtester -v linux-hello-test "$USERNAME" authenticate || {
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo "   ✓ Authentification réussie (PAM_SUCCESS)"
    else
        echo "   ! Authentification échouée ou erreur: $RESULT"
    fi
}

echo ""
echo "4. Arrêt du daemon..."
kill $DAEMON_PID 2>/dev/null || true
wait $DAEMON_PID 2>/dev/null || true
echo "   ✓ Daemon arrêté"
echo ""

echo "=== Test terminé ==="
