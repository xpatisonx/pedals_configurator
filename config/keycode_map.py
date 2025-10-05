# GUI name (Qt/keyboard) → HID name (adafruit_hid.keycode)
GUI_TO_HID = {
    # Modifiers
    "CTRL": "CONTROL",
    "CONTROL": "CONTROL",
    "SHIFT": "SHIFT",
    "ALT": "ALT",
    "META": "GUI",      # Windows / Command key

    # Letters
    **{chr(i): chr(i) for i in range(ord("A"), ord("Z") + 1)},

    # Number keys (top row)
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",

    # Common keys
    "RETURN": "ENTER",
    "ENTER": "ENTER",
    "ESC": "ESCAPE",
    "ESCAPE": "ESCAPE",
    "TAB": "TAB",
    "SPACE": "SPACE",
    "BACKSPACE": "BACKSPACE",
    "DEL": "DELETE",
    "DELETE": "DELETE",
    "INS": "INSERT",
    "INSERT": "INSERT",

    # Arrows
    "UP": "UP_ARROW",
    "DOWN": "DOWN_ARROW",
    "LEFT": "LEFT_ARROW",
    "RIGHT": "RIGHT_ARROW",

    # Page / Home / End
    "PAGEUP": "PAGE_UP",
    "PAGEDOWN": "PAGE_DOWN",
    "HOME": "HOME",
    "END": "END",

    # Function keys
    **{f"F{i}": f"F{i}" for i in range(1, 25)},

    # Punctuation / main symbols
    "-": "MINUS",
    "=": "EQUALS",
    "[": "LEFT_BRACKET",
    "]": "RIGHT_BRACKET",
    "\\": "BACKSLASH",
    ";": "SEMICOLON",
    "'": "QUOTE",
    "`": "GRAVE_ACCENT",
    ",": "COMMA",
    ".": "PERIOD",
    "/": "FORWARD_SLASH",

    # Numeric keypad (optional — Pico may use these HID KEYPAD_* names)
    "NUMLOCK": "KEYPAD_NUMLOCK",
    "NUMPAD0": "KEYPAD_ZERO",
    "NUMPAD1": "KEYPAD_ONE",
    "NUMPAD2": "KEYPAD_TWO",
    "NUMPAD3": "KEYPAD_THREE",
    "NUMPAD4": "KEYPAD_FOUR",
    "NUMPAD5": "KEYPAD_FIVE",
    "NUMPAD6": "KEYPAD_SIX",
    "NUMPAD7": "KEYPAD_SEVEN",
    "NUMPAD8": "KEYPAD_EIGHT",
    "NUMPAD9": "KEYPAD_NINE",
    "NUMPAD.": "KEYPAD_PERIOD",
    "NUMPAD/": "KEYPAD_FORWARD_SLASH",
    "NUMPAD*": "KEYPAD_ASTERISK",
    "NUMPAD-": "KEYPAD_MINUS",
    "NUMPAD+": "KEYPAD_PLUS",
    "NUMPADENTER": "KEYPAD_ENTER",
}

# Reverse mapping HID → GUI
HID_TO_GUI = {v: k for k, v in GUI_TO_HID.items()}

# Aliases for nicer display in GUI
HID_TO_GUI.update({
    "GUI": "META",
    "ENTER": "RETURN",
    "ESCAPE": "ESC",
    "UP_ARROW": "UP",
    "DOWN_ARROW": "DOWN",
    "LEFT_ARROW": "LEFT",
    "RIGHT_ARROW": "RIGHT",
    "PAGE_UP": "PAGEUP",
    "PAGE_DOWN": "PAGEDOWN",
    "DELETE": "DEL",
})


def translate_keys(value):
    """
    Convert GUI-style key names (e.g. 'CTRL+ALT+A')
    to HID key strings used by adafruit_hid.keycode.
    """
    if isinstance(value, str):
        parts = [v.strip().upper() for v in value.split("+")]
        result = [GUI_TO_HID.get(k, k) for k in parts]
        return result if len(result) > 1 else result[0]
    elif isinstance(value, list):
        return [GUI_TO_HID.get(str(k).upper(), str(k).upper()) for k in value]
    else:
        return GUI_TO_HID.get(str(value).upper(), str(value).upper())


def reverse_translate_keys(value):
    """
    Convert HID key strings back to GUI-friendly names
    (e.g. ['CONTROL', 'ALT', 'ENTER'] → ['CTRL', 'ALT', 'RETURN']).
    """
    if isinstance(value, str):
        return HID_TO_GUI.get(value.upper(), value.upper())
    elif isinstance(value, list):
        return [HID_TO_GUI.get(str(k).upper(), str(k).upper()) for k in value]
    else:
        return value
