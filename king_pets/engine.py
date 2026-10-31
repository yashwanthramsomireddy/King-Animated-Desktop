"""Engine: builds the windows from config, runs the animation loop, tray icon."""
import sys
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from . import config as C
from . import platform_utils as PU
from .sprites import REGISTRY
from .actors import PetActor, BadgeActor, TextActor
from . import custom  # noqa: F401  (registers hand-coded characters)


def tray_icon():
    pm = QPixmap(64, 64); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#08080c")); p.setPen(QColor("#00ffd0"))
    p.drawRoundedRect(4, 14, 56, 36, 6, 6)
    p.setPen(QColor("#00ffd0")); p.drawText(pm.rect(), Qt.AlignCenter, "K")
    p.end()
    return QIcon(pm)


class Engine:
    def __init__(self, app, cfg):
        self.app, self.cfg = app, cfg
        self.actors, self.badges, self.texts = [], [], []
        self.paused = False
        self.hidden_reason = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.clock = QElapsedTimer()
        self.slow = QTimer(); self.slow.timeout.connect(self.slow_tick); self.slow.start(1000)
        self._since_top = 0
        self.rainbow = 0.0
        self.settings_dialog = None
        self.rebuild()

    # ── lifecycle ──
    def screens(self):
        scr = self.app.screens()
        m = self.cfg["monitor"]
        if m == "all":
            return scr
        if m == "primary":
            return [self.app.primaryScreen()]
        i = int(m) - 1
        return [scr[i]] if 0 <= i < len(scr) else [self.app.primaryScreen()]

    def pick_screen(self, m):
        """'primary' or a 1-based monitor number; falls back to the primary screen if that monitor is not connected."""
        scr = self.app.screens()
        try:
            i = int(m) - 1
        except (TypeError, ValueError):
            return self.app.primaryScreen()
        return scr[i] if 0 <= i < len(scr) else self.app.primaryScreen()

    def clear(self):
        for w in self.actors + self.badges + self.texts:
            w.hide(); w.close(); w.deleteLater()
        self.actors, self.badges, self.texts = [], [], []

    def rebuild(self, cfg=None):
        if cfg is not None:
            self.cfg = cfg
        self.clear()
        c = self.cfg
        PU.set_autostart(c["start_with_windows"])
        if not c["enabled"]:
            self.timer.stop()
            return
        scrs = self.screens()
        ids = [pid for pid, d in c["pets"].items() if d.get("enabled") and pid in REGISTRY][: c["max_active"]]
        for i, pid in enumerate(ids):
            self.actors.append(PetActor(REGISTRY[pid], c, scrs[i % len(scrs)], index=i))
        if c["badge_enabled"]:
            self.badges.append(BadgeActor(c, scrs[0]))
        allscr = self.app.screens()
        for i, tc in enumerate(c.get("texts", [])):
            if tc.get("enabled"):
                self.texts.append(TextActor(tc, c, self.pick_screen(tc["monitor"]), i))
        for w in self.all_windows():
            w.show()
        if c["always_on_top"]:
            QTimer.singleShot(150, self.keep_on_top)
        self.clock.start()
        self.timer.start(int(1000 / c["fps"]))
        self.check_visibility()

    # ── loop ──
    def tick(self):
        dt = min(self.clock.restart() / 1000.0, 0.1)
        if self.paused or self.hidden_reason:
            return
        c = self.cfg
        self.rainbow = (self.rainbow + dt * c["rainbow_speed"] * 360) % 360 if c["rainbow"] else 0.0
        for a in self.actors:
            a.hue_extra = self.rainbow
            a.step(dt)
            a.update()
        for b in self.badges:
            b.step(dt); b.update()
        for tx in self.texts:
            tx.step(dt); tx.update()

    def all_windows(self):
        return self.actors + self.badges + getattr(self, "texts", [])

    def slow_tick(self):
        self.check_visibility()
        c = self.cfg
        self._since_top += 1
        if c["always_on_top"] and not self.hidden_reason and not self.paused and self._since_top >= c["keep_on_top_interval"]:
            self._since_top = 0
            self.keep_on_top()

    def keep_on_top(self):
        n = 0
        for w in self.all_windows():
            if w.isVisible():
                n += bool(PU.force_topmost(int(w.winId()), self.cfg["click_through"]))
        return n

    def check_visibility(self):
        c = self.cfg
        reason = None
        if PU.in_quiet_hours(c["quiet_start"], c["quiet_end"]) and c["quiet_hours"]:
            reason = "quiet"
        elif c["pause_on_battery"] and PU.on_battery():
            reason = "battery"
        elif c["pause_fullscreen"] and any(PU.fullscreen_app_active(s.geometry()) for s in self.screens()):
            reason = "fullscreen"
        if reason != self.hidden_reason:
            self.hidden_reason = reason
            for w in self.all_windows():
                w.setVisible(reason is None and not self.paused)

    def set_paused(self, v):
        self.paused = v
        for w in self.all_windows():
            w.setVisible(not v and not self.hidden_reason)


def run(open_settings=False, background=False):
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    import os, tempfile
    from PySide6.QtCore import QLockFile
    lock = QLockFile(os.path.join(tempfile.gettempdir(), "kingdesktop.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(200):          # already running (e.g. autostart + manual launch)
        return 0
    app.setApplicationName(C.APP_NAME)
    cfg = C.load()
    from . import theme as TH
    TH.apply_theme(app, cfg["theme"], cfg["ui_accent"])
    first_run = not __import__("os").path.exists(C.config_path())
    if first_run:
        C.save(cfg)
    eng = Engine(app, cfg)

    from .ui import SettingsDialog

    def show_settings():
        if eng.settings_dialog is None:
            eng.settings_dialog = SettingsDialog(eng)
        eng.settings_dialog.reload()
        eng.settings_dialog.show(); eng.settings_dialog.raise_(); eng.settings_dialog.activateWindow()

    tray = QSystemTrayIcon(tray_icon())
    menu = QMenu()
    menu.addAction("Settings / choose objects...", show_settings)
    pause = QAction("Pause pets", menu, checkable=True)
    pause.toggled.connect(lambda v: (eng.set_paused(v), pause.setText("Resume pets" if v else "Pause pets")))
    menu.addAction(pause)
    menu.addSeparator()
    menu.addAction("Quit King Animated Desktop", app.quit)
    tray.setContextMenu(menu)
    tray.setToolTip(f"{C.APP_NAME} {C.VERSION}")
    tray.activated.connect(lambda r: show_settings() if r in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger) else None)
    tray.show()
    if open_settings or (first_run and not background):
        QTimer.singleShot(400, show_settings)
    app._king_refs = (eng, tray, menu, lock)          # keep alive
    return app.exec()
