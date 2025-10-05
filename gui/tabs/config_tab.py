from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QComboBox, QPushButton
from gui.widgets.key_capture_lineedit import KeyCaptureLineEdit
from PySide6.QtWidgets import QMessageBox


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.group = QGroupBox("⚙️ Konfiguracja pedałów")
        self.config_layout = QVBoxLayout()
        self.group.setLayout(self.config_layout)
        self.layout.addWidget(self.group)
        self.setLayout(self.layout)

        self.input_widgets = []

    def load_config(self, config):
        # Czyścimy stare
        for i in reversed(range(self.config_layout.count())):
            self.config_layout.itemAt(i).widget().setParent(None)
        self.input_widgets.clear()

        for entry in config:
            self.add_pin_row(entry)

        add_btn = QPushButton("+ Dodaj pin")
        add_btn.clicked.connect(self.handle_add_pin)
        self.config_layout.addWidget(add_btn)

    def get_current_config(self):
        new_config = []
        for pin_label, type_box, value_edit, _ in self.input_widgets:
            pin = pin_label.text()
            action_type = type_box.currentText()
            value = value_edit.get_parsed_value(action_type)
            new_config.append([pin, action_type, value])
        return new_config

    def add_pin_row(self, entry=None):
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

    def remove_pin_row(self, widget):
        for i, (_, _, _, w) in enumerate(self.input_widgets):
            if w == widget:
                self.input_widgets.pop(i)
                widget.setParent(None)
                break

    def handle_add_pin(self):
        max_pins = 26
        if len(self.input_widgets) >= max_pins:
            QMessageBox.warning(self, "Limit pinów", f"Maksymalna liczba pinów to {max_pins}.")
            return

        used_pins = {pin_label.text() for pin_label, *_ in self.input_widgets}
        for i in range(max_pins):
            pin_name = f"GP{i}"
            if pin_name not in used_pins:
                self.add_pin_row([pin_name, "key", "A"])
                break
