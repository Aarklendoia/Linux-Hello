import os
import socket
import getpass
import cv2
import numpy as np

from .camera import open_camera
from .embeddings import get_embedding
from .config import load_config

SOCKET_PATH = "/run/linux-hello/daemon.sock"

def get_faces_dir(user: str = None):
    """Get user-specific faces directory"""
    if user is None:
        user = getpass.getuser()
    home = os.path.expanduser(f"~{user}" if user != getpass.getuser() else "~")
    faces_dir = os.path.join(home, ".linux-hello", "faces")
    return faces_dir


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class HelloDaemon:
    def __init__(self):
        self.config = load_config()

    def _load_user_embeddings(self, user: str):
        faces_dir = get_faces_dir(user)
        # Check if user has a single .npy file or subdirectory
        if os.path.isfile(f"{faces_dir}/{user}.npy"):
            # Single embedding per user
            try:
                emb = np.load(f"{faces_dir}/{user}.npy")
                return [emb]
            except Exception:
                return []
        
        # Multiple embeddings per user (in subdirectory)
        if not os.path.isdir(faces_dir):
            return []

        embeddings = []
        for name in os.listdir(faces_dir):
            if not name.endswith(".npy"):
                continue
            path = os.path.join(faces_dir, name)
            try:
                emb = np.load(path)
                embeddings.append(emb)
            except Exception:
                continue

        return embeddings

    def authenticate(self) -> str:
        user = getpass.getuser()
        threshold = self.config.get("threshold", 0.35)

        embeddings = self._load_user_embeddings(user)
        if not embeddings:
            return "NO_FACE"

        cap = open_camera()
        if cap is None:
            return "NO_CAMERA"

        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "NO_CAMERA"

        emb_live = get_embedding(frame)
        if emb_live is None:
            return "NO_FACE"

        for emb_saved in embeddings:
            sim = cosine_similarity(emb_live, emb_saved)
            if sim >= threshold:
                return "OK"

        return "FAIL"

    def _prepare_socket(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(5)
        os.chmod(SOCKET_PATH, 0o666)
        return server

    def run(self):
        server = self._prepare_socket()

        while True:
            conn, _ = server.accept()
            try:
                data = conn.recv(1024).decode().strip()
                if data == "AUTH":
                    result = self.authenticate()
                    conn.send(result.encode())
                else:
                    conn.send(b"ERROR")
            except Exception:
                try:
                    conn.send(b"ERROR")
                except Exception:
                    pass
            finally:
                conn.close()


def main():
    daemon = HelloDaemon()
    daemon.run()