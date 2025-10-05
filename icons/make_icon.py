from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtWidgets import QApplication
from PIL import Image
import io

app = QApplication([])  # potrzebne dla QPixmap/QSvgRenderer

svg_path = "pedals.svg"
ico_path = "pedals.ico"

sizes = [16, 24, 32, 48, 64, 128, 256]

png_images = []
for s in sizes:
    pixmap = QPixmap(s, s)
    pixmap.fill(Qt.transparent)
    renderer = QSvgRenderer(svg_path)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    pixmap.save(buffer, "PNG")
    png_data = buffer.data()
    buffer.close()

    png_images.append(Image.open(io.BytesIO(png_data)))

png_images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in sizes])
print(f"✅ Ikona zapisana: {ico_path}")
