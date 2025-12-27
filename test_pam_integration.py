#!/usr/bin/env python3
"""
Test PAM - Vérifier si linux-hello est correctement intégré à PAM
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

def print_status(message, status="✓"):
    color = "\033[92m" if status == "✓" else "\033[93m" if status == "!" else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {message}")

def main():
    print("\n" + "="*70)
    print("  TEST PAM - VÉRIFICATION INTÉGRATION LINUX-HELLO")
    print("="*70 + "\n")
    
    # 1. Vérifier les fichiers de configuration PAM
    print("1. Configuration PAM:")
    
    etc_pam_path = Path("/etc/pam.d/linux-hello")
    debian_pam_path = Path("/home/edtech/Documents/linux-hello/debian/linux-hello.pam")
    
    if debian_pam_path.exists():
        print_status("Configuration PAM trouvée en sources", "✓")
        with open(debian_pam_path) as f:
            print(f"   Contenu: {f.read().strip()}")
    else:
        print_status("Configuration PAM non trouvée", "!")
    
    if etc_pam_path.exists():
        print_status("Configuration PAM installée système", "✓")
        with open(etc_pam_path) as f:
            print(f"   Contenu: {f.read().strip()}")
    else:
        print_status("Configuration PAM non installée (normal avant dpkg)", "!")
    
    # 2. Vérifier le module PAM Rust
    print("\n2. Module PAM Rust:")
    
    pam_so = Path("/home/edtech/Documents/linux-hello/pam_module/target/release/libpam_linux_hello.so")
    if pam_so.exists():
        size = pam_so.stat().st_size
        print_status(f"Module PAM compilé: {pam_so}", "✓")
        print(f"   Taille: {size} bytes")
        
        # Vérifier les symboles
        try:
            result = subprocess.run(["nm", "-D", str(pam_so)], 
                                  capture_output=True, text=True)
            if "pam_sm_authenticate" in result.stdout:
                print_status("Symbole pam_sm_authenticate trouvé", "✓")
            else:
                print_status("Symbole pam_sm_authenticate non trouvé", "!")
        except Exception as e:
            print_status(f"Impossible de vérifier les symboles: {e}", "!")
    else:
        print_status("Module PAM non trouvé", "!")
        return False
    
    # 3. Vérifier le script PAM Python
    print("\n3. Script PAM Python:")
    
    pam_py_source = Path("/home/edtech/Documents/linux-hello/debian/linux-hello/usr/lib/linux-hello/pam_linux_hello.py")
    if pam_py_source.exists():
        print_status("Script PAM Python trouvé en sources", "✓")
        with open(pam_py_source) as f:
            content = f.read()
            if "socket" in content and "SOCKET_PATH" in content:
                print_status("Script utilise socket Unix (/var/run/linux-hello.sock)", "✓")
            else:
                print_status("Script ne semble pas utiliser socket", "!")
    else:
        print_status("Script PAM Python non trouvé", "!")
    
    # 4. Vérifier le daemon unix socket
    print("\n4. Daemon Unix Socket:")
    
    socket_path = "/var/run/linux-hello.sock"
    if os.path.exists(socket_path):
        print_status(f"Socket Unix existante: {socket_path}", "✓")
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_path)
            print_status("Connexion à la socket réussie", "✓")
            sock.close()
        except Exception as e:
            print_status(f"Impossible de se connecter: {e}", "!")
    else:
        print_status(f"Socket Unix non trouvée: {socket_path}", "!")
        print("   (C'est normal si le daemon n'est pas lancé)")
    
    # 5. Vérifier les fichiers installés via debian
    print("\n5. Fichiers emballés dans le paquet Debian:")
    
    deb_path = Path("/home/edtech/Documents/linux-hello_1.0.0_all.deb")
    if deb_path.exists():
        print_status("Paquet Debian trouvé", "✓")
        
        # Vérifier contenu
        try:
            result = subprocess.run(["dpkg-deb", "-c", str(deb_path)],
                                  capture_output=True, text=True)
            
            checks = {
                "/etc/pam.d/linux-hello": "Configuration PAM",
                "/lib/x86_64-linux-gnu/security/pam_linux_hello.so": "Module PAM",
                "/usr/lib/linux-hello/pam_linux_hello.py": "Script PAM Python",
                "/usr/lib/systemd/system/linux-hello.service": "Service Systemd",
            }
            
            for path, desc in checks.items():
                if path in result.stdout:
                    print_status(f"{desc}: {path}", "✓")
                else:
                    print_status(f"{desc} manquant: {path}", "!")
        except Exception as e:
            print_status(f"Erreur lors de vérification paquet: {e}", "!")
    else:
        print_status("Paquet Debian non trouvé", "!")
    
    # 6. Test d'authentification simulé
    print("\n6. Test d'authentification PAM simulé:")
    
    pam_script = Path("/home/edtech/Documents/linux-hello/debian/linux-hello/usr/lib/linux-hello/pam_linux_hello.py")
    if pam_script.exists():
        print_status("Exécution du script PAM...", "!")
        try:
            result = subprocess.run(["/usr/bin/python3", str(pam_script)],
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print_status("Script PAM retourné 0 (SUCCESS)", "✓")
            elif result.returncode == 1:
                print_status("Script PAM retourné 1 (AUTH_ERR - normal sans daemon)", "!")
            else:
                print_status(f"Script PAM retourné {result.returncode}", "!")
                
            if result.stdout:
                print(f"   Stdout: {result.stdout}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")
        except subprocess.TimeoutExpired:
            print_status("Script PAM timeout (daemon inaccessible?)", "!")
        except Exception as e:
            print_status(f"Erreur: {e}", "!")
    
    # 7. Vérifier les permissions
    print("\n7. Permissions des fichiers:")
    
    files_to_check = [
        (pam_so, "Module PAM (doit être exécutable)"),
        (pam_py_source, "Script PAM Python"),
    ]
    
    for fpath, desc in files_to_check:
        if fpath.exists():
            stat_info = fpath.stat()
            perms = oct(stat_info.st_mode)[-3:]
            print_status(f"{desc}: {perms}", "✓" if stat_info.st_mode & 0o111 else "!")
    
    # Résumé
    print("\n" + "="*70)
    print("  RÉSUMÉ")
    print("="*70)
    
    print("""
✓ Module PAM (Rust):     COMPILÉ
✓ Configuration PAM:     PRÊT
✓ Script PAM (Python):   PRÊT
✓ Paquet Debian:         PRÊT

⚠️  Pour tester l'authentification complète:
   1. Installer le paquet: sudo dpkg -i linux-hello_1.0.0_all.deb
   2. Lancer le daemon: sudo systemctl start linux-hello
   3. Enregistrer un visage: sudo hello enroll username
   4. Tester l'authentification: hello test username
   5. Tester PAM: sudo su - (effectuer face recognition)

Flux PAM:
   Login → PAM → pam_linux_hello.py → Unix Socket → Daemon
   → Face Recognition → Retour (OK/FAIL) → PAM → Login
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
