"""Generates assets/king_animated_desktop.ico (needs Pillow)."""
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QRectF
app = QApplication([])
S = 256
img = QImage(S, S, QImage.Format_ARGB32); img.fill(Qt.transparent)
p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
for i, a in ((18, 40), (12, 70), (7, 110)):
    g = QColor("#00ffd0"); g.setAlpha(a); p.setPen(QPen(g, i)); p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRectF(26, 26, S - 52, S - 52), 40, 40)
p.setPen(QPen(QColor("#00ffd0"), 6)); p.setBrush(QColor("#08080c"))
p.drawRoundedRect(QRectF(26, 26, S - 52, S - 52), 40, 40)
f = QFont("Arial", 120); f.setBold(True); p.setFont(f); p.setPen(QColor("#00ffd0"))
p.drawText(QRectF(0, 20, S, S), Qt.AlignCenter, "K")
p.setBrush(QColor("#ffd23c")); p.setPen(Qt.NoPen)                      # little crown
from PySide6.QtGui import QPolygonF
from PySide6.QtCore import QPointF
p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in ((86, 74), (100, 44), (118, 64), (128, 36), (138, 64), (156, 44), (170, 74))]))
p.end()
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img.save(os.path.join(root, "assets", "king_animated_desktop.png"))
from PIL import Image
Image.open(os.path.join(root, "assets", "king_animated_desktop.png")).save(
    os.path.join(root, "assets", "king_animated_desktop.ico"), sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("icon ok")
