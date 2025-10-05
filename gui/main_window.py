from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QIcon, QAction
import PySide6.QtSvg

from pico_serial.serial_reader import SerialReader
from hotkeys.hotkey_manager import DynamicHotkeyManager
from config.config_manager import save_config
from config.pico_sync import sync_to_pico, sync_from_pico

from gui.tabs.presets_tab import PresetsTab
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
        self.config_tab = ConfigTab()
        self.logs_tab = LogsTab(self.load_config, self.save_config)
        self.presets_tab = PresetsTab(self.on_preset_applied, self.config_tab.get_current_config)

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
            on_after_sync_callback=self.load_config,
            log_callback=self.logs_tab.append_log
        )

        self.tabs.addTab(self.config_tab, "⚙️ Configuration")
        self.tabs.addTab(self.presets_tab, "🎛️ Presets")
        self.tabs.addTab(self.hotkeys_tab, "⌨️ Hotkeys")
        self.tabs.addTab(self.sync_tab, "🔌 Sync")
        self.tabs.addTab(self.logs_tab, "📟 Logs")

        # --- Serial port ---
        self.serial = SerialReader(port="COM3", baudrate=115200)
        try:
            self.serial.start()
            self.logs_tab.append_log("Connected to Pico on COM3.")
        except Exception as e:
            self.logs_tab.append_log(f"[Serial error]: {e}")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_serial)
        self.timer.start(100)

        # --- Initial load ---
        self.load_config()

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
        line = self.serial.get_line()
        if line:
            self.logs_tab.append_log(f"[Pico] {line}")

    def load_config(self):
        """Load configuration from local config.json."""
        from config.config_manager import load_config
        self.current_config = load_config()
        self.config_tab.load_config(self.current_config)
        self.logs_tab.append_log("Loaded config.json")

    def save_config(self):
        """Save current configuration and try syncing to Pico."""
        try:
            self.current_config = self.config_tab.get_current_config()
            save_config(self.current_config)

            # auto-sync to Pico
            try:
                path = sync_to_pico()
                self.logs_tab.append_log(f"💾 Saved locally and sent to Pico → {path}")
            except Exception as e:
                self.logs_tab.append_log(f"⚠️ Saved locally, but failed to sync to Pico: {e}")

        except Exception as e:
            self.logs_tab.append_log(f"[Save error]: {e}")

    def on_preset_applied(self, config, name):
        """Apply preset, save locally, and sync to Pico."""
        from config.config_manager import save_config
        from config.pico_sync import sync_to_pico

        self.current_config = config
        self.config_tab.load_config(config)

        try:
            save_config(config)
            self.logs_tab.append_log(f"💾 Preset '{name}' applied and saved locally.")
        except Exception as e:
            self.logs_tab.append_log(f"[Local save error]: {e}")

        try:
            path = sync_to_pico()
            self.logs_tab.append_log(f"🔌 Config sent to Pico → {path}")
        except Exception as e:
            self.logs_tab.append_log(f"⚠️ Failed to send to Pico: {e}")

        try:
            self.presets_tab.preset_box.setCurrentText(name)
        except Exception:
            pass

        self.update_status(f"✅ Active preset: {name}")

    def on_hotkey_preset_loaded(self, config, name):
        """Triggered when a preset is loaded via global hotkey."""
        self.on_preset_applied(config, name)
        self.logs_tab.append_log(f"[Hotkey] Loaded preset: {name}")

    def _apply_preset_from_hotkey(self, name: str):
        """Slot called from background thread via signal."""
        from config.preset_manager import load_preset
        try:
            config = load_preset(name)
            self.on_preset_applied(config, name)
            self.logs_tab.append_log(f"[Shortcut] Loaded preset: {name}")
            try:
                self.presets_tab.preset_box.setCurrentText(name)
            except Exception:
                pass
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
