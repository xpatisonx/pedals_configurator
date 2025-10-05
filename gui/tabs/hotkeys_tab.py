from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QMessageBox
)
from hotkeys.hotkey_manager import DynamicHotkeyManager
from config.preset_manager import list_presets
from gui.widgets.key_capture_lineedit import KeyCaptureLineEdit


class HotkeysTab(QWidget):
    """Tab responsible for managing global hotkeys assigned to presets."""

    def __init__(self, hotkey_mgr: DynamicHotkeyManager, log_callback=None):
        super().__init__()
        self.hotkey_mgr = hotkey_mgr
        self.log = log_callback or (lambda msg: None)
        self.layout = QVBoxLayout()

        self.entries = []
        self.redraw_hotkeys_ui()

        add_btn = QPushButton("➕ Add new hotkey")
        add_btn.clicked.connect(self.add_empty_row)
        self.layout.addWidget(add_btn)

        save_btn = QPushButton("💾 Save hotkeys")
        save_btn.clicked.connect(self.save_hotkeys)
        self.layout.addWidget(save_btn)

        self.setLayout(self.layout)

    # ------------------------------------------------------------------

    def redraw_hotkeys_ui(self):
        """Rebuild the UI list of hotkeys."""
        # Clear existing widgets
        for _, _, _, w in self.entries:
            w.setParent(None)
        self.entries.clear()

        # Recreate all existing hotkey bindings
        for hotkey, preset in self.hotkey_mgr.hotkey_map.items():
            self.add_hotkey_row(hotkey, preset)

    # ------------------------------------------------------------------

    def add_empty_row(self):
        """Add an empty row to create a new hotkey binding."""
        presets = list_presets()
        self.add_hotkey_row("", presets[0] if presets else "")

    # ------------------------------------------------------------------

    def add_hotkey_row(self, hotkey, preset):
        """Add a single editable hotkey row."""
        row = QHBoxLayout()

        # Key combination input
        key_input = KeyCaptureLineEdit()
        key_input.setText(hotkey)
        row.addWidget(key_input)

        # Preset selector
        preset_box = QComboBox()
        preset_box.addItems(list_presets())
        if preset in list_presets():
            preset_box.setCurrentText(preset)
        row.addWidget(preset_box)

        # Remove button
        remove_btn = QPushButton("❌")
        row.addWidget(remove_btn)

        container = QWidget()
        container.setLayout(row)
        self.layout.insertWidget(self.layout.count() - 2, container)

        self.entries.append((key_input, preset_box, remove_btn, container))
        remove_btn.clicked.connect(lambda: self.remove_entry(container))

    # ------------------------------------------------------------------

    def remove_entry(self, widget):
        """Remove a hotkey row."""
        for i, (_, _, _, w) in enumerate(self.entries):
            if w == widget:
                self.entries.pop(i)
                widget.setParent(None)
                break

    # ------------------------------------------------------------------

    def save_hotkeys(self):
        """Save all hotkeys to file and reload the active bindings."""
        new_map = {}
        seen = set()

        for key_input, preset_box, _, _ in self.entries:
            combo = key_input.text().strip().lower()
            preset = preset_box.currentText()

            if not combo:
                self.log("[Hotkeys] Skipped empty entry.")
                continue

            if combo in seen:
                QMessageBox.warning(
                    self,
                    "Duplicate",
                    f"The shortcut '{combo}' is used more than once."
                )
                return
            seen.add(combo)

            new_map[combo] = preset

        self.hotkey_mgr.save_hotkeys(new_map)
        self.hotkey_mgr.reload_hooks()

        self.log("[Hotkeys] Saved and reloaded active shortcuts.")
        QMessageBox.information(
            self,
            "Hotkeys saved",
            "New hotkeys have been saved to hotkeys.json and are active immediately ✅"
        )
