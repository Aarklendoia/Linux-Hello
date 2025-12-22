import os
import cv2
import numpy as np
import getpass
import pwd

from .camera import open_camera
from .embeddings import get_embedding

def get_faces_dir():
    """Get user-specific faces directory"""
    home = os.path.expanduser("~")
    faces_dir = os.path.join(home, ".linux-hello", "faces")
    os.makedirs(faces_dir, exist_ok=True)
    return faces_dir

def enroll():
    user = getpass.getuser()
    faces_dir = get_faces_dir()

    # Ensure directory exists with proper permissions
    os.makedirs(faces_dir, exist_ok=True)
    os.chmod(faces_dir, 0o750)  # rwxr-x--- (owner full, linux-hello group can read)
    
    # Set group ownership to linux-hello for access by daemon
    try:
        import grp
        linux_hello_gid = grp.getgrall()
        for group in grp.getgrall():
            if group.gr_name == "linux-hello":
                os.chown(faces_dir, -1, group.gr_gid)
                break
    except Exception:
        pass

    cap = open_camera()
    if cap is None:
        print("Impossible d'ouvrir la caméra.")
        return

    print("Capturant une image de la caméra…")
    frame = None
    for _ in range(10):  # Try up to 10 frames to get a good one
        ret, frame = cap.read()
        if ret and frame is not None:
            break

    cap.release()

    if frame is None:
        print("Impossible de capturer une image.")
        return

    emb = get_embedding(frame)
    if emb is None:
        print("Aucun visage détecté.")
        return

    # Save with username
    path = os.path.join(faces_dir, f"{user}.npy")
    np.save(path, emb)
    
    # Set proper permissions: owner rw, linux-hello group r
    os.chmod(path, 0o640)
    
    # Set group ownership to linux-hello
    try:
        import grp
        for group in grp.getgrall():
            if group.gr_name == "linux-hello":
                os.chown(path, -1, group.gr_gid)
                break
    except Exception:
        pass

    print(f"✅ Visage enregistré : {path}")