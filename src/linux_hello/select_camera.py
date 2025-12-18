import cv2
import json
import os

from .i18n import _

CONFIG_PATH = "/etc/linux-hello/config.json"

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
    print(_("Look at the LED or preview. Press Enter to continue."))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow(f"Camera {index}", frame)
        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()

    confirm = input(_("Use camera %d? (y/N) ") % index)
    return confirm.lower() == "y"

def save_camera(index):
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)

    config["camera_index"] = index

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print(_("✅ Camera %d saved.") % index)

def select_camera():
    cameras = list_cameras()
    if not cameras:
        print(_("No camera detected."))
        return

    for cam in cameras:
        if test_camera(cam):
            save_camera(cam)
            return

    print(_("No camera selected."))
