from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout,
    QPushButton, QInputDialog, QMessageBox
)
from config.preset_manager import list_presets, load_preset, save_preset, delete_preset


class PresetsTab(QWidget):
    """Tab for managing pedal configuration presets."""

    def __init__(self, on_preset_applied_callback, get_current_config_callback):
        super().__init__()
        self.on_preset_applied = on_preset_applied_callback
        self.get_current_config = get_current_config_callback

        self.layout = QVBoxLayout()

        # Preset selector
        self.preset_box = QComboBox()
        self.refresh_presets()
        self.layout.addWidget(QLabel("🎛️ Select preset:"))
        self.layout.addWidget(self.preset_box)

        # Buttons row
        buttons = QHBoxLayout()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_selected)
        buttons.addWidget(apply_btn)

        save_btn = QPushButton("Save as...")
        save_btn.clicked.connect(self.save_as_new)
        buttons.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_selected)
        buttons.addWidget(delete_btn)

        container = QWidget()
        container.setLayout(buttons)
        self.layout.addWidget(container)

        self.setLayout(self.layout)

    # ------------------------------------------------------------------

    def refresh_presets(self):
        """Reload the list of available presets."""
        self.preset_box.clear()
        self.preset_box.addItems(list_presets())

    # ------------------------------------------------------------------

    def apply_selected(self):
        """Load and apply the selected preset."""
        name = self.preset_box.currentText()
        try:
            config = load_preset(name)
            self.on_preset_applied(config, name)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ------------------------------------------------------------------

    def save_as_new(self):
        """Save the current configuration as a new preset."""
        name, ok = QInputDialog.getText(self, "New preset", "Enter preset name:")
        if ok and name:
            try:
                save_preset(name, self.get_current_config())
                self.refresh_presets()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ------------------------------------------------------------------

    def delete_selected(self):
        """Delete the selected preset."""
        name = self.preset_box.currentText()
        confirm = QMessageBox.question(
            self,
            "Delete preset",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            delete_preset(name)
            self.refresh_presets()
