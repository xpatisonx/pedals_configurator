from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from config.pico_sync import sync_to_pico, sync_from_pico

class SyncTab(QWidget):
    def __init__(self, on_after_sync_callback=None, log_callback=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.on_after_sync = on_after_sync_callback
        self.log = log_callback or (lambda txt: None)

        btn_upload = QPushButton("⬆️ Wyślij config.json na Pico")
        btn_upload.clicked.connect(self.upload_to_pico)
        self.layout.addWidget(btn_upload)

        btn_download = QPushButton("⬇️ Pobierz config.json z Pico")
        btn_download.clicked.connect(self.download_from_pico)
        self.layout.addWidget(btn_download)

    def upload_to_pico(self):
        try:
            path = sync_to_pico()
            self.log(f"✅ Wysłano config.json na Pico → {path}")
            if self.on_after_sync:
                self.on_after_sync()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))
            self.log(f"[Błąd wysyłania do Pico]: {e}")

    def download_from_pico(self):
        try:
            path = sync_from_pico()
            self.log(f"📂 Pobrano config.json z Pico → {path}")
            if self.on_after_sync:
                self.on_after_sync()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))
            self.log(f"[Błąd pobierania z Pico]: {e}")
