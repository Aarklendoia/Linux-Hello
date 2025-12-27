#!/usr/bin/env python3
"""
Test script for linux-hello PAM module
Vérifie que le module PAM est compilé et testable
"""

import os
import sys
import subprocess
from pathlib import Path

def print_status(message: str, status: str = "✓"):
    """Print a status message"""
    color = "\033[92m" if status == "✓" else "\033[93m" if status == "!" else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {message}")

def main():
    print("\n" + "="*60)
    print("  Linux Hello - PAM Module Test Suite")
    print("="*60 + "\n")
    
    # Check Python dependencies
    print("1. Vérification des dépendances Python:")
    try:
        import click
        print_status("click est installé", "✓")
    except ImportError:
        print_status("click n'est pas installé", "✗")
        return False
    
    try:
        import insightface
        print_status("insightface est installé", "✓")
    except ImportError:
        print_status("insightface n'est pas installé", "✗")
        return False
    
    try:
        import onnxruntime
        print_status("onnxruntime est installé", "✓")
    except ImportError:
        print_status("onnxruntime n'est pas installé", "✗")
        return False
    
    try:
        import cv2
        print_status("opencv est installé", "✓")
    except ImportError:
        print_status("opencv n'est pas installé", "✗")
        return False
    
    try:
        import numpy
        print_status("numpy est installé", "✓")
    except ImportError:
        print_status("numpy n'est pas installé", "✗")
        return False
    
    # Check Rust toolchain
    print("\n2. Vérification de la toolchain Rust:")
    try:
        result = subprocess.run(["rustc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(result.stdout.strip(), "✓")
        else:
            print_status("rustc not found", "✗")
            return False
    except FileNotFoundError:
        print_status("rustc not found", "✗")
        return False
    
    try:
        result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(result.stdout.strip(), "✓")
        else:
            print_status("cargo not found", "✗")
            return False
    except FileNotFoundError:
        print_status("cargo not found", "✗")
        return False
    
    # Check PAM module compilation
    print("\n3. Vérification de la compilation du module PAM:")
    pam_module_path = Path(__file__).parent / "pam_module" / "target" / "release" / "libpam_linux_hello.so"
    if pam_module_path.exists():
        print_status(f"Module PAM compilé: {pam_module_path}", "✓")
        print_status(f"Taille: {pam_module_path.stat().st_size} bytes", "✓")
    else:
        print_status(f"Module PAM non trouvé: {pam_module_path}", "✗")
        return False
    
    # Check linux-hello package
    print("\n4. Vérification du paquet linux-hello:")
    try:
        import linux_hello
        print_status("Package linux-hello est importable", "✓")
    except ImportError:
        print_status("linux-hello package not found", "✗")
        return False
    
    # Summary
    print("\n" + "="*60)
    print("  ✓ Toutes les dépendances sont prêtes !")
    print("="*60)
    print("\nPour commencer les tests:")
    print("  - Module PAM: /home/edtech/Documents/linux-hello/pam_module/target/release/libpam_linux_hello.so")
    print("  - Python: /home/edtech/Documents/linux-hello/.venv/bin/python")
    print("\nCommandes utiles:")
    print("  - Tester le package: .venv/bin/python -m pytest")
    print("  - Utiliser le CLI: .venv/bin/hello --help")
    print("  - Compiler le module PAM: cd pam_module && cargo build --release")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
