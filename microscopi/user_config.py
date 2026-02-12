import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "microscopi"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_user_config():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_user_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
