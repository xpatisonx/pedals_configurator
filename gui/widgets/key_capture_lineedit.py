from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from config.keycode_map import translate_keys, reverse_translate_keys


class KeyCaptureLineEdit(QLineEdit):
    """
    Pole do przechwytywania kombinacji klawiszy.
    - for_config=True  → zwraca HID stringi (np. CONTROL+ENTER)
    - for_config=False → zwraca Qt/keyboard nazwy (np. CTRL+RETURN)
    """
    def __init__(self, for_config=False):
        super().__init__()
        self.setPlaceholderText("Wciśnij klawisz(e)...")
        self.for_config = for_config

    def keyPressEvent(self, event):
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
            # Translacja GUI → HID i od razu pokazanie HID-owych nazw
            hid_value = translate_keys(combo)
            if isinstance(hid_value, list):
                self.setText("+".join(hid_value))
            else:
                self.setText(str(hid_value))
        else:
            self.setText(combo)

        event.accept()

    def get_parsed_value(self, action_type):
        """
        Zwraca wartość do zapisania.
        Jeśli for_config=True → HID stringi.
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

    def set_value(self, value):
        """
        Ustawia początkową wartość pola.
        - przy for_config=True przetłumaczy HID → GUI
        - value może być listą lub stringiem
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
            # reverse_translate zwraca string lub listę, upewniamy się, że jest tekst
            if isinstance(display_value, list):
                display_value = "+".join(display_value)
            self.setText(display_value)
