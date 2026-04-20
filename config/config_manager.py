import json
import os
from config.action_config import normalize_config

# Path to the main configuration file
CONFIG_PATH = "config/config.json"

# Default configuration used when config.json does not exist
DEFAULT_CONFIG = [
    ["GP0", "key", "C"],
    ["GP1", "cmb", ["GUI", "TAB"]],
]


def load_config():
    """Load configuration from file or return default config if missing."""
    if not os.path.exists(CONFIG_PATH):
        return normalize_config(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return normalize_config(json.load(f))


def save_config(cfg):
    """
    Save configuration to config.json using an atomic write.
    Writes to a temporary file first, then replaces the original.
    """
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    normalized = normalize_config(cfg, strict=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=4)
    os.replace(tmp, CONFIG_PATH)  # atomic replace
