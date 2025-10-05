import os
import json

PRESET_DIR = "presets"


def list_presets():
    if not os.path.exists(PRESET_DIR):
        os.makedirs(PRESET_DIR)
    return [f[:-5] for f in os.listdir(PRESET_DIR) if f.endswith(".json")]


def load_preset(name):
    path = os.path.join(PRESET_DIR, f"{name}.json")
    with open(path, "r") as f:
        return json.load(f)


def save_preset(name, config):
    if not os.path.exists(PRESET_DIR):
        os.makedirs(PRESET_DIR)
    path = os.path.join(PRESET_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=4)


def delete_preset(name):
    path = os.path.join(PRESET_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
