# 🎛️ Pedals Configurator

A desktop application for configuring custom foot pedals based on **Raspberry Pi Pico** running **CircuitPython**.  
It allows you to map pedal GPIO pins to keyboard actions (single keys or key combos), manage presets,  
and send configurations directly to the Pico as `config.json`.

Built with **Python + PySide6 (Qt)** and sprinkled with sarcasm and too much love for automation.

---

## 🚀 Features

- 🦶 **Pedal Configuration GUI**  
  Assign key actions to individual Pico GPIO pins with a simple interface.

- 🎚️ **Presets System**  
  Save, load, and manage pedal profiles.  
  Auto-save and auto-sync with Pico’s `config.json`.

- ⌨️ **Global Hotkeys**  
  Switch presets on the fly using system-wide keyboard shortcuts.

- 🔌 **Pico Integration**  
  Automatically detects your connected `CIRCUITPY` drive and syncs the configuration file.

- 🪟 **System Tray Support**  
  Runs quietly in the background. Minimize to tray, right-click to show, save, or quit.

---

## 🧰 Tech Stack

| Component | Purpose |
|------------|----------|
| **PySide6 (Qt)** | GUI & Tray |
| **psutil** | Detecting CIRCUITPY drive |
| **keyboard** | Global hotkeys |
| **pyserial** | Reading data from Pico serial port |
| **Pillow** | Icon generation (optional) |
| **darkdetect** | Theme-based icon switching (optional) |

---

## 🪄 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/pedals-configurator.git
cd pedals-configurator
pip install -r requirements.txt
```
Run the application:

```bash
python main.py
```

## ⚙️ Configuration Files

| File                     | Purpose                          |
| ------------------------ | -------------------------------- |
| `config/config.json`     | Main pedal mapping configuration |
| `config/hotkeys.json`    | Global hotkey → preset bindings  |
| `presets/*.json`         | User-defined pedal profiles      |
| `icons/pedals.ico`       | The mighty rainbow pedal icon    |

## 💾 Syncing with Pico

When a CIRCUITPY device is connected:

- The app detects it automatically,
- Saves config.json directly to the Pico drive,
- CircuitPython loads it on startup.

Manual sync available under the 🔌 "Sync" tab.

## 🧱 Build an executable (Windows)
You can create a standalone .exe file using PyInstaller:

```bash
pyinstaller --onefile --noconsole --icon=icons/pedals_turbo.ico main.py
```
The generated .exe will include the custom icon and run without a console window.

## 🧑‍💻 Development Notes
- Works best on Windows 10/11 (tested).
- Run as Administrator if global hotkeys don’t register.
- for Pico → CircuitPython firmware: https://circuitpython.org/board/raspberry_pi_pico/

## 📸 Screenshots
(TBD)

## 👨‍💼 Author
Built by Bartosz Połok

because sometimes hands are not enough.

> “It’s not automation until you can trigger it with your foot.”
>
>— Someone who definitely had too many pedals connected

## 📜 License
MIT License – do whatever you want, but don’t blame me if your foot triggers a system shutdown.