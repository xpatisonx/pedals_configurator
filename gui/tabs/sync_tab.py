from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from config.pico_sync import sync_to_pico, sync_from_pico


class SyncTab(QWidget):
    """Tab that handles manual synchronization between local config and Pico."""

    def __init__(self, on_after_sync_callback=None, log_callback=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.on_after_sync = on_after_sync_callback
        self.log = log_callback or (lambda txt: None)

        # Upload button
        btn_upload = QPushButton("⬆️ Upload config.json to Pico")
        btn_upload.clicked.connect(self.upload_to_pico)
        self.layout.addWidget(btn_upload)

        # Download button
        btn_download = QPushButton("⬇️ Download config.json from Pico")
        btn_download.clicked.connect(self.download_from_pico)
        self.layout.addWidget(btn_download)

    # ------------------------------------------------------------------

    def upload_to_pico(self):
        """Send local config.json to the connected Pico."""
        try:
            path = sync_to_pico()
            self.log(f"✅ Sent config.json to Pico → {path}")
            if self.on_after_sync:
                self.on_after_sync()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.log(f"[Upload error to Pico]: {e}")

    # ------------------------------------------------------------------

    def download_from_pico(self):
        """Fetch config.json from Pico and save it locally."""
        try:
            path = sync_from_pico()
            self.log(f"📂 Downloaded config.json from Pico → {path}")
            if self.on_after_sync:
                self.on_after_sync()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.log(f"[Download error from Pico]: {e}")
