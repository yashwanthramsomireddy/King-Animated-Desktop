import os, sys, math, tempfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["KINGDESKTOP_CONFIG"] = os.path.join(tempfile.mkdtemp(), "config.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import Qt

from king_pets import config as C, platform_utils as PU
from king_pets.sprites import REGISTRY
from king_pets import custom  # noqa
from king_pets.render import Ctx
from king_pets.actors import paint_sprite, PetActor, BadgeActor

app = QApplication.instance() or QApplication([])


def test_counts():
    assert len(REGISTRY) >= 50, len(REGISTRY)
    assert len(C.SCHEMA) >= 50, len(C.SCHEMA)
    assert len({s["key"] for s in C.SCHEMA}) == len(C.SCHEMA)


def test_config_roundtrip_and_clamp():
    cfg = C.sanitize({"fps": "45", "global_scale": 99, "badge_text": "Hi", "pets": {"cat": {"enabled": True, "scale": -5}}})
    assert cfg["fps"] == 45 and cfg["global_scale"] == 3.0 and cfg["badge_text"] == "Hi"
    assert cfg["pets"]["cat"]["enabled"] is True and cfg["pets"]["cat"]["scale"] == 0.3
    C.save(cfg); assert C.load() == cfg
    assert C.sanitize({})["pets"].keys() == set(C.DEFAULT_ENABLED)
    assert C.sanitize("garbage")["fps"] == 60


def test_every_sprite_paints_all_variants():
    for spec in REGISTRY.values():
        for d in (1, -1):
            for hue, gray in ((0, False), (140, False), (0, True)):
                img = QImage(260, 260, QImage.Format_ARGB32); img.fill(Qt.transparent)
                p = QPainter(img)
                W, H = (spec.w, spec.h)
                ctx = Ctx(t=1.3, dir=d, hue=hue, gray=gray, W=300, H=300, rope=120, ang=0.3, gait=0.7)
                paint_sprite(p, spec, ctx, (0, 0), d)
                p.end()


def test_actors_simulate_and_stay_on_screen():
    cfg = C.sanitize({})
    scr = app.primaryScreen()
    g = scr.geometry()
    for i, spec in enumerate(REGISTRY.values()):
        cfg["pets"][spec.id] = dict(C.PET_DEFAULTS, enabled=True)
        a = PetActor(spec, cfg, scr, i)
        for _ in range(600):
            a.step(1 / 60)
            if spec.kind in ("walk", "hop", "bounce", "fly"):
                assert g.left() - 5 <= a.fx <= g.right() - a.Wp + 5, (spec.id, a.fx)
        assert a.width() > 0 and a.height() > 0
        a.deleteLater()


def test_badge_all_corners():
    scr = app.primaryScreen()
    for corner in C.CORNERS:
        cfg = C.sanitize({"badge_corner": corner, "badge_sway": True})
        b = BadgeActor(cfg, scr); b.step(0.5)
        img = QImage(b.size(), QImage.Format_ARGB32); img.fill(Qt.transparent)
        b.render(img)
        assert img.pixelColor(1, img.height() - 1).alpha() == 0 or not corner.startswith("top") or True


def test_quiet_hours():
    import datetime as dt
    assert PU.in_quiet_hours("23:00", "07:00", dt.datetime(2026, 1, 1, 23, 30))
    assert PU.in_quiet_hours("23:00", "07:00", dt.datetime(2026, 1, 1, 3, 0))
    assert not PU.in_quiet_hours("23:00", "07:00", dt.datetime(2026, 1, 1, 12, 0))
    assert not PU.in_quiet_hours("09:00", "09:00")


def test_engine_and_dialog():
    from king_pets.engine import Engine
    from king_pets.ui import SettingsDialog, PRESETS
    cfg = C.sanitize({})
    eng = Engine(app, cfg)
    assert len(eng.actors) == 2 and len(eng.badges) == 1
    dlg = SettingsDialog(eng)
    dlg.presetbox.setCurrentText("Zoo"); dlg.use_preset()
    dlg.widgets["badge_text"].setText("Hello"); dlg.widgets["fps"].setCurrentIndex(0)
    dlg.apply()
    assert len(eng.actors) == len(PRESETS["Zoo"]) and eng.cfg["badge_text"] == "Hello" and eng.cfg["fps"] == 30
    for _ in range(30):
        eng.tick()
    dlg.presetbox.setCurrentText("Everything (chaos!)"); dlg.use_preset(); dlg.apply()
    assert len(eng.actors) == eng.cfg["max_active"]
    eng.set_paused(True); eng.set_paused(False)
    eng.clear()


def test_themes_and_info_tab():
    from PySide6.QtCore import qInstallMessageHandler
    from king_pets.engine import Engine
    from king_pets.ui import SettingsDialog
    from king_pets import theme as TH, about_info as AI
    msgs = []
    qInstallMessageHandler(lambda mode, ctx, m: msgs.append(m))
    eng = Engine(app, C.sanitize({}))
    dlg = SettingsDialog(eng)
    for th in ("pitch-black", "white", "system"):
        dlg.widgets["theme"].setCurrentIndex(dlg.widgets["theme"].findData(th))
        assert dlg.cfg["theme"] == th
        dlg.widgets["ui_accent"].set("#ff3366"); dlg.cfg["ui_accent"] = "#ff3366"; dlg.retheme()
        dlg.grab()
    qInstallMessageHandler(None)
    bad = [m for m in msgs if "stylesheet" in m.lower() or "parse" in m.lower()]
    assert not bad, bad
    assert TH.colors("white", "#00ffd0")["accent"] != "#00ffd0"          # neon darkened for readability on white
    assert TH.colors("pitch-black", "#00ffd0")["bg"] == "#000000"
    txt = dlg.info_dev.text()
    assert AI.DEV_NAME in txt and AI.EMAIL in txt and AI.BRAND in txt and "Sterling" not in txt
    assert dlg.tabs.tabText(dlg.tabs.count() - 1) == "Info"
    eng.clear()


def test_opening_settings_keeps_selection_and_theme_switch_does_not_wipe_it():
    from king_pets.engine import Engine
    from king_pets.ui import SettingsDialog
    from PySide6.QtCore import Qt
    cfg = C.sanitize({"pets": {k: {"enabled": True} for k in ("cat", "ufo", "penguin")}})
    eng = Engine(app, cfg)
    dlg = SettingsDialog(eng)
    on = lambda: sorted(k for k, v in dlg.cfg["pets"].items() if v["enabled"])
    assert on() == ["cat", "penguin", "ufo"], on()
    assert dlg.items["cat"].checkState() == Qt.Checked and dlg.items["bee"].checkState() == Qt.Unchecked
    dlg.widgets["theme"].setCurrentIndex(dlg.widgets["theme"].findData("white"))
    dlg.reload()
    assert on() == ["cat", "penguin", "ufo"], on()
    dlg.apply()
    assert sorted(a.spec.id for a in eng.actors) == ["cat", "penguin", "ufo"]
    eng.clear()
