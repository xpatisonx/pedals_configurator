import json, os, threading, time
import keyboard

HOTKEY_CONFIG = "config/hotkeys.json"

class DynamicHotkeyManager:
    def __init__(self, emit_preset_name):
        self.emit_preset_name = emit_preset_name
        self.hotkey_map = {}
        self._handles = []
        self._thread = None
        self._running = False
        self._stop_evt = threading.Event()
        self.load_hotkeys()

    def load_hotkeys(self):
        if os.path.exists(HOTKEY_CONFIG):
            with open(HOTKEY_CONFIG, "r", encoding="utf-8") as f:
                self.hotkey_map = json.load(f)
        else:
            self.hotkey_map = {}

    def save_hotkeys(self, new_map: dict):
        os.makedirs(os.path.dirname(HOTKEY_CONFIG), exist_ok=True)
        with open(HOTKEY_CONFIG, "w", encoding="utf-8") as f:
            json.dump(new_map, f, indent=4)
        self.hotkey_map = new_map
        self.reload_hooks()  # przeładuj w locie

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self._install_only()
        # lekka pętla „keep-alive” dla managera (keyboard ma własny wątek)
        while self._running and not self._stop_evt.wait(0.2):
            pass

    def _install_only(self):
        # UWAGA: nie dotykamy GUI, tylko emitujemy nazwę presetu
        for hk, preset in self.hotkey_map.items():
            handle = keyboard.add_hotkey(hk, lambda p=preset: self.emit_preset_name(p))
            self._handles.append(handle)

    def reload_hooks(self):
        self._unhook_all()
        self._install_only()

    def _unhook_all(self):
        try:
            for h in self._handles:
                keyboard.remove_hotkey(h)
        except Exception:
            pass
        self._handles.clear()

    def stop(self):
        self._running = False
        self._stop_evt.set()
        self._unhook_all()
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
