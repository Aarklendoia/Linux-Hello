import os
import subprocess
import sys
import socket
import cv2

VENV = "/opt/linux-hello/venv"
SOCKET_PATH = "/var/run/linux-hello.sock"
FACES_DIR = "/var/lib/linux-hello/faces"

def check(title, func):
    print(f"→ {title}… ", end="")
    try:
        func()
        print("OK")
    except Exception as e:
        print("FAIL")
        print(f"   {e}")

def check_venv_exists():
    if not os.path.isdir(VENV):
        raise Exception("Venv absent")

def check_venv_python():
    python = f"{VENV}/bin/python3"
    if not os.path.exists(python):
        raise Exception("python3 manquant dans le venv")

def check_insightface():
    python = f"{VENV}/bin/python3"
    code = "import insightface"
    result = subprocess.run([python, "-c", code], capture_output=True)
    if result.returncode != 0:
        raise Exception("InsightFace non importable")

def check_daemon_running():
    result = subprocess.run(["systemctl", "is-active", "linux-hello.service"], capture_output=True)
    if result.stdout.strip() != b"active":
        raise Exception("Daemon non actif")

def check_socket():
    if not os.path.exists(SOCKET_PATH):
        raise Exception("Socket absent")
    if not stat.S_ISSOCK(os.stat(SOCKET_PATH).st_mode):
        raise Exception("Le fichier existe mais n'est pas un socket")

def check_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Caméra inaccessible")
    cap.release()

def check_faces_dir():
    if not os.path.isdir(FACES_DIR):
        raise Exception("Dossier faces absent")
    if not os.listdir(FACES_DIR):
        raise Exception("Aucun visage enregistré")

def main():
    print("=== Linux Hello Doctor ===")

    check("Venv présent", check_venv_exists)
    check("Python du venv présent", check_venv_python)
    check("InsightFace importable", check_insightface)
    check("Daemon actif", check_daemon_running)
    check("Socket Unix présent", check_socket)
    check("Caméra accessible", check_camera)
    check("Visages enregistrés", check_faces_dir)

    print("\nDiagnostic terminé.")

if __name__ == "__main__":
    main()
