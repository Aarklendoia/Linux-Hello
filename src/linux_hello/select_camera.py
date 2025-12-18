import cv2
import json
import os

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

    print(f"Test de la caméra {index}…")
    print("Regardez la LED ou l’aperçu. Appuyez sur Entrée pour continuer.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow(f"Caméra {index}", frame)
        if cv2.waitKey(1) == 13:  # Entrée
            break

    cap.release()
    cv2.destroyAllWindows()

    confirm = input(f"Voulez-vous utiliser la caméra {index} ? (o/N) ")
    return confirm.lower() == "o"

def save_camera(index):
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)

    config["camera_index"] = index

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print(f"✅ Caméra {index} enregistrée.")

def select_camera():
    cameras = list_cameras()
    if not cameras:
        print("Aucune caméra détectée.")
        return

    for cam in cameras:
        if test_camera(cam):
            save_camera(cam)
            return

    print("Aucune caméra sélectionnée.")