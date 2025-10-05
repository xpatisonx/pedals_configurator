from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from config.keycode_map import translate_keys, reverse_translate_keys


class KeyCaptureLineEdit(QLineEdit):
    """
    A custom input field for capturing keyboard combinations.
    - for_config=True  → returns HID strings (e.g. CONTROL+ENTER)
    - for_config=False → returns Qt/keyboard names (e.g. CTRL+RETURN)
    """

    def __init__(self, for_config=False):
        super().__init__()
        self.setPlaceholderText("Press key(s)...")
        self.for_config = for_config

    # ------------------------------------------------------------------

    def keyPressEvent(self, event):
        """Capture pressed key(s) and display the combination."""
        key = event.key()
        modifiers = event.modifiers()

        parts = []

        if modifiers & Qt.ControlModifier:
            parts.append("CTRL")
        if modifiers & Qt.ShiftModifier:
            parts.append("SHIFT")
        if modifiers & Qt.AltModifier:
            parts.append("ALT")
        if modifiers & Qt.MetaModifier:
            parts.append("META")

        key_name = Qt.Key(key).name.replace("Key_", "")
        if key_name not in ["CTRL", "SHIFT", "ALT", "META"]:
            parts.append(key_name.upper())

        combo = "+".join(parts)

        if self.for_config:
            # Translate GUI → HID and immediately display HID names
            hid_value = translate_keys(combo)
            if isinstance(hid_value, list):
                self.setText("+".join(hid_value))
            else:
                self.setText(str(hid_value))
        else:
            self.setText(combo)

        event.accept()

    # ------------------------------------------------------------------

    def get_parsed_value(self, action_type):
        """
        Return the field value ready to be saved.
        If for_config=True → translates to HID strings.
        """
        text = self.text().strip()

        if not text:
            return ""

        if action_type == "cmb":
            value = [k.strip().upper() for k in text.split("+")]
        else:
            value = text.upper()

        if self.for_config:
            return translate_keys(value)
        return value

    # ------------------------------------------------------------------

    def set_value(self, value):
        """
        Set the initial field value.
        - with for_config=True it translates HID → GUI
        - value may be a list or a single string
        """
        if not value:
            self.setText("")
            return

        if isinstance(value, list):
            display_parts = (
                reverse_translate_keys(value)
                if self.for_config else
                [str(v).upper() for v in value]
            )
            self.setText("+".join(display_parts))
        else:
            display_value = (
                reverse_translate_keys(value)
                if self.for_config else
                str(value).upper()
            )
            # reverse_translate may return a list; ensure it's a string
            if isinstance(display_value, list):
                display_value = "+".join(display_value)
            self.setText(display_value)
