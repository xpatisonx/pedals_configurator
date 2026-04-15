from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QIcon, QAction
import PySide6.QtSvg

from pico_serial.serial_reader import SerialReader
from hotkeys.hotkey_manager import DynamicHotkeyManager
from config.config_manager import save_config, load_config
from config.pico_sync import sync_to_pico
from config.preset_manager import list_presets, load_preset, save_preset, delete_preset

from gui.tabs.logs_tab import LogsTab
from gui.tabs.config_tab import ConfigTab
from gui.tabs.hotkeys_tab import HotkeysTab
from gui.tabs.sync_tab import SyncTab


class HotkeyBridge(QObject):
    """Bridge object used to emit preset change requests from hotkey threads."""
    presetRequested = Signal(str)


class PedalsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pedals Configurator")
        self.setWindowIcon(QIcon("icons/pedals.ico"))
        self.resize(700, 550)

        # --- Main layout and tabs ---
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # --- Status bar ---
        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)
        self.update_status("No active preset")

        # --- Tabs ---
        self.current_preset_name = None
        self.current_config = []
        self.config_tab = ConfigTab(
            self.select_preset,
            self.save_selected_preset,
            self.load_current_config_to_device,
            self.save_and_load_selected_preset,
            self.create_preset,
            self.delete_selected_preset,
        )
        self.serial = SerialReader(baudrate=115200)
        self.logs_tab = LogsTab(
            self.load_config,
            self.save_config,
            self.refresh_serial_ports,
            self.connect_serial,
            self.disconnect_serial
        )

        # --- Hotkey bridge (thread-safe signal emitter) ---
        self.bridge = HotkeyBridge()
        self.bridge.presetRequested.connect(self._apply_preset_from_hotkey)

        # --- Hotkey manager ---
        self.hotkey_mgr = DynamicHotkeyManager(self.bridge.presetRequested.emit)
        self.hotkey_mgr.start()
        self.logs_tab.append_log("Global hotkeys initialized.")

        self.hotkeys_tab = HotkeysTab(self.hotkey_mgr, log_callback=self.logs_tab.append_log)

        # --- Sync tab (local ↔ Pico) ---
        self.sync_tab = SyncTab(
            on_after_sync_callback=self.load_config_from_file,
            log_callback=self.logs_tab.append_log
        )

        self.tabs.addTab(self.config_tab, "⚙️ Configuration")
        self.tabs.addTab(self.hotkeys_tab, "⌨️ Hotkeys")
        self.tabs.addTab(self.sync_tab, "🔌 Sync")
        self.tabs.addTab(self.logs_tab, "📟 Logs")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_serial)
        self.timer.start(100)

        self.refresh_serial_ports()
        self.logs_tab.append_log("Select a serial port and click Connect to start reading Pico logs.")

        # --- Initial load ---
        self.load_initial_editor_state()

        # --- System tray icon ---
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icons/pedals.ico"))
        self.tray_icon.setToolTip("Pedals Configurator")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Context menu for tray icon
        tray_menu = QMenu()

        show_action = QAction("Show window", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # ---------------------------------------------------------------------

    def check_serial(self):
        """Check if Pico has sent any data and display it in logs."""
        if not self.serial.is_connected():
            return
        line = self.serial.get_line()
        if line:
            self.logs_tab.append_log(f"[Pico] {line}")

    def refresh_serial_ports(self):
        """Detect serial ports and refresh the dropdown in the logs tab."""
        ports = self.serial.list_available_ports()
        self.logs_tab.set_available_ports(ports)
        if ports:
            self.logs_tab.append_log(f"Detected serial ports: {', '.join(ports)}")
        else:
            self.logs_tab.append_log("No active serial ports detected.")

    def connect_serial(self, port):
        """Connect to the selected serial port."""
        if not port:
            self.logs_tab.append_log("Select a serial port before connecting.")
            return

        if self.serial.is_connected():
            if self.serial.port == port:
                self.logs_tab.append_log(f"Already connected to {port}.")
                return
            self.disconnect_serial()

        try:
            self.serial.start(port=port)
            self.logs_tab.append_log(f"Connected to Pico on {port}.")
        except Exception as e:
            self.logs_tab.append_log(f"[Serial connect error]: {e}")

    def disconnect_serial(self):
        """Disconnect from the current serial port if connected."""
        if not self.serial.is_connected():
            self.logs_tab.append_log("Serial port is not connected.")
            return

        port = self.serial.port
        try:
            self.serial.stop()
            self.logs_tab.append_log(f"Disconnected from {port}.")
        except Exception as e:
            self.logs_tab.append_log(f"[Serial disconnect error]: {e}")

    def load_initial_editor_state(self):
        """Load the first preset into the editor or fall back to config.json."""
        presets = list_presets()
        self.config_tab.refresh_presets(presets)

        if presets:
            self.select_preset(presets[0], update_selector=False)
        else:
            self.current_preset_name = None
            self.current_config = load_config()
            self.config_tab.load_config(self.current_config)
            self.logs_tab.append_log("Loaded config.json")
            self.update_status("No preset selected")

    def load_config(self):
        """Reload the editor from the selected preset or local config fallback."""
        if self.current_preset_name:
            self.select_preset(self.current_preset_name)
            return

        self.current_config = load_config()
        self.config_tab.load_config(self.current_config)
        self.logs_tab.append_log("Loaded config.json")

    def load_config_from_file(self):
        """Load config.json into the editor as a standalone working state."""
        self.current_preset_name = None
        self.current_config = load_config()
        self.config_tab.refresh_presets(list_presets())
        self.config_tab.clear_preset_selection()
        self.config_tab.load_config(self.current_config)
        self.logs_tab.append_log("Loaded config.json into the editor.")
        self.update_status("Editing local config.json")

    def save_config(self):
        """Save the current editor state to config.json without syncing."""
        try:
            self.current_config = self.config_tab.get_current_config()
            save_config(self.current_config)
            self.logs_tab.append_log("💾 Saved current editor state to config.json")
        except Exception as e:
            self.logs_tab.append_log(f"[Save error]: {e}")

    def select_preset(self, name, update_selector=True):
        """Load a preset into the editor."""
        if not name:
            return
        try:
            config = load_preset(name)
            self.current_preset_name = name
            self.current_config = config
            self.config_tab.load_config(config)
            if update_selector:
                self.config_tab.refresh_presets(list_presets(), selected_name=name)
            save_config(config)
            self.logs_tab.append_log(f"Loaded preset '{name}' into the editor.")
            self.update_status(f"✅ Active preset: {name}")
        except Exception as e:
            self.logs_tab.append_log(f"[Preset load error]: {e}")

    def save_selected_preset(self):
        """Save the current editor state to the selected preset."""
        name = self.config_tab.selected_preset_name()
        if not name:
            self.logs_tab.append_log("Select a preset before saving.")
            return
        try:
            config = self.config_tab.get_current_config()
            save_preset(name, config)
            save_config(config)
            self.current_preset_name = name
            self.current_config = config
            self.config_tab.refresh_presets(list_presets(), selected_name=name)
            self.hotkeys_tab.redraw_hotkeys_ui()
            self.logs_tab.append_log(f"💾 Saved preset '{name}'.")
            self.update_status(f"✅ Active preset: {name}")
        except Exception as e:
            self.logs_tab.append_log(f"[Preset save error]: {e}")

    def load_current_config_to_device(self):
        """Send the current editor state to the Pico without changing preset files."""
        try:
            config = self.config_tab.get_current_config()
            save_config(config)
            self.current_config = config
            path = sync_to_pico()
            self.logs_tab.append_log(f"🔌 Loaded current editor state to Pico → {path}")
        except Exception as e:
            self.logs_tab.append_log(f"[Device sync error]: {e}")

    def save_and_load_selected_preset(self):
        """Save the selected preset and immediately send it to the Pico."""
        name = self.config_tab.selected_preset_name()
        if not name:
            self.logs_tab.append_log("Select a preset before saving and loading.")
            return
        try:
            config = self.config_tab.get_current_config()
            save_preset(name, config)
            save_config(config)
            self.current_preset_name = name
            self.current_config = config
            self.config_tab.refresh_presets(list_presets(), selected_name=name)
            self.hotkeys_tab.redraw_hotkeys_ui()
            path = sync_to_pico()
            self.logs_tab.append_log(f"💾🔌 Saved preset '{name}' and loaded it to Pico → {path}")
            self.update_status(f"✅ Active preset: {name}")
        except Exception as e:
            self.logs_tab.append_log(f"[Save and load error]: {e}")

    def create_preset(self, name):
        """Create a new preset from the current editor state."""
        if name in list_presets():
            self.logs_tab.append_log(f"Preset '{name}' already exists.")
            return
        try:
            config = self.config_tab.get_current_config() if self.config_tab.input_widgets else load_config()
            save_preset(name, config)
            self.current_preset_name = name
            self.current_config = config
            self.config_tab.refresh_presets(list_presets(), selected_name=name)
            self.hotkeys_tab.redraw_hotkeys_ui()
            self.logs_tab.append_log(f"Created preset '{name}'.")
            self.update_status(f"✅ Active preset: {name}")
        except Exception as e:
            self.logs_tab.append_log(f"[Preset create error]: {e}")

    def delete_selected_preset(self, name):
        """Delete a preset and load the next available editor state."""
        try:
            delete_preset(name)
            presets = list_presets()
            self.config_tab.refresh_presets(presets)
            self.hotkeys_tab.redraw_hotkeys_ui()
            self.logs_tab.append_log(f"Deleted preset '{name}'.")

            if presets:
                self.select_preset(presets[0], update_selector=False)
            else:
                self.current_preset_name = None
                self.current_config = load_config()
                self.config_tab.load_config(self.current_config)
                self.update_status("No preset selected")
        except Exception as e:
            self.logs_tab.append_log(f"[Preset delete error]: {e}")

    def _apply_preset_from_hotkey(self, name: str):
        """Slot called from background thread via signal."""
        try:
            self.select_preset(name)
            self.logs_tab.append_log(f"[Shortcut] Loaded preset: {name}")
        except Exception as e:
            self.logs_tab.append_log(f"[Shortcut] Failed to load preset '{name}': {e}")

    # ---------------------------------------------------------------------

    def closeEvent(self, event):
        """Handle window close event: hide or exit cleanly."""
        from PySide6.QtWidgets import QSystemTrayIcon

        # If user clicked window "X" → hide to tray instead of closing
        if self.isVisible() and not self.isMinimized():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Pedals Configurator",
                "The app is still running in the background (check the system tray).",
                QSystemTrayIcon.Information,
                1000
            )
            return

        # If closed from tray → stop services and exit
        try:
            self.hotkey_mgr.stop()
        except Exception:
            pass
        try:
            self.serial.stop()
        except Exception:
            pass
        self.tray_icon.hide()
        super().closeEvent(event)

    def update_status(self, text: str):
        """Update status bar message."""
        self.status_bar.showMessage(text)

    def changeEvent(self, event):
        """Hide to tray when minimized."""
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QSystemTrayIcon

        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "Pedals Configurator",
                    "App is running in the background (click the tray icon to restore).",
                    QSystemTrayIcon.Information,
                    3000
                )

    def show_from_tray(self):
        """Restore window from tray."""
        self.showNormal()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon click (left-click restores window)."""
        from PySide6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.Trigger:
            self.show_from_tray()
