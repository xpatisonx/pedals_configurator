import os
import json

# Directory where all preset JSON files are stored
PRESET_DIR = "presets"


def list_presets():
    """
    Return a list of available preset names (without .json extension).
    Creates the presets directory if it doesn't exist.
    """
    if not os.path.exists(PRESET_DIR):
        os.makedirs(PRESET_DIR)
    return [f[:-5] for f in os.listdir(PRESET_DIR) if f.endswith(".json")]


def load_preset(name):
    """
    Load a preset by name and return its configuration data.
    """
    path = os.path.join(PRESET_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_preset(name, config):
    """
    Save the given configuration under the specified preset name.
    Creates the presets directory if needed.
    """
    if not os.path.exists(PRESET_DIR):
        os.makedirs(PRESET_DIR)
    path = os.path.join(PRESET_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def delete_preset(name):
    """
    Delete the preset file with the given name if it exists.
    """
    path = os.path.join(PRESET_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
