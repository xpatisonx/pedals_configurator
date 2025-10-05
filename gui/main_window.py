from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QStatusBar, QSystemTrayIcon, QMenu, QApplication
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
    presetRequested = Signal(str)  # nazwa presetu

class PedalsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pedals Configurator")
        self.setWindowIcon(QIcon("icons/pedals.ico"))
        self.resize(700, 550)

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # --- Status bar ---
        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)
        self.update_status("Brak aktywnego presetu")

        # --- Zakładki ---
        self.config_tab = ConfigTab()
        self.logs_tab = LogsTab(self.load_config, self.save_config)
        self.presets_tab = PresetsTab(self.on_preset_applied, self.config_tab.get_current_config)

        # --- Hotkey bridge ---
        self.bridge = HotkeyBridge()
        self.bridge.presetRequested.connect(self._apply_preset_from_hotkey)

        # --- Hotkey manager ---
        self.hotkey_mgr = DynamicHotkeyManager(self.bridge.presetRequested.emit)
        self.hotkey_mgr.start()
        self.logs_tab.append_log("Globalne hotkeye uruchomione.")

        self.hotkeys_tab = HotkeysTab(self.hotkey_mgr, log_callback=self.logs_tab.append_log)

        # --- Synchronizacja ---
        self.sync_tab = SyncTab(on_after_sync_callback=self.load_config,
                                log_callback=self.logs_tab.append_log)

        self.tabs.addTab(self.config_tab, "⚙️ Konfiguracja")
        self.tabs.addTab(self.presets_tab, "🎛️ Presety")
        self.tabs.addTab(self.hotkeys_tab, "⌨️ Skróty")
        self.tabs.addTab(self.sync_tab, "🔌 Synchronizacja")
        self.tabs.addTab(self.logs_tab, "📟 Logi")

        # --- Serial port ---
        self.serial = SerialReader(port="COM3", baudrate=115200)
        try:
            self.serial.start()
            self.logs_tab.append_log("Połączono z Pico na COM3")
        except Exception as e:
            self.logs_tab.append_log(f"[Błąd seriala]: {e}")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_serial)
        self.timer.start(100)

        # Start
        self.load_config()

        # --- Ikona w zasobniku (tray) ---
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icons/pedals.svg"))  # <- możesz zmienić ikonę
        self.tray_icon.setToolTip("Pedals Configurator")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Menu kontekstowe tray'a
        tray_menu = QMenu()

        show_action = QAction("Pokaż okno", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        exit_action = QAction("Zamknij", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def check_serial(self):
        line = self.serial.get_line()
        if line:
            self.logs_tab.append_log(f"[Pico] {line}")

    def load_config(self):
        from config.config_manager import load_config
        self.current_config = load_config()
        self.config_tab.load_config(self.current_config)
        self.logs_tab.append_log("Wczytano config.json")

    def save_config(self):
        try:
            self.current_config = self.config_tab.get_current_config()
            save_config(self.current_config)  # lokalny zapis

            # auto-sync na Pico
            try:
                path = sync_to_pico()
                self.logs_tab.append_log(f"💾 Zapisano lokalnie i wysłano na Pico → {path}")
            except Exception as e:
                self.logs_tab.append_log(f"⚠️ Lokalnie zapisano, ale błąd przy wysyłce na Pico: {e}")

        except Exception as e:
            self.logs_tab.append_log(f"[Błąd zapisu]: {e}")

    def on_preset_applied(self, config, name):
        from config.config_manager import save_config
        from config.pico_sync import sync_to_pico

        # 1. zaktualizuj GUI
        self.current_config = config
        self.config_tab.load_config(config)

        # 2. zapisz lokalnie
        try:
            save_config(config)
            self.logs_tab.append_log(f"💾 Preset '{name}' załadowany i zapisany lokalnie.")
        except Exception as e:
            self.logs_tab.append_log(f"[Błąd zapisu lokalnego]: {e}")

        # 3. spróbuj wysłać na Pico (autosync)
        try:
            path = sync_to_pico()
            self.logs_tab.append_log(f"🔌 Config wysłany na Pico → {path}")
        except Exception as e:
            self.logs_tab.append_log(f"⚠️ Nie udało się wysłać na Pico: {e}")

        # 4. zsynchronizuj GUI z zakładką Presets
        try:
            self.presets_tab.preset_box.setCurrentText(name)
        except Exception:
            pass

        self.update_status(f"✅ Aktywny preset: {name}")

    def on_hotkey_preset_loaded(self, config, name):
        self.on_preset_applied(config, name)
        self.logs_tab.append_log(f"[Hotkey] Załadowano preset: {name}")

    def _apply_preset_from_hotkey(self, name: str):
        # TO JEST WĄTEK GUI (slot)
        from config.preset_manager import load_preset
        try:
            config = load_preset(name)
            self.on_preset_applied(config, name)  # to już masz
            self.logs_tab.append_log(f"[Skrót] Załadowano preset: {name}")
            # opcjonalnie zsynchronizuj combo w PresetsTab:
            try:
                self.presets_tab.preset_box.setCurrentText(name)
            except Exception:
                pass
        except Exception as e:
            self.logs_tab.append_log(f"[Skrót] Błąd ładowania presetu '{name}': {e}")

    def closeEvent(self, event):
        """Zachowanie przy zamknięciu okna"""
        # Jeśli okno jest aktywne (kliknięty X) – chowamy, nie zamykamy
        if self.isVisible() and not self.isMinimized():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Pedals Configurator",
                "Aplikacja nadal działa w tle (ikonka w zasobniku).",
                QSystemTrayIcon.Information,
                1000
            )
            return

        # Jeśli wywołano 'Zamknij' z traya – kończymy ładnie
        try:
            self.hotkey_mgr.stop()
        except Exception:
            pass
        try:
            self.serial.stop()
        except Exception:
            pass
        self.tray_icon.hide()

        # to faktycznie kończy aplikację
        super().closeEvent(event)

    def update_status(self, text: str):
        self.status_bar.showMessage(text)

    def changeEvent(self, event):
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QSystemTrayIcon

        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "Pedals Configurator",
                    "Aplikacja działa w tle (kliknij ikonę w zasobniku, aby przywrócić)",
                    QSystemTrayIcon.Information,
                    3000
                )
    def show_from_tray(self):
        """Przywróć okno z traya"""
        self.showNormal()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        from PySide6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.Trigger:
            # Kliknięcie LPM
            self.show_from_tray()
