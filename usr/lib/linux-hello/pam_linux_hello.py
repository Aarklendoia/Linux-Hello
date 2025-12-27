#!/opt/linux-hello/venv/bin/python3

import socket
import sys
import os

SOCKET_PATH = "/run/linux-hello/daemon.sock"

def send_auth(username=None):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        
        # Get username from PAM_USER environment variable or argument
        if username is None:
            username = os.environ.get('PAM_USER')
        if username is None and len(sys.argv) > 1:
            username = sys.argv[1]
        
        # Send AUTH request with username
        if username:
            msg = f"AUTH:{username}".encode()
        else:
            msg = b"AUTH"
        
        client.send(msg)
        result = client.recv(1024).decode().strip()
        client.close()
        return result
    except Exception as e:
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