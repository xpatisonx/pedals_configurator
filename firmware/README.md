# Firmware Package

This directory is a self-contained CircuitPython firmware bundle for the pedal device.

It already includes:

- `code.py`
- `config.json`
- `lib/adafruit_hid/*.mpy`

## How to install

1. Flash CircuitPython onto a Raspberry Pi Pico.
2. Mount the board as `CIRCUITPY`.
3. Copy everything from this directory onto the `CIRCUITPY` drive.
4. Safely eject the drive or wait for CircuitPython to reload.

No extra library downloads are required.

## Included demo mapping

- `GP0` -> `UP_ARROW`
- `GP1` -> `DOWN_ARROW`
- `GP2` -> `GUI + SPACE`
- `GP3` -> `PLAY_PAUSE`
