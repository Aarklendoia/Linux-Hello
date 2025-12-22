import cv2
import json
import os

from .i18n import _

CONFIG_PATH = "/var/lib/linux-hello/config.json"

def list_cameras(max_test=10):
    cameras = []
    for i in range(max_test):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
    return cameras

def test_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return False

    print(_("Testing camera %d…") % index)
    
    # Try to read a frame to verify the camera works
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print(_("❌ Camera %d: unable to capture frame.") % index)
        return False
    
    print(_("✅ Camera %d: working.") % index)
    print(_("Resolution: %d x %d") % (frame.shape[1], frame.shape[0]))
    
    confirm = input(_("Use camera %d? (y/N) ") % index)
    # Accept "y", "yes", "o", "oui" (for French users)
    return confirm.lower()[0] in ("y", "o") if confirm else False

def save_camera(index):
    config = {}
    config_dir = os.path.dirname(CONFIG_PATH)
    
    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, mode=0o755, exist_ok=True)
    
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)

    config["camera_index"] = index

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print(_("✅ Camera %d saved.") % index)

def select_camera():
    # Check if running as root/admin
    if os.geteuid() != 0:
        print(_("❌ This command requires administrator privileges."))
        print(_("Please run: sudo hello select-camera"))
        return
    
    cameras = list_cameras()
    if not cameras:
        print(_("No camera detected."))
        return

    for cam in cameras:
        if test_camera(cam):
            save_camera(cam)
            return

    print(_("No camera selected."))
