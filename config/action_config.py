from config.keycode_map import translate_keys

CONSUMER_CONTROL_OPTIONS = [
    ("PLAY_PAUSE", "Play/Pause"),
    ("PLAY", "Play"),
    ("PAUSE", "Pause"),
    ("STOP", "Stop"),
    ("MUTE", "Mute"),
    ("VOLUME_INCREMENT", "Volume Up"),
    ("VOLUME_DECREMENT", "Volume Down"),
    ("SCAN_NEXT_TRACK", "Next Track"),
    ("SCAN_PREVIOUS_TRACK", "Previous Track"),
    ("FAST_FORWARD", "Fast Forward"),
    ("REWIND", "Rewind"),
]

CONSUMER_CONTROL_LABELS = dict(CONSUMER_CONTROL_OPTIONS)
CONSUMER_CONTROL_NAMES = set(CONSUMER_CONTROL_LABELS)


def normalize_consumer_control(value):
    """Normalize one ConsumerControlCode name and validate it."""
    normalized = str(value).strip().upper()
    if normalized not in CONSUMER_CONTROL_NAMES:
        raise ValueError("Unsupported consumer control action: {}".format(value))
    return normalized


def normalize_config_entry(entry, strict=False):
    """
    Normalize one config entry to the canonical shape [pin, type, value].

    In non-strict mode old or slightly inconsistent data is coerced into the
    closest valid representation. In strict mode invalid user input raises.
    """
    if not isinstance(entry, list) or len(entry) != 3:
        raise ValueError("Invalid config entry: {}".format(entry))

    pin = str(entry[0]).strip().upper()
    action_type = str(entry[1]).strip().lower()
    value = entry[2]

    if not pin:
        raise ValueError("Pin name cannot be empty.")

    if action_type == "ccc":
        return [pin, action_type, normalize_consumer_control(value)]

    if value in ("", None, []):
        raise ValueError("Action value cannot be empty.")

    translated = translate_keys(value)

    if action_type == "key":
        if isinstance(translated, list):
            translated = [item for item in translated if item]
            if len(translated) == 1:
                translated = translated[0]
            elif strict:
                raise ValueError("Type 'key' accepts exactly one keyboard key.")
            else:
                return [pin, "cmb", translated]
        if not translated:
            raise ValueError("Type 'key' requires one key.")
        return [pin, action_type, translated]

    if action_type == "cmb":
        if isinstance(translated, str):
            translated = [translated]
        translated = [item for item in translated if item]
        if not translated:
            raise ValueError("Type 'cmb' requires at least one key.")
        if strict and len(translated) < 2:
            raise ValueError("Type 'cmb' requires at least two keys.")
        return [pin, action_type, translated]

    raise ValueError("Unsupported action type: {}".format(action_type))


def normalize_config(config, strict=False):
    """Normalize a whole pedal configuration."""
    return [normalize_config_entry(entry, strict=strict) for entry in config]
