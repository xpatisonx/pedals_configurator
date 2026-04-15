from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QHBoxLayout, QComboBox
)


class LogsTab(QWidget):
    """Tab that displays log output from Pico and application events."""

    def __init__(self, on_load_config, on_save_config, on_refresh_ports, on_connect_port, on_disconnect_port):
        super().__init__()
        self.layout = QVBoxLayout()

        # Title label
        self.label = QLabel("📟 Pico Logs:")
        self.layout.addWidget(self.label)

        # Serial controls
        serial_layout = QHBoxLayout()
        self.port_box = QComboBox()
        self.port_box.setPlaceholderText("Select a serial port")
        serial_layout.addWidget(self.port_box)

        refresh_btn = QPushButton("🔄 Refresh Ports")
        refresh_btn.clicked.connect(on_refresh_ports)
        serial_layout.addWidget(refresh_btn)

        connect_btn = QPushButton("🔌 Connect")
        connect_btn.clicked.connect(lambda: on_connect_port(self.selected_port()))
        serial_layout.addWidget(connect_btn)

        disconnect_btn = QPushButton("⏹ Disconnect")
        disconnect_btn.clicked.connect(on_disconnect_port)
        serial_layout.addWidget(disconnect_btn)

        self.layout.addLayout(serial_layout)

        # Log output area
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        # Buttons for reloading and saving configuration
        load_btn = QPushButton("🔄 Load Config")
        load_btn.clicked.connect(on_load_config)
        self.layout.addWidget(load_btn)

        save_btn = QPushButton("💾 Save Config")
        save_btn.clicked.connect(on_save_config)
        self.layout.addWidget(save_btn)

        self.setLayout(self.layout)

    # ------------------------------------------------------------------

    def append_log(self, text: str):
        """Append a new line of text to the log display."""
        self.log_box.append(text)

    def selected_port(self):
        """Return the currently selected serial port or None."""
        port = self.port_box.currentText().strip()
        return port or None

    def set_available_ports(self, ports):
        """Refresh the serial port dropdown while preserving selection if possible."""
        current = self.selected_port()
        self.port_box.clear()
        self.port_box.addItems(ports)
        if current and current in ports:
            self.port_box.setCurrentText(current)
