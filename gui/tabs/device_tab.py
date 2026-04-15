from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QHBoxLayout, QComboBox
)


class DeviceTab(QWidget):
    """Tab that groups device connection, sync actions, and runtime logs."""

    def __init__(
        self,
        on_refresh_ports,
        on_connect_port,
        on_disconnect_port,
        on_upload_config,
        on_download_config,
    ):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("🔌 Device Connection and Logs")
        self.layout.addWidget(self.label)

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

        serial_container = QWidget()
        serial_container.setLayout(serial_layout)
        self.layout.addWidget(serial_container)

        sync_layout = QHBoxLayout()

        upload_btn = QPushButton("⬆️ Upload to Device")
        upload_btn.clicked.connect(on_upload_config)
        sync_layout.addWidget(upload_btn)

        download_btn = QPushButton("⬇️ Download from Device")
        download_btn.clicked.connect(on_download_config)
        sync_layout.addWidget(download_btn)

        sync_container = QWidget()
        sync_container.setLayout(sync_layout)
        self.layout.addWidget(sync_container)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        self.setLayout(self.layout)

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
