import json
import os

CONFIG_PATH = "config/config.json"

DEFAULT_CONFIG = [
    ["GP0", "key", "C"],
    ["GP1", "cmb", ["WINDOWS", "TAB"]]
]


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
    os.replace(tmp, CONFIG_PATH)  # atomowy podmian
