import os
import json
import psutil
from config.config_manager import load_config, save_config

CONFIG_FILENAME = "config.json"
VOLUME_LABEL = "CIRCUITPY"

def find_circuitpy_drive():
    """
    Zwraca mountpoint CIRCUITPY (np. 'E:\\') albo None.
    """
    for part in psutil.disk_partitions(all=False):
        if VOLUME_LABEL in part.device or VOLUME_LABEL in part.mountpoint:
            return part.mountpoint
        try:
            if os.path.exists(os.path.join(part.mountpoint, "boot_out.txt")):
                with open(os.path.join(part.mountpoint, "boot_out.txt"), "r", encoding="utf-8", errors="ignore") as f:
                    if "Adafruit CircuitPython" in f.read():
                        return part.mountpoint
        except Exception:
            pass
    return None


def sync_to_pico():
    """
    Kopiuje lokalny config.json na Pico.
    """
    drive = find_circuitpy_drive()
    if not drive:
        raise RuntimeError("Nie znaleziono podłączonego Pico (CIRCUITPY).")

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
    Kopiuje config.json z Pico do lokalnego pliku.
    """
    drive = find_circuitpy_drive()
    if not drive:
        raise RuntimeError("Nie znaleziono podłączonego Pico (CIRCUITPY).")

    path = os.path.join(drive, CONFIG_FILENAME)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Brak pliku {CONFIG_FILENAME} na Pico.")

    with open(path, "r", encoding="utf-8") as f:
        pico_cfg = json.load(f)

    save_config(pico_cfg)
    return path
