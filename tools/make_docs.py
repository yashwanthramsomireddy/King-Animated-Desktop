"""Generates docs/gallery.png, docs/settings.png and docs/demo.gif (offscreen). Run: python tools/make_docs.py"""
import os, sys, math, tempfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["KINGDESKTOP_CONFIG"] = os.path.join(tempfile.mkdtemp(), "config.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF
from king_pets import config as C
from king_pets.sprites import REGISTRY, CATEGORIES
from king_pets import custom  # noqa
from king_pets.render import Ctx
from king_pets.actors import paint_sprite
from king_pets.engine import Engine
from king_pets.ui import SettingsDialog

app = QApplication([])
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
os.makedirs(OUT, exist_ok=True)

# ── gallery ──
CELL, COLS = 132, 9
specs = list(REGISTRY.values())
rows = math.ceil(len(specs) / COLS)
img = QImage(COLS * CELL, rows * CELL + 60, QImage.Format_ARGB32); img.fill(QColor("#12141c"))
p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
p.setPen(QColor("#00ffd0")); f = QFont("Arial", 16); f.setBold(True); p.setFont(f)
p.drawText(QRectF(0, 8, img.width(), 40), Qt.AlignCenter, f"King Animated Desktop - {len(specs)} objects")
for i, s in enumerate(specs):
    cx, cy = (i % COLS) * CELL, (i // COLS) * CELL + 60
    p.save(); p.translate(cx + 8, cy + 6)
    if s.custom and s.kind == "swing": W, H, rope, ang = 130, 130, 70, 0.35
    elif s.kind == "swing": W, H, rope, ang = 100, 100, 0, 0.0
    else: W, H, rope, ang = s.w, s.h, 0, 0.0
    sc = 100 / max(W, H); p.translate((116 - W * sc) / 2, 0); p.scale(sc, sc)
    paint_sprite(p, s, Ctx(t=0.9, W=W, H=H, rope=rope, ang=ang, gait=0.4, shadow=False))
    p.restore()
    p.setPen(QColor("#c8cde0")); p.setFont(QFont("Arial", 8))
    p.drawText(QRectF(cx, cy + 108, CELL, 20), Qt.AlignCenter, s.name)
p.end(); img.save(os.path.join(OUT, "gallery.png"))

# ── settings window ──
cfg = C.sanitize({"pets": {k: {"enabled": True} for k in ("spiderman", "lab_yellow", "cat", "ufo", "penguin", "cricket")}})
eng = Engine(app, cfg)
dlg = SettingsDialog(eng); dlg.show(); app.processEvents()
dlg.list.setCurrentItem(dlg.items["cat"]); app.processEvents()
dlg.grab().save(os.path.join(OUT, "settings.png"))               # pitch-black theme (default)
dlg.tabs.setCurrentIndex(dlg.tabs.count() - 1); app.processEvents()
dlg.grab().save(os.path.join(OUT, "settings_info.png"))
dlg.add_text(dict(text="OPEN", style="neon-box", swing=True, font_size=34)); dlg.add_text(dict(text="Welcome to TeamExyKings!", animation="marquee-left", style="pill", anchor="bottom-center", glow=False))
dlg.text_list.setCurrentRow(0); dlg.tabs.setCurrentIndex(1); app.processEvents()
dlg.grab().save(os.path.join(OUT, "settings_text.png"))
dlg.cfg["texts"] = []; dlg._rebuild_text_list()
dlg.cfg["theme"] = "white"; dlg.retheme(); dlg.tabs.setCurrentIndex(0); app.processEvents()
dlg.list.setCurrentItem(dlg.items["cat"]); app.processEvents()
dlg.grab().save(os.path.join(OUT, "settings_white.png"))
dlg.cfg["theme"] = "pitch-black"; dlg.retheme()

# ── live frame on fake desktop (+ gif) ──
cfg = C.sanitize({"pets": {k: {"enabled": True} for k in ("spiderman", "lab_yellow", "cat", "ufo", "penguin", "bee", "balloon", "snowflake", "cricket", "moon")},
                  "texts": [dict(text="OPEN", style="neon-box", swing=True, font_size=30, anchor="top-left"), dict(text="Hello from King Animated Desktop", animation="marquee-left", style="pill", anchor="bottom-center", glow=False, font_size=20), dict(text="Wave!", animation="wave", anchor="middle-left", font_size=40, glow=False)]})
eng.rebuild(cfg)
frames = []
SW = 1280
SH = int(1280 * eng.actors[0].geo.height() / eng.actors[0].geo.width())
for n in range(90):
    eng.tick()
    if n % 3 == 0:
        fr = QImage(SW, SH, QImage.Format_ARGB32); fr.fill(QColor("#2b5f8f"))
        q = QPainter(fr); q.setRenderHint(QPainter.SmoothPixmapTransform)
        q.fillRect(0, SH - 40, SW, 40, QColor("#1c1c24"))
        k = SW / eng.actors[0].geo.width() if eng.actors else 1
        for w in eng.all_windows():
            wi = QImage(w.size(), QImage.Format_ARGB32); wi.fill(Qt.transparent); w.render(wi)
            q.drawImage(int(w.geometry().x() * k), int(w.geometry().y() * k), wi.scaled(int(wi.width() * k), int(wi.height() * k), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        q.end(); frames.append(fr)
frames[-1].save(os.path.join(OUT, "preview.png"))
try:
    from PIL import Image
    ims = [Image.frombytes("RGBA", (f.width(), f.height()), bytes(f.constBits())).convert("RGB") for f in frames]
    ims = [i.convert("P", palette=Image.ADAPTIVE) for i in ims]
    ims[0].save(os.path.join(OUT, "demo.gif"), save_all=True, append_images=ims[1:], duration=100, loop=0)
except Exception as e:
    print("gif skipped:", e)
print("done")
