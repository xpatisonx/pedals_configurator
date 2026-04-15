from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QMessageBox, QInputDialog
)

from gui.widgets.key_capture_lineedit import KeyCaptureLineEdit


class ConfigTab(QWidget):
    """Tab responsible for editing pedal configuration for a selected preset."""

    def __init__(
        self,
        on_preset_selected,
        on_save_preset,
        on_load_to_device,
        on_save_and_load,
        on_create_preset,
        on_delete_preset,
    ):
        super().__init__()
        self.on_preset_selected = on_preset_selected
        self.on_save_preset = on_save_preset
        self.on_load_to_device = on_load_to_device
        self.on_save_and_load = on_save_and_load
        self.on_create_preset = on_create_preset
        self.on_delete_preset = on_delete_preset

        self.layout = QVBoxLayout()

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("🎛️ Preset:"))

        self.preset_box = QComboBox()
        self.preset_box.currentTextChanged.connect(self._handle_preset_changed)
        preset_row.addWidget(self.preset_box, 1)

        new_preset_btn = QPushButton("➕ New Preset")
        new_preset_btn.clicked.connect(self.create_preset)
        preset_row.addWidget(new_preset_btn)

        delete_preset_btn = QPushButton("🗑 Delete")
        delete_preset_btn.clicked.connect(self.delete_selected_preset)
        preset_row.addWidget(delete_preset_btn)

        preset_container = QWidget()
        preset_container.setLayout(preset_row)
        self.layout.addWidget(preset_container)

        self.group = QGroupBox("⚙️ Pedal Configuration")
        self.config_layout = QVBoxLayout()
        self.group.setLayout(self.config_layout)
        self.layout.addWidget(self.group)

        actions_row = QHBoxLayout()

        save_btn = QPushButton("💾 Save Preset")
        save_btn.clicked.connect(self.on_save_preset)
        actions_row.addWidget(save_btn)

        load_btn = QPushButton("🔌 Load to Device")
        load_btn.clicked.connect(self.on_load_to_device)
        actions_row.addWidget(load_btn)

        save_and_load_btn = QPushButton("💾🔌 Save and Load")
        save_and_load_btn.clicked.connect(self.on_save_and_load)
        actions_row.addWidget(save_and_load_btn)

        actions_container = QWidget()
        actions_container.setLayout(actions_row)
        self.layout.addWidget(actions_container)

        self.setLayout(self.layout)
        self.input_widgets = []

    # ------------------------------------------------------------------

    def _handle_preset_changed(self, name):
        """Load the selected preset whenever the combobox value changes."""
        if name:
            self.on_preset_selected(name)

    # ------------------------------------------------------------------

    def refresh_presets(self, presets, selected_name=None):
        """Reload the preset list while preserving or selecting a target preset."""
        current_name = selected_name or self.selected_preset_name()
        with QSignalBlocker(self.preset_box):
            self.preset_box.clear()
            self.preset_box.addItems(presets)
            if current_name and current_name in presets:
                self.preset_box.setCurrentText(current_name)
            elif presets:
                self.preset_box.setCurrentIndex(0)

    # ------------------------------------------------------------------

    def selected_preset_name(self):
        """Return the currently selected preset name or None."""
        name = self.preset_box.currentText().strip()
        return name or None

    # ------------------------------------------------------------------

    def clear_preset_selection(self):
        """Clear the preset selection without triggering a reload."""
        with QSignalBlocker(self.preset_box):
            self.preset_box.setCurrentIndex(-1)

    # ------------------------------------------------------------------

    def create_preset(self):
        """Prompt for a new preset name and create it from the current editor state."""
        name, ok = QInputDialog.getText(self, "New preset", "Enter preset name:")
        if ok and name.strip():
            self.on_create_preset(name.strip())

    # ------------------------------------------------------------------

    def delete_selected_preset(self):
        """Ask for confirmation and delete the selected preset."""
        name = self.selected_preset_name()
        if not name:
            QMessageBox.warning(self, "No preset selected", "Select a preset to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Delete preset",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.on_delete_preset(name)

    # ------------------------------------------------------------------

    def load_config(self, config):
        """Load configuration and rebuild the list of pins."""
        for i in reversed(range(self.config_layout.count())):
            item = self.config_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.input_widgets.clear()

        for entry in config:
            self.add_pin_row(entry)

        add_btn = QPushButton("+ Add pin")
        add_btn.clicked.connect(self.handle_add_pin)
        self.config_layout.addWidget(add_btn)

    # ------------------------------------------------------------------

    def get_current_config(self):
        """Return current configuration as a list of [pin, type, value]."""
        new_config = []
        for pin_label, type_box, value_edit, _ in self.input_widgets:
            pin = pin_label.text()
            action_type = type_box.currentText()
            value = value_edit.get_parsed_value(action_type)
            new_config.append([pin, action_type, value])
        return new_config

    # ------------------------------------------------------------------

    def add_pin_row(self, entry=None):
        """Add a single editable pin row to the layout."""
        if entry is None:
            pin_index = len(self.input_widgets)
            entry = [f"GP{pin_index}", "key", "A"]

        pin, action_type, value = entry
        row = QHBoxLayout()

        pin_label = QLabel(pin)
        row.addWidget(pin_label)

        type_box = QComboBox()
        type_box.addItems(["key", "cmb", "ccc"])
        type_box.setCurrentText(action_type)
        row.addWidget(type_box)

        value_edit = KeyCaptureLineEdit(for_config=True)
        value_edit.setText("+".join(value) if isinstance(value, list) else str(value))
        row.addWidget(value_edit)

        remove_btn = QPushButton("❌")
        row.addWidget(remove_btn)

        container = QWidget()
        container.setLayout(row)
        self.config_layout.insertWidget(len(self.input_widgets), container)

        self.input_widgets.append((pin_label, type_box, value_edit, container))
        remove_btn.clicked.connect(lambda: self.remove_pin_row(container))

    # ------------------------------------------------------------------

    def remove_pin_row(self, widget):
        """Remove a selected pin row."""
        for i, (_, _, _, w) in enumerate(self.input_widgets):
            if w == widget:
                self.input_widgets.pop(i)
                widget.setParent(None)
                break

    # ------------------------------------------------------------------

    def handle_add_pin(self):
        """Handle the '+ Add pin' button."""
        max_pins = 26
        if len(self.input_widgets) >= max_pins:
            QMessageBox.warning(
                self,
                "Pin limit reached",
                f"The maximum number of pins is {max_pins}."
            )
            return

        used_pins = {pin_label.text() for pin_label, *_ in self.input_widgets}
        for i in range(max_pins):
            pin_name = f"GP{i}"
            if pin_name not in used_pins:
                self.add_pin_row([pin_name, "key", "A"])
                break
