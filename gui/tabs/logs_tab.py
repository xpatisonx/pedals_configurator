from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton


class LogsTab(QWidget):
    def __init__(self, on_load_config, on_save_config):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("📟 Logi z Pico:")
        self.layout.addWidget(self.label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(on_load_config)
        self.layout.addWidget(load_btn)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(on_save_config)
        self.layout.addWidget(save_btn)

        self.setLayout(self.layout)

    def append_log(self, text):
        self.log_box.append(text)
