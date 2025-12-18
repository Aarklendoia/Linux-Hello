import json
import os

CONFIG_PATH = "/etc/linux-hello/config.json"

DEFAULT_CONFIG = {
    "camera_index": 0,
    "threshold": 0.35,
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()

    # Merge defaults with existing config
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)