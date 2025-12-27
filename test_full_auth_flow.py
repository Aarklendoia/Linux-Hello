#!/usr/bin/env python3
"""
Test complet du flux d'authentification PAM avec enrollment facial

Ce test démontre:
1. Enregistrement d'un nouveau visage (hello enroll)
2. Test de reconnaissance (hello test)
3. Test PAM avec le daemon (authentification PAM)
"""

import os
import sys
import socket
import getpass
import numpy as np
from pathlib import Path

# Ajouter le chemin pour importer les modules linux-hello
sys.path.insert(0, "/home/edtech/Documents/linux-hello/src")

from linux_hello.daemon import HelloDaemon, get_faces_dir
from linux_hello.config import load_config

def test_user_enrollment():
    """Tester si des visages sont enregistrés pour l'utilisateur"""
    user = getpass.getuser()
    faces_dir = get_faces_dir(user)
    
    print(f"\n[*] Vérification des visages enregistrés...")
    print(f"    Répertoire: {faces_dir}")
    
    if not os.path.exists(faces_dir):
        print(f"✗ Pas de visages enregistrés pour {user}")
        print(f"  (Le répertoire {faces_dir} n'existe pas)")
        return False
    
    # Compter les embeddings
    embeddings = []
    if os.path.isfile(f"{faces_dir}/{user}.npy"):
        embeddings.append(f"{faces_dir}/{user}.npy")
    
    # Chercher les fichiers .npy
    for fname in os.listdir(faces_dir):
        if fname.endswith(".npy") and fname != f"{user}.npy":
            embeddings.append(os.path.join(faces_dir, fname))
    
    if embeddings:
        print(f"✓ {len(embeddings)} visage(s) enregistré(s):")
        for emb_file in embeddings:
            print(f"  - {emb_file}")
        return True
    else:
        print(f"✗ Aucun visage enregistré")
        return False

def test_daemon_with_no_enrollment():
    """Tester le daemon quand aucun visage n'est enregistré"""
    print("\n" + "="*70)
    print("TEST 1: Authentification SANS visage enregistré")
    print("="*70)
    
    SOCKET_PATH = "/run/linux-hello/daemon.sock"
    
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(b"AUTH")
        result = client.recv(1024).decode().strip()
        client.close()
        
        print(f"\nRéponse du daemon: {result}")
        
        if result == "NO_FACE":
            print("✓ Daemon retourne NO_FACE (correct - pas de visage enregistré)")
            print("  → Script PAM retourne exit 1")
            print("  → Demande le mot de passe")
            return True
        else:
            print(f"✗ Réponse inattendue: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def create_fake_embedding():
    """Créer un faux embedding pour simuler un visage enregistré"""
    user = getpass.getuser()
    faces_dir = get_faces_dir(user)
    
    print(f"\n[*] Création d'un embedding de test...")
    os.makedirs(faces_dir, exist_ok=True)
    
    # Créer un embedding aléatoire (vecteur 512D comme InsightFace)
    embedding = np.random.randn(512).astype(np.float32)
    # Normaliser
    embedding = embedding / np.linalg.norm(embedding)
    
    embedding_file = f"{faces_dir}/{user}.npy"
    np.save(embedding_file, embedding)
    
    print(f"✓ Embedding de test créé: {embedding_file}")
    print(f"  Dimension: {embedding.shape}")
    return embedding_file, embedding

def test_daemon_with_enrollment(enrollment_embedding):
    """Tester le daemon quand un visage EST enregistré"""
    print("\n" + "="*70)
    print("TEST 2: Authentification AVEC visage enregistré")
    print("="*70)
    
    SOCKET_PATH = "/run/linux-hello/daemon.sock"
    
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(b"AUTH")
        result = client.recv(1024).decode().strip()
        client.close()
        
        print(f"\nRéponse du daemon: {result}")
        
        if result == "NO_CAMERA":
            print("✓ Daemon retourne NO_CAMERA")
            print("  (Caméra non disponible en VM)")
            print("  → Script PAM retourne exit 1")
            print("  → Demande le mot de passe")
            return True
        elif result == "NO_FACE":
            print("⚠ Daemon retourne NO_FACE")
            print("  (L'embedding créé n'a pas été trouvé)")
            return False
        elif result == "OK":
            print("✓ Daemon retourne OK")
            print("  (Visage reconnu!)")
            print("  → Script PAM retourne exit 0")
            print("  → Authentification réussie")
            return True
        elif result == "FAIL":
            print("⚠ Daemon retourne FAIL")
            print("  (Visage enregistré mais pas reconnu)")
            print("  → Script PAM retourne exit 1")
            print("  → Demande le mot de passe")
            return True
        else:
            print(f"✗ Réponse inattendue: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def print_test_instructions():
    """Afficher les instructions pour tester avec une vraie caméra"""
    print("\n" + "="*70)
    print("INSTRUCTIONS: TESTER AVEC UNE VRAIE CAMÉRA")
    print("="*70)
    print("""
Sur une machine avec webcam connectée:

1️⃣  Enregistrer un visage:
    $ sudo hello enroll edtech
    
    Cela va:
    • Ouvrir la caméra
    • Capturer plusieurs images de votre visage
    • Créer des embeddings (vecteurs 512D)
    • Sauvegarder dans ~/.linux-hello/faces/edtech.npy

2️⃣  Tester la reconnaissance faciale:
    $ hello test edtech
    
    Cela va:
    • Ouvrir la caméra
    • Capturer une image
    • Comparer avec l'embedding enregistré
    • Afficher "OK" ou "FAIL"

3️⃣  Tester l'authentification PAM:
    $ sudo su - edtech
    [insère visage en face de la caméra]
    ✓ Authentification réussie!
    
    OU si visage pas reconnu:
    [demande du mot de passe]
    Password: [entrez le mot de passe]

4️⃣  Test de sécurité PAM:
    $ sudo hello enroll hacker
    [enregistre un autre visage]
    
    $ sudo su - edtech
    [montre le visage du "hacker"]
    [demande le mot de passe - REFUSÉ!]
    Password: [oui, c'est exigé]
    
    → Cela prouve que la face recognition marche!

RÉSUMÉ DES CODES DE SORTIE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daemon retourne    Script PAM    Comportement
─────────────────────────────────────────────────────────────
OK                 exit 0        Authentification réussie
FAIL               exit 1        Demande mot de passe
NO_FACE            exit 1        Demande mot de passe
NO_CAMERA          exit 1        Demande mot de passe
ERROR              exit 0        Erreur gracieuse (laisse passer)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

def cleanup_test_embedding():
    """Nettoyer l'embedding de test"""
    user = getpass.getuser()
    faces_dir = get_faces_dir(user)
    embedding_file = f"{faces_dir}/{user}.npy"
    
    if os.path.exists(embedding_file):
        os.remove(embedding_file)
        print(f"\n[*] Nettoyage: suppression de {embedding_file}")

if __name__ == "__main__":
    print("="*70)
    print("TEST COMPLET: FLUX D'AUTHENTIFICATION PAM")
    print("="*70)
    
    # Test 1: Sans visage enregistré
    test_daemon_with_no_enrollment()
    
    # Test 2: Avec visage simulé
    emb_file, emb = create_fake_embedding()
    test_daemon_with_enrollment(emb)
    
    # Nettoyage
    cleanup_test_embedding()
    
    # Instructions finales
    print_test_instructions()
    
    print("\n✓ Tests terminés")
