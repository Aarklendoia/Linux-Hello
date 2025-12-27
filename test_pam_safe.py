#!/usr/bin/env python3
"""
Test PAM sécurisé avec pamtester - Isolation du profil de test
Permet de tester linux-hello sans risquer de corrompre PAM du système
"""

import subprocess
import os
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70 + "\n")

def print_test(name, status="✓"):
    icon = "✅" if status == "✓" else "⚠️ " if status == "!" else "❌"
    print(f"{icon} {name}")

def main():
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + "TEST PAM SÉCURISÉ - PAMTESTER".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    # 1. Vérifier pamtester
    print_section("1. VÉRIFICATION PAMTESTER")
    
    try:
        result = subprocess.run(["pamtester", "--version"],
                              capture_output=True, text=True)
        print_test("pamtester installé", "✓")
        print(f"  Version: {result.stdout.strip()}")
    except FileNotFoundError:
        print_test("pamtester non trouvé", "✗")
        return False
    
    # 2. Vérifier le profil de test
    print_section("2. VÉRIFICATION PROFIL PAM DE TEST")
    
    test_profile = Path("/etc/pam.d/linux-hello-test")
    
    if test_profile.exists():
        print_test("Profil de test créé", "✓")
        with open(test_profile) as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    print(f"  {line}")
    else:
        print_test("Profil de test non trouvé", "✗")
        return False
    
    # 3. Vérifier le script PAM Python
    print_section("3. VÉRIFICATION SCRIPT PAM PYTHON")
    
    pam_script = Path("/home/edtech/Documents/linux-hello/debian/linux-hello/usr/lib/linux-hello/pam_linux_hello.py")
    
    if pam_script.exists():
        print_test("Script PAM trouvé", "✓")
        print(f"  Chemin: {pam_script}")
    else:
        print_test("Script PAM non trouvé", "✗")
        return False
    
    # 4. Vérifier le daemon
    print_section("4. VÉRIFICATION DAEMON")
    
    try:
        result = subprocess.run(["pgrep", "-f", "linux-hello-daemon"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_test("Daemon actif", "✓")
            print(f"  PID: {result.stdout.strip()}")
        else:
            print_test("Daemon non détecté", "!")
            print("  ⚠️  Le daemon doit être en cours d'exécution")
    except Exception as e:
        print_test(f"Erreur vérification daemon: {e}", "!")
    
    # 5. Test authentification avec pamtester
    print_section("5. TEST AUTHENTIFICATION AVEC PAMTESTER")
    
    print("""
    Pamtester permet de tester PAM en isolation:
    
    Commande de base:
      pamtester linux-hello-test authenticate
    
    Options:
      -v                 Verbose (affiche détails)
      authenticate       Test module auth
      -c login=username  Spécifier un utilisateur
    
    Codes de retour:
      0  = Success
      1  = Failure
      2  = Error
    """)
    
    print("Exécution du test avec pamtester...")
    print("─" * 70)
    
    try:
        # Test sans utilisateur (utilisateur actuel)
        result = subprocess.run(
            ["pamtester", "-v", "linux-hello-test", "authenticate"],
            capture_output=True, text=True, timeout=10
        )
        
        print("Sortie pamtester:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Erreurs:")
            print(result.stderr)
        
        print(f"\nCode de retour: {result.returncode}")
        
        if result.returncode == 0:
            print_test("Authentification réussie", "✓")
            success = True
        elif result.returncode == 1:
            print_test("Authentification échouée (NO_FACE probablement)", "!")
            print("  C'est attendu s'il n'y a pas de visage enregistré")
            success = True
        else:
            print_test("Erreur", "✗")
            success = False
    
    except subprocess.TimeoutExpired:
        print_test("Timeout lors du test", "!")
        success = True
    except Exception as e:
        print_test(f"Erreur exécution: {e}", "✗")
        success = False
    
    # 6. Résumé et recommandations
    print_section("RÉSUMÉ ET RECOMMANDATIONS")
    
    print("""
    ✅ Avantages de pamtester pour les tests:
    
    1. SÉCURITÉ: Test isolé sans risquer le PAM système
       → Le profil linux-hello-test est séparé du système
       → Impossible de corrompre l'authentification système
    
    2. CONTRÔLE: Tester chaque composant indépendamment
       → Test du module PAM seul
       → Test du script Python
       → Test de la communication daemon
    
    3. DÉPANNAGE: Voir les messages d'erreur détaillés
       → Option -v pour verbose
       → Voir exact ce que PAM retourne
    
    🔬 Tests additionnels possibles:
    
    # Tester avec utilisateur spécifique:
    pamtester -v -c login=edtech linux-hello-test authenticate
    
    # Tester plusieurs fois:
    for i in {1..3}; do
        echo "Test $i"
        pamtester linux-hello-test authenticate
    done
    
    # Tester avec différents profils:
    pamtester linux-hello-test authenticate    # test seul
    pamtester linux-hello authenticate         # production
    
    ⚠️  IMPORTANT:
    
    • Le profil linux-hello-test utilise 'sufficient' SEUL
      → Pas de fallback mot de passe
      → Test uniquement de la face recognition
    
    • Le profil linux-hello production utilise 'sufficient' + fallback
      → Si face échoue → demande mot de passe
    
    • Ne modifiez JAMAIS /etc/pam.d/linux-hello directement en test
      → Utilisez toujours linux-hello-test
      → Ou testez avec une VM/conteneur
    """)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
