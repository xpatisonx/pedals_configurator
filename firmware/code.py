import json
import time

import board
import digitalio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

CONFIG_PATH = "/config.json"
POLL_INTERVAL = 0.01
DEBOUNCE_INTERVAL = 0.02


def resolve_pin(pin_name):
    if not hasattr(board, pin_name):
        raise ValueError("Unknown pin: {}".format(pin_name))
    return getattr(board, pin_name)


def resolve_key_value(value):
    if isinstance(value, list):
        result = []
        for item in value:
            result.append(getattr(Keycode, item))
        return result
    return getattr(Keycode, value)


def resolve_consumer_value(value):
    if isinstance(value, str):
        return getattr(ConsumerControlCode, value)
    return int(value)


def normalize_entry(entry):
    if not isinstance(entry, list) or len(entry) != 3:
        raise ValueError("Invalid config entry: {}".format(entry))

    pin_name = entry[0]
    action_type = entry[1]
    raw_value = entry[2]
    pin = resolve_pin(pin_name)

    if action_type == "cmb":
        if not isinstance(raw_value, list):
            raw_value = [raw_value]
        action_value = resolve_key_value(raw_value)
    elif action_type == "key":
        action_value = resolve_key_value(raw_value)
    elif action_type == "ccc":
        action_value = resolve_consumer_value(raw_value)
    else:
        raise ValueError("Unsupported action type: {}".format(action_type))

    return [pin_name, pin, action_type, action_value]


def load_config():
    with open(CONFIG_PATH, "r") as handle:
        raw_config = json.load(handle)

    config = []
    for entry in raw_config:
        try:
            config.append(normalize_entry(entry))
        except Exception:
            pass

    if not config:
        raise RuntimeError("No valid button definitions found in config.json")

    return config


def create_button(pin):
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    return button


def press_keyboard(value, keyboard):
    if isinstance(value, list):
        for key in value:
            keyboard.press(key)
    else:
        keyboard.press(value)


def release_keyboard(value, keyboard):
    if isinstance(value, list):
        keyboard.release_all()
    else:
        keyboard.release(value)


def press_action(entry, keyboard, consumer_control):
    action_type = entry[2]
    value = entry[3]

    if action_type in ("key", "cmb"):
        press_keyboard(value, keyboard)
    elif action_type == "ccc":
        consumer_control.press(value)


def release_action(entry, keyboard, consumer_control):
    action_type = entry[2]
    value = entry[3]

    if action_type in ("key", "cmb"):
        release_keyboard(value, keyboard)
    elif action_type == "ccc":
        consumer_control.release()


def main():
    config = load_config()
    keyboard = Keyboard(usb_hid.devices)
    consumer_control = ConsumerControl(usb_hid.devices)

    buttons = []
    for entry in config:
        buttons.append(create_button(entry[1]))

    pressed = [False] * len(buttons)
    last_change = [0.0] * len(buttons)

    while True:
        now = time.monotonic()
        for index, button in enumerate(buttons):
            is_pressed = not button.value

            if is_pressed != pressed[index]:
                if now - last_change[index] < DEBOUNCE_INTERVAL:
                    continue

                if is_pressed:
                    press_action(config[index], keyboard, consumer_control)
                else:
                    release_action(config[index], keyboard, consumer_control)

                pressed[index] = is_pressed
                last_change[index] = now

        time.sleep(POLL_INTERVAL)


main()
