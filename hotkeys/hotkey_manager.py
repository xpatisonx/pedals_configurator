import json
import os
import threading
import time
import keyboard

HOTKEY_CONFIG = "config/hotkeys.json"


class DynamicHotkeyManager:
    """
    Manages global hotkeys that trigger preset changes.
    Uses the 'keyboard' library for system-wide key hooks.
    """

    def __init__(self, emit_preset_name):
        """
        :param emit_preset_name: a callable (signal emitter)
                                 that receives the preset name to load.
        """
        self.emit_preset_name = emit_preset_name
        self.hotkey_map = {}
        self._handles = []
        self._thread = None
        self._running = False
        self._stop_evt = threading.Event()
        self.load_hotkeys()

    # ------------------------------------------------------------------

    def load_hotkeys(self):
        """Load all saved hotkeys from the configuration file."""
        if os.path.exists(HOTKEY_CONFIG):
            with open(HOTKEY_CONFIG, "r", encoding="utf-8") as f:
                self.hotkey_map = json.load(f)
        else:
            self.hotkey_map = {}

    # ------------------------------------------------------------------

    def save_hotkeys(self, new_map: dict):
        """Save new hotkey mappings to file and reload them immediately."""
        os.makedirs(os.path.dirname(HOTKEY_CONFIG), exist_ok=True)
        with open(HOTKEY_CONFIG, "w", encoding="utf-8") as f:
            json.dump(new_map, f, indent=4)
        self.hotkey_map = new_map
        self.reload_hooks()  # reload live

    # ------------------------------------------------------------------

    def start(self):
        """Start listening for hotkeys in a background thread."""
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------

    def _run(self):
        """Main loop: installs hotkeys and keeps the manager alive."""
        self._install_only()
        # Keep-alive loop for the manager (keyboard has its own thread)
        while self._running and not self._stop_evt.wait(0.2):
            pass

    # ------------------------------------------------------------------

    def _install_only(self):
        """
        Install all hotkeys from the current map.
        WARNING: must not interact with GUI — only emit preset names.
        """
        for hk, preset in self.hotkey_map.items():
            handle = keyboard.add_hotkey(hk, lambda p=preset: self.emit_preset_name(p))
            self._handles.append(handle)

    # ------------------------------------------------------------------

    def reload_hooks(self):
        """Reinstall all active hotkeys."""
        self._unhook_all()
        self._install_only()

    # ------------------------------------------------------------------

    def _unhook_all(self):
        """Remove all existing hotkey hooks."""
        try:
            for h in self._handles:
                keyboard.remove_hotkey(h)
        except Exception:
            pass
        self._handles.clear()

    # ------------------------------------------------------------------

    def stop(self):
        """Stop the hotkey manager and clear all hooks."""
        self._running = False
        self._stop_evt.set()
        self._unhook_all()
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
