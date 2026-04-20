from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget

from config.action_config import (
    CONSUMER_CONTROL_LABELS,
    CONSUMER_CONTROL_OPTIONS,
    normalize_config_entry,
)
from gui.widgets.key_capture_lineedit import KeyCaptureLineEdit


class ActionValueWidget(QWidget):
    """Editor widget that switches between keyboard and consumer-control inputs."""

    def __init__(self):
        super().__init__()
        self.action_type = "key"
        self.pin_name = ""
        self.validation_message = ""

        self.key_edit = KeyCaptureLineEdit(for_config=True)
        self.consumer_box = QComboBox()
        for value, label in CONSUMER_CONTROL_OPTIONS:
            self.consumer_box.addItem(label, value)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.key_edit)
        layout.addWidget(self.consumer_box)
        self.setLayout(layout)

        self.key_edit.textChanged.connect(self._update_validation_state)
        self.consumer_box.currentIndexChanged.connect(self._update_validation_state)
        self.set_action_type(self.action_type)

    def set_pin_name(self, pin_name):
        """Store the current pin name for validation messages."""
        self.pin_name = pin_name
        self._update_validation_state()

    def set_action_type(self, action_type):
        """Switch the visible editor for the selected action type."""
        self.action_type = action_type
        self.key_edit.set_action_type(action_type)
        is_consumer = action_type == "ccc"
        self.key_edit.setVisible(not is_consumer)
        self.consumer_box.setVisible(is_consumer)

        if is_consumer:
            self.consumer_box.setFocus()
        else:
            self.key_edit.setFocus()
        self._update_validation_state()

    def set_value(self, value, action_type):
        """Load an existing value into the right sub-widget."""
        self.set_action_type(action_type)
        if action_type == "ccc":
            normalized = str(value).strip().upper()
            index = self.consumer_box.findData(normalized)
            if index == -1:
                label = CONSUMER_CONTROL_LABELS.get(normalized, normalized.title())
                self.consumer_box.addItem(label, normalized)
                index = self.consumer_box.findData(normalized)
            self.consumer_box.setCurrentIndex(index)
            self._update_validation_state()
            return

        self.key_edit.set_value(value)
        self._update_validation_state()

    def is_valid(self):
        """Return True when the current field value is valid."""
        self._update_validation_state()
        return not self.validation_message

    def _update_validation_state(self):
        """Apply immediate validation feedback to the active editor."""
        try:
            if self.action_type == "ccc":
                value = self.consumer_box.currentData()
            else:
                value = self.key_edit.get_parsed_value(self.action_type)

            normalize_config_entry(
                [self.pin_name or "GP0", self.action_type, value],
                strict=True,
            )
            self.validation_message = ""
        except ValueError as exc:
            self.validation_message = str(exc)

        is_invalid = bool(self.validation_message)
        self.key_edit.setToolTip(self.validation_message)
        self.consumer_box.setToolTip(self.validation_message)

        invalid_style = "border: 1px solid #d9534f;"
        self.key_edit.setStyleSheet(invalid_style if is_invalid and self.action_type != "ccc" else "")
        self.consumer_box.setStyleSheet(invalid_style if is_invalid and self.action_type == "ccc" else "")

    def get_parsed_value(self, action_type, pin_name):
        """Return one normalized action value for saving."""
        self.pin_name = pin_name
        self.action_type = action_type
        self._update_validation_state()
        if self.validation_message:
            raise ValueError(self.validation_message)

        if action_type == "ccc":
            value = self.consumer_box.currentData()
        else:
            value = self.key_edit.get_parsed_value(action_type)

        normalized = normalize_config_entry([pin_name, action_type, value], strict=True)
        return normalized[2]
