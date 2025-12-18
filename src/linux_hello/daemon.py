import os
import socket
import getpass
import cv2
import numpy as np

from .camera import open_camera
from .embeddings import get_embedding
from .config import load_config

SOCKET_PATH = "/var/run/linux-hello.sock"
FACES_DIR = "/var/lib/linux-hello/faces"


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class HelloDaemon:
    def __init__(self):
        self.config = load_config()

    def _load_user_embeddings(self, user: str):
        user_dir = os.path.join(FACES_DIR, user)
        if not os.path.isdir(user_dir):
            return []

        embeddings = []
        for name in os.listdir(user_dir):
            if not name.endswith(".npy"):
                continue
            path = os.path.join(user_dir, name)
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