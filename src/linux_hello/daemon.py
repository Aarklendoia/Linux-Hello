import socket
import os
import cv2
import numpy as np

os.environ["INSIGHTFACE_HOME"] = "/var/lib/linux-hello/.insightface"
os.environ["MPLCONFIGDIR"] = "/var/lib/linux-hello/.config/matplotlib"

import insightface

SOCKET_PATH = "/run/linux-hello/linux-hello.sock"
FACE_DIR = "/var/lib/linux-hello/faces"
DEVICE = "/dev/video0"


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class HelloDaemon:
    def __init__(self):
        self.model = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )
        self.model.prepare(ctx_id=0)
        self.load_faces()

    def load_faces(self):
        """Chargement des embeddings en mémoire (optionnel)."""
        self.faces = {}
        if not os.path.isdir(FACE_DIR):
            return
        for f in os.listdir(FACE_DIR):
            if f.endswith(".npy"):
                name = f[:-4]
                self.faces[name] = np.load(os.path.join(FACE_DIR, f))

    def authenticate(self, username):
        if username not in self.faces:
            return "NO_FACE"

        saved = self.faces[username]

        cap = cv2.VideoCapture(DEVICE)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return "NO_CAMERA"

        faces = self.model.get(frame)
        if not faces:
            return "NO_FACE"

        live = faces[0].embedding
        sim = cosine_similarity(live, saved)

        return "OK" if sim > 0.35 else "FAIL"

    def run(self):
        # S'assurer que le dossier du socket existe
        socket_dir = os.path.dirname(SOCKET_PATH)
        os.makedirs(socket_dir, exist_ok=True)

        # Supprimer un ancien socket si présent
        try:
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
        except OSError:
            pass

        # Créer le socket Unix
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            server.bind(SOCKET_PATH)
        except OSError as e:
            raise RuntimeError(f"Impossible de binder le socket {SOCKET_PATH}: {e}")

        server.listen(1)

        # Permissions : lecture/écriture pour tous (CLI utilisateur)
        os.chmod(SOCKET_PATH, 0o666)

        # Boucle principale
        while True:
            conn, _ = server.accept()
            try:
                data = conn.recv(1024).decode().strip()

                if data.startswith("AUTH "):
                    username = data.split(" ", 1)[1]
                    result = self.authenticate(username)
                    conn.send(result.encode())

                elif data == "reload":
                    self.load_faces()
                    conn.send(b"OK")

            finally:
                conn.close()


def main():
    daemon = HelloDaemon()
    daemon.run()
