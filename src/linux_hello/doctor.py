import os
import subprocess
import sys
import socket
import cv2
import stat

from .i18n import _

VENV = "/opt/linux-hello/venv"
SOCKET_PATH = "/var/run/linux-hello.sock"
FACES_DIR = "/var/lib/linux-hello/faces"

def check(title, func):
    print(f"→ {title}… ", end="")
    try:
        func()
        print(_("OK"))
    except Exception as e:
        print(_("FAIL"))
        print(f"   {e}")

def check_venv_exists():
    if not os.path.isdir(VENV):
        raise Exception(_("Venv missing"))

def check_venv_python():
    python = f"{VENV}/bin/python3"
    if not os.path.exists(python):
        raise Exception(_("python3 missing from venv"))

def check_insightface():
    python = f"{VENV}/bin/python3"
    code = "import insightface"
    result = subprocess.run([python, "-c", code], capture_output=True)
    if result.returncode != 0:
        raise Exception(_("InsightFace not importable"))

def check_daemon_running():
    result = subprocess.run(["systemctl", "is-active", "linux-hello.service"], capture_output=True)
    if result.stdout.strip() != b"active":
        raise Exception(_("Daemon not active"))

def check_socket():
    if not os.path.exists(SOCKET_PATH):
        raise Exception(_("Socket missing"))
    if not stat.S_ISSOCK(os.stat(SOCKET_PATH).st_mode):
        raise Exception(_("File exists but is not a socket"))

def check_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception(_("Camera inaccessible"))
    cap.release()

def check_faces_dir():
    if not os.path.isdir(FACES_DIR):
        raise Exception(_("Faces directory missing"))
    if not os.listdir(FACES_DIR):
        raise Exception(_("No registered faces"))

def main():
    print(_("=== Linux Hello Doctor ==="))

    check(_("Venv present"), check_venv_exists)
    check(_("Python in venv present"), check_venv_python)
    check(_("InsightFace importable"), check_insightface)
    check(_("Daemon active"), check_daemon_running)
    check(_("Unix socket present"), check_socket)
    check(_("Camera accessible"), check_camera)
    check(_("Registered faces"), check_faces_dir)

    print(f"\n{_('Diagnosis complete.')}")

if __name__ == "__main__":
    main()


