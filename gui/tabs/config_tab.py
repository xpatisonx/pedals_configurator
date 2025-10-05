from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QMessageBox
)
from gui.widgets.key_capture_lineedit import KeyCaptureLineEdit


class ConfigTab(QWidget):
    """Tab responsible for editing pedal configuration."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.group = QGroupBox("⚙️ Pedal Configuration")
        self.config_layout = QVBoxLayout()
        self.group.setLayout(self.config_layout)
        self.layout.addWidget(self.group)
        self.setLayout(self.layout)

        self.input_widgets = []

    # ------------------------------------------------------------------

    def load_config(self, config):
        """Load configuration and rebuild the list of pins."""
        # Clear previous widgets
        for i in reversed(range(self.config_layout.count())):
            self.config_layout.itemAt(i).widget().setParent(None)
        self.input_widgets.clear()

        # Recreate all pin rows
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

        # Pin label
        pin_label = QLabel(pin)
        row.addWidget(pin_label)

        # Action type selector
        type_box = QComboBox()
        type_box.addItems(["key", "cmb", "ccc"])
        type_box.setCurrentText(action_type)
        row.addWidget(type_box)

        # Key/value editor
        value_edit = KeyCaptureLineEdit(for_config=True)
        value_edit.setText("+".join(value) if isinstance(value, list) else str(value))
        row.addWidget(value_edit)

        # Remove button
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
