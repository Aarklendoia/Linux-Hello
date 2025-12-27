#!/usr/bin/env python3
"""
Script pour tester la compilation debian du projet linux-hello
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None, show_output=True):
    """Run a command and return success status"""
    try:
        print(f"\n$ {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=not show_output)
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Test de Compilation Debian - Linux Hello")
    print("="*60)
    
    linux_hello_dir = Path("/home/edtech/Documents/linux-hello")
    
    print("\n1. Vérification de l'environnement:")
    
    # Check if dpkg-buildpackage is available
    if not Path("/usr/bin/dpkg-buildpackage").exists():
        print("✗ dpkg-buildpackage n'est pas installé")
        print("  Installation: sudo apt install devscripts")
        return False
    print("✓ dpkg-buildpackage est disponible")
    
    # Check if debian/ directory exists
    debian_dir = linux_hello_dir / "debian"
    if not debian_dir.exists():
        print(f"✗ Répertoire debian/ non trouvé: {debian_dir}")
        return False
    print(f"✓ Répertoire debian/ trouvé")
    
    # Check required files
    required_files = ["control", "rules", "changelog", "source/format"]
    for file in required_files:
        file_path = debian_dir / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} manquant")
            return False
    
    print("\n2. Commande de compilation debian:")
    print(f"  Répertoire: {linux_hello_dir}")
    print(f"  Commande: dpkg-buildpackage -us -uc")
    print()
    print("  ⚠️  Cette commande va:")
    print("     - Construire le paquet source et binaire")
    print("     - Créer un fichier .deb installable")
    print("     - Utiliser la configuration debian/control")
    print()
    
    print("Pour compiler le paquet debian:")
    print(f"  cd {linux_hello_dir}")
    print("  dpkg-buildpackage -us -uc")
    print()
    
    print("Après compilation, le paquet sera disponible dans:")
    print(f"  /home/edtech/Documents/linux-hello_*.deb")
    print()
    
    print("Pour installer le paquet:")
    print("  sudo dpkg -i linux-hello_*.deb")
    print("  sudo systemctl start linux-hello")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
