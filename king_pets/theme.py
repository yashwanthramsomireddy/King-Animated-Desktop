"""Pitch-black / white / system themes for the settings window, tray menu and dialogs."""
import os, tempfile
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication

PALETTES = {
    "pitch-black": dict(bg="#000000", panel="#0b0b0d", panel2="#16171b", input="#0b0b0d", border="#2a2b32",
                        text="#ececf1", muted="#8b8d98", tile="#12131a"),
    "white": dict(bg="#ffffff", panel="#f4f5f8", panel2="#e9ebf1", input="#ffffff", border="#c9cdd8",
                  text="#14151a", muted="#5d6170", tile="#d9deea"),
}


def resolve(theme):
    if theme == "system":
        try:
            scheme = QApplication.instance().styleHints().colorScheme()
            return "white" if scheme == Qt.ColorScheme.Light else "pitch-black"
        except Exception:
            return "pitch-black"
    return theme if theme in PALETTES else "pitch-black"


def _readable_accent(accent, on_light):
    c = QColor(accent)
    if not c.isValid():
        c = QColor("#00ffd0")
    if on_light:                       # bright neon colours vanish on white: darken until readable
        while c.lightnessF() > 0.38 and c.value() > 30:
            c = c.darker(112)
    return c


def _check_png():
    path = os.path.join(tempfile.gettempdir(), "kingdesktop_check.png")
    if not os.path.exists(path):
        pm = QPixmap(32, 32); pm.fill(Qt.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#ffffff"), 5); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen); p.drawPolyline([__import__("PySide6.QtCore", fromlist=["QPointF"]).QPointF(*pt)
                                       for pt in ((7, 17), (13, 23), (25, 9))])
        p.end(); pm.save(path)
    return path.replace("\\", "/")


def colors(theme, accent):
    name = resolve(theme)
    p = dict(PALETTES[name]); p["name"] = name
    a = _readable_accent(accent, name == "white")
    p["accent"] = a.name()
    p["accent_text"] = "#000000" if a.lightnessF() > 0.55 else "#ffffff"
    p["accent_bg"] = f"rgba({a.red()},{a.green()},{a.blue()},{'46' if name == 'pitch-black' else '38'})"
    return p


def build_qss(c):
    return f"""
QWidget {{ background:{c['bg']}; color:{c['text']}; font-size:13px; }}
QDialog, QScrollArea, QScrollArea > QWidget > QWidget {{ background:{c['bg']}; }}
QLabel {{ background:transparent; }}
QToolTip {{ background:{c['panel']}; color:{c['text']}; border:1px solid {c['accent']}; padding:4px; }}
QTabWidget::pane {{ border:1px solid {c['border']}; background:{c['bg']}; top:-1px; }}
QTabBar::tab {{ background:{c['panel']}; color:{c['muted']}; padding:8px 16px; border:1px solid {c['border']};
  border-bottom:none; margin-right:2px; border-top-left-radius:7px; border-top-right-radius:7px; }}
QTabBar::tab:selected {{ background:{c['bg']}; color:{c['accent']}; border-bottom:2px solid {c['accent']}; }}
QTabBar::tab:hover:!selected {{ color:{c['text']}; }}
QPushButton {{ background:{c['panel2']}; color:{c['text']}; border:1px solid {c['border']};
  border-radius:7px; padding:6px 14px; }}
QPushButton:hover {{ border-color:{c['accent']}; color:{c['accent']}; }}
QPushButton:pressed, QPushButton:default {{ border-color:{c['accent']}; }}
QPushButton:default {{ background:{c['accent']}; color:{c['accent_text']}; font-weight:bold; }}
QPushButton:default:hover {{ color:{c['accent_text']}; }}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{ background:{c['input']}; color:{c['text']};
  border:1px solid {c['border']}; border-radius:6px; padding:4px 8px;
  selection-background-color:{c['accent']}; selection-color:{c['accent_text']}; }}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{ border-color:{c['accent']}; }}
QComboBox QAbstractItemView {{ background:{c['panel']}; color:{c['text']}; border:1px solid {c['border']};
  selection-background-color:{c['accent']}; selection-color:{c['accent_text']}; outline:0; }}
QCheckBox {{ background:transparent; spacing:8px; }}
QCheckBox::indicator, QListView::indicator {{ width:16px; height:16px; border:1px solid {c['muted']};
  border-radius:4px; background:{c['input']}; }}
QCheckBox::indicator:checked, QListView::indicator:checked {{ background:{c['accent']}; border-color:{c['accent']};
  image:url({_check_png()}); }}
QCheckBox::indicator:hover, QListView::indicator:hover {{ border-color:{c['accent']}; }}
QSlider::groove:horizontal {{ height:4px; background:{c['border']}; border-radius:2px; }}
QSlider::sub-page:horizontal {{ background:{c['accent']}; border-radius:2px; }}
QSlider::handle:horizontal {{ background:{c['accent']}; width:14px; height:14px; margin:-6px 0; border-radius:7px; }}
QListWidget {{ background:{c['panel']}; border:1px solid {c['border']}; border-radius:8px; outline:0; }}
QListWidget::item {{ color:{c['text']}; border:1px solid transparent; border-radius:9px; padding:4px; }}
QListWidget::item:hover {{ background:{c['panel2']}; }}
QListWidget::item:selected {{ background:{c['accent_bg']}; border:1px solid {c['accent']}; color:{c['text']}; }}
QGroupBox {{ border:1px solid {c['border']}; border-radius:9px; margin-top:16px; padding-top:12px; }}
QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 6px; color:{c['accent']}; }}
QScrollBar:vertical {{ background:{c['bg']}; width:12px; margin:0; }}
QScrollBar::handle:vertical {{ background:{c['border']}; border-radius:6px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:{c['muted']}; }}
QScrollBar:horizontal {{ background:{c['bg']}; height:12px; margin:0; }}
QScrollBar::handle:horizontal {{ background:{c['border']}; border-radius:6px; min-width:30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background:transparent; }}
QMenu {{ background:{c['panel']}; color:{c['text']}; border:1px solid {c['border']}; padding:4px; }}
QMenu::item {{ padding:6px 22px; border-radius:4px; }}
QMenu::item:selected {{ background:{c['accent']}; color:{c['accent_text']}; }}
QMenu::separator {{ height:1px; background:{c['border']}; margin:4px 8px; }}
QMessageBox {{ background:{c['bg']}; }}
QFrame#card {{ background:{c['panel']}; border:1px solid {c['border']}; border-radius:12px; }}
"""


_applied = {"qss": None}


def apply_theme(app, theme, accent):
    """Apply the theme. Re-styling every widget is slow, so it is skipped when nothing changed."""
    c = colors(theme, accent)
    qss = build_qss(c)
    if app.property("_kad_qss") != qss:
        if app.style().objectName().lower() != "fusion":
            app.setStyle("Fusion")
        app.setStyleSheet(qss)
        app.setProperty("_kad_qss", qss)
    return c
