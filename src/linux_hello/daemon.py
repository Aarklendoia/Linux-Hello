import socket
import os
import cv2
import numpy as np
import insightface
import getpass


SOCKET_PATH = "/var/run/linux-hello.sock"
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

    def authenticate(self, username):
        user = getpass.getuser()
        faces_dir = f"/var/lib/linux-hello/faces/{user}"

        path = os.path.join(faces_dir, f"{username}.npy")
        if not os.path.exists(path):
            return "NO_FACE"

        saved = np.load(path)

        cap = cv2.VideoCapture(DEVICE)
        ret, frame = cap.read()
        cap.release()

        faces = self.model.get(frame)
        if not faces:
            return "NO_FACE"

        live = faces[0].embedding
        sim = cosine_similarity(live, saved)

        return "OK" if sim > 0.35 else "FAIL"

    def run(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(1)
        os.chmod(SOCKET_PATH, 0o666)

        while True:
            conn, _ = server.accept()
            data = conn.recv(1024).decode().strip()

            if data.startswith("AUTH "):
                username = data.split(" ", 1)[1]
                result = self.authenticate(username)
                conn.send(result.encode())

            conn.close()


def main():
    daemon = HelloDaemon()
    daemon.run()
