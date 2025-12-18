#!/opt/linux-hello/venv/bin/python3

import socket
import sys

SOCKET_PATH = "/var/run/linux-hello.sock"

def send_auth():
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(b"AUTH")
        result = client.recv(1024).decode().strip()
        client.close()
        return result
    except Exception:
        return "ERROR"

def main():
    result = send_auth()

    if result == "OK":
        sys.exit(0)  # PAM_SUCCESS
    elif result in ("FAIL", "NO_FACE", "NO_CAMERA"):
        sys.exit(1)  # PAM_AUTH_ERR
    else:
        # En cas d'erreur daemon, on laisse passer (comme Howdy)
        sys.exit(0)

if __name__ == "__main__":
    main()