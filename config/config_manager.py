import json
import os

# Path to the main configuration file
CONFIG_PATH = "config/config.json"

# Default configuration used when config.json does not exist
DEFAULT_CONFIG = [
    ["GP0", "key", "C"],
    ["GP1", "cmb", ["WINDOWS", "TAB"]],
]


def load_config():
    """Load configuration from file or return default config if missing."""
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    """
    Save configuration to config.json using an atomic write.
    Writes to a temporary file first, then replaces the original.
    """
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
    os.replace(tmp, CONFIG_PATH)  # atomic replace
