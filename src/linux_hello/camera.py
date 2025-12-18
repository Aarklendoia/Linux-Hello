import cv2
from .config import load_config

def open_camera(index=None):
    config = load_config()
    if index is None:
        index = config.get("camera_index", 0)

    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return None

    return cap