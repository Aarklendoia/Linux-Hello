import os
import cv2
import numpy as np
import getpass
import pwd

from .camera import open_camera
from .embeddings import get_embedding

FACES_DIR = "/var/lib/linux-hello/faces"

def enroll():
    user = getpass.getuser()
    user_dir = os.path.join(FACES_DIR, user)

    # Permissions strictes
    os.makedirs(user_dir, exist_ok=True)
    info = pwd.getpwnam(user)
    os.chown(user_dir, info.pw_uid, info.pw_gid)
    os.chmod(user_dir, 0o700)

    cap = open_camera()
    if cap is None:
        print("Impossible d'ouvrir la caméra.")
        return

    print("Regardez la caméra. Appuyez sur Entrée pour capturer.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture", frame)
        if cv2.waitKey(1) == 13:  # Entrée
            break

    cap.release()
    cv2.destroyAllWindows()

    emb = get_embedding(frame)
    if emb is None:
        print("Aucun visage détecté.")
        return

    # Numérotation
    existing = [f for f in os.listdir(user_dir) if f.endswith(".npy")]
    index = len(existing)

    path = os.path.join(user_dir, f"{index}.npy")
    np.save(path, emb)

    print(f"✅ Visage enregistré : {path}")