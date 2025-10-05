import os
import json
import psutil
from config.config_manager import load_config, save_config

CONFIG_FILENAME = "config.json"
VOLUME_LABEL = "CIRCUITPY"


def find_circuitpy_drive():
    """
    Returns the mount point of the CIRCUITPY drive (e.g. 'E:\\') or None if not found.
    """
    for part in psutil.disk_partitions(all=False):
        if VOLUME_LABEL in part.device or VOLUME_LABEL in part.mountpoint:
            return part.mountpoint
        try:
            boot_file = os.path.join(part.mountpoint, "boot_out.txt")
            if os.path.exists(boot_file):
                with open(boot_file, "r", encoding="utf-8", errors="ignore") as f:
                    if "Adafruit CircuitPython" in f.read():
                        return part.mountpoint
        except Exception:
            pass
    return None


def sync_to_pico():
    """
    Copy the local config.json to the connected Pico (CIRCUITPY drive).
    """
    drive = find_circuitpy_drive()
    if not drive:
        raise RuntimeError("No connected Pico (CIRCUITPY) was found.")

    local_cfg = load_config()
    path = os.path.join(drive, CONFIG_FILENAME)
    tmp = path + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(local_cfg, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, path)
    return path


def sync_from_pico():
    """
    Copy config.json from the connected Pico to the local config directory.
    """
    drive = find_circuitpy_drive()
    if not drive:
        raise RuntimeError("No connected Pico (CIRCUITPY) was found.")

    path = os.path.join(drive, CONFIG_FILENAME)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{CONFIG_FILENAME}' not found on Pico.")

    with open(path, "r", encoding="utf-8") as f:
        pico_cfg = json.load(f)

    save_config(pico_cfg)
    return path
