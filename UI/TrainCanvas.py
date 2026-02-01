from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtSvg import QSvgRenderer
from assets import SVG_RESOURCES

class TrainCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.carriages = []
        self.setMinimumHeight(160)

    def set_data(self, carriages):
        self.carriages = carriages
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#7f8c8d"), 2))
        painter.drawLine(0, 120, self.width(), 120)
        x_pos = 20
        loco_renderer = QSvgRenderer(SVG_RESOURCES["locomotive"].encode())
        loco_renderer.render(painter, QRectF(x_pos, 40, 90, 75))
        x_pos += 85
        for quality, label in self.carriages:
            svg_data = SVG_RESOURCES.get(quality, SVG_RESOURCES["basic"])
            car_renderer = QSvgRenderer(svg_data.encode())
            car_renderer.render(painter, QRectF(x_pos, 50, 75, 65))
            painter.setPen(Qt.black)
            painter.setFont(QFont("Microsoft YaHei", 7))
            painter.drawText(QRect(int(x_pos), 125, 75, 20), Qt.AlignCenter, label[:6])
            x_pos += 70