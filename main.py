import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.main_window import PedalsApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/pedals.ico"))
    window = PedalsApp()
    window.show()
    sys.exit(app.exec())
