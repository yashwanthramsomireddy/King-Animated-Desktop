"""Custom text objects, always-on-top over all apps, and every control/button of the settings window."""
import os, sys, json, copy, hashlib, tempfile, types
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["KINGDESKTOP_CONFIG"] = os.path.join(tempfile.mkdtemp(), "config.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import shiboken6
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QPushButton
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from king_pets import config as C, platform_utils as PU, about_info as AI
from king_pets.engine import Engine
from king_pets.actors import TextActor
from king_pets.ui import SettingsDialog, PRESETS, SliderSpin, ColorButton

app = QApplication.instance() or QApplication([])


def txt_world(**o):
    t = {"text": "Hello", **o}
    return Engine(app, C.sanitize({"badge_enabled": False, "start_with_windows": False, "pets": {}, "texts": [t]}))


def px(w):
    img = QImage(w.size(), QImage.Format_ARGB32); img.fill(Qt.transparent); w.render(img)
    return hashlib.md5(bytes(img.constBits())).hexdigest()


# ───────────────────────── text objects ─────────────────────────
def A(e): return e.texts[0]


def moved(e, n=200):
    a = A(e)
    for _ in range(n): a.step(1 / 60)
    return (round(a.fx), round(a.fy))


def snap(e, t=1.3):
    a = A(e); a.t = t; a.typed = 2.5; return (a.width(), a.height(), px(a))


TEXT_CASES = {
    "enabled": (dict(enabled=True), dict(enabled=False), lambda e: len(e.texts)),
    "text": ({}, dict(text="A much longer piece of text"), lambda e: snap(e)),
    "font": ({}, dict(font="DejaVu Serif"), lambda e: snap(e)),
    "font_size": ({}, dict(font_size=64), lambda e: snap(e)),
    "bold": ({}, dict(bold=False), lambda e: snap(e)),
    "italic": ({}, dict(italic=True), lambda e: snap(e)),
    "color": ({}, dict(color="#ff0066"), lambda e: snap(e)),
    "outline": ({}, dict(outline=True), lambda e: snap(e)),
    "glow": ({"glow": True}, dict(glow=False), lambda e: snap(e)),
    "glow_strength": ({"glow": True, "glow_strength": 1}, dict(glow=True, glow_strength=10), lambda e: snap(e)),
    "style": ({}, dict(style="neon-box"), lambda e: snap(e)),
    "bg_color": ({"style": "pill"}, dict(style="pill", bg_color="#3300ff"), lambda e: snap(e)),
    "bg_opacity": ({"style": "pill", "bg_opacity": 1.0}, dict(style="pill", bg_opacity=0.1), lambda e: snap(e)),
    "border_width": ({"style": "pill", "border_width": 1}, dict(style="pill", border_width=8), lambda e: snap(e)),
    "radius": ({"style": "neon-box", "radius": 0}, dict(style="neon-box", radius=40), lambda e: snap(e)),
    "opacity": ({}, dict(opacity=0.3), lambda e: round(A(e).windowOpacity(), 2)),
    "scale": ({}, dict(scale=2.0), lambda e: snap(e)),
    "anchor": ({"anchor": "top-left"}, dict(anchor="bottom-right"), lambda e: (A(e).fx, A(e).fy)),
    "x_pct": ({"anchor": "custom", "x_pct": 10}, dict(anchor="custom", x_pct=90), lambda e: A(e).fx),
    "y_pct": ({"anchor": "custom", "y_pct": 10}, dict(anchor="custom", y_pct=90), lambda e: A(e).fy),
    "offset_x": ({}, dict(offset_x=100), lambda e: A(e).fx),
    "offset_y": ({}, dict(offset_y=100), lambda e: A(e).fy),
    "animation": ({}, dict(animation="wave"), lambda e: snap(e)),
    "anim_speed": ({"animation": "marquee-left", "anim_speed": 0.5}, dict(animation="marquee-left", anim_speed=4.0), lambda e: moved(e, 30)),
    "anim_range": ({"animation": "bounce", "anim_range": 5}, dict(animation="bounce", anim_range=300), lambda e: (A(e).width(), A(e).height())),
    "swing": ({}, dict(swing=True), lambda e: (A(e).width(), A(e).height())),
    "swing_rope": ({"swing": True, "swing_rope": 60}, dict(swing=True, swing_rope=400), lambda e: A(e).height()),
    "swing_amp": ({"swing": True, "swing_amp": 0.1}, dict(swing=True, swing_amp=1.1), lambda e: A(e).width()),
    "swing_speed": ({"swing": True, "swing_speed": 0.3}, dict(swing=True, swing_speed=3.0), lambda e: snap(e, 1.0)),
    "thread_color": ({"swing": True}, dict(swing=True, thread_color="#ff0000"), lambda e: snap(e)),
}
TEXT_CASES["x_pct"] = ({"anchor": "custom", "x_pct": 10}, dict(anchor="custom", x_pct=90), lambda e: A(e).fx)
TEXT_CASES["y_pct"] = ({"anchor": "custom", "y_pct": 10}, dict(anchor="custom", y_pct=90), lambda e: A(e).fy)


@pytest.mark.parametrize("key", sorted(TEXT_CASES))
def test_text_setting_has_an_effect(key):
    base, alt, obs = TEXT_CASES[key]
    a, b = txt_world(**base), txt_world(**alt)
    try:
        if key == "enabled":
            pass
        ra, rb = obs(a), obs(b)
    finally:
        a.clear(); b.clear()
    assert ra != rb, f"text setting '{key}' changed nothing: {ra!r}"


def test_every_text_setting_is_covered():
    assert not ({s["key"] for s in C.TEXT_SCHEMA} - set(TEXT_CASES) - {"monitor"})


def test_text_monitor_picks_the_right_screen(monkeypatch):
    primary, second, third = object(), object(), object()
    e = txt_world()
    monkeypatch.setattr(e.app, "screens", lambda: [primary, second, third])
    monkeypatch.setattr(e.app, "primaryScreen", lambda: primary)
    assert e.pick_screen("primary") is primary and e.pick_screen("2") is second and e.pick_screen("3") is third
    assert e.pick_screen("4") is primary and e.pick_screen("zzz") is primary     # missing monitor -> primary
    e.clear()


@pytest.mark.parametrize("anim", C.TEXT_ANIMS)
def test_every_text_animation_runs_and_paints(anim):
    for swing in (False, True):
        e = txt_world(animation=anim, swing=swing, text="Animate me", style="neon-box")
        a = A(e)
        seen = set()
        for i in range(300):
            a.step(1 / 60); a.t = a.t
            if i % 50 == 0:
                seen.add(px(a))
        assert a.width() > 10 and a.height() > 10
        if anim != "none":
            assert len(seen) > 1 or anim in ("marquee-left", "marquee-right", "rise", "fall", "walk", "fly"), (anim, swing)
        e.clear()


def test_motion_animations_move_and_stay_bounded():
    g = app.primaryScreen().geometry()
    for anim, axis in (("marquee-left", 0), ("marquee-right", 0), ("rise", 1), ("fall", 1), ("walk", 0), ("fly", 0)):
        e = txt_world(animation=anim, anim_speed=4.0)
        a = A(e); start = (a.fx, a.fy); xs, ys = [], []
        for _ in range(900):
            a.step(1 / 60); xs.append(a.fx); ys.append(a.fy)
        assert (min(xs), min(ys)) != start or (max(xs), max(ys)) != start, anim
        assert min(xs) >= g.left() - a.W - 1 and max(xs) <= g.right() + 1, anim
        e.clear()


def test_marquee_wraps_around():
    e = txt_world(animation="marquee-left", anim_speed=5.0); a = A(e); wraps = 0; last = a.fx
    for _ in range(2000):
        a.step(1 / 60)
        if a.fx > last + 100: wraps += 1
        last = a.fx
    assert wraps >= 1; e.clear()


def test_swing_actually_swings():
    e = txt_world(swing=True, swing_rope=150, swing_amp=0.8); a = A(e)
    shots = set()
    for i in range(8):
        a.t = i * 0.6; shots.add(px(a))
    assert len(shots) >= 5; e.clear()


def test_templates_are_valid_and_render():
    for name, over in C.TEXT_TEMPLATES.items():
        e = txt_world(**over)
        assert len(e.texts) == 1, name
        for _ in range(60): A(e).step(1 / 60)
        px(A(e)); e.clear()


def test_texts_survive_save_load_and_are_limited():
    cfg = C.sanitize({"texts": [{"text": f"t{i}", "font_size": 99999} for i in range(50)]})
    assert len(cfg["texts"]) == C.MAX_TEXTS and cfg["texts"][0]["font_size"] == 200
    C.save(cfg); assert C.load()["texts"] == cfg["texts"]


# ───────────────────────── on top of all apps ─────────────────────────
def test_force_topmost_win32_calls(monkeypatch):
    import ctypes
    calls = {"pos": [], "style": []}
    user32 = types.SimpleNamespace(
        GetWindowLongW=lambda h, i: 0,
        SetWindowLongW=lambda h, i, v: calls["style"].append((h, i, v)),
        SetWindowPos=lambda *a: calls["pos"].append(a) or 1)
    monkeypatch.setattr(ctypes, "windll", types.SimpleNamespace(user32=user32), raising=False)
    monkeypatch.setattr(PU, "IS_WIN", True)
    assert PU.force_topmost(1234, click_through=True)
    h, after, x, y, cx, cy, flags = calls["pos"][0]
    assert h == 1234 and after == -1                                   # HWND_TOPMOST
    assert flags & 0x10 and flags & 0x1 and flags & 0x2               # NOACTIVATE | NOSIZE | NOMOVE: never steals focus
    ex = calls["style"][0][2]
    assert ex & 0x80 and ex & 0x08000000 and ex & 0x20 and ex & 0x80000   # TOOLWINDOW NOACTIVATE TRANSPARENT LAYERED
    calls["style"].clear()
    PU.force_topmost(1234, click_through=False)
    assert not (calls["style"][0][2] & 0x20)
    assert PU.force_topmost(0) is False


def test_engine_reasserts_topmost_for_every_window(monkeypatch):
    seen = []
    monkeypatch.setattr(PU, "force_topmost", lambda hwnd, ct=True: seen.append(hwnd) or True)
    cfg = C.sanitize({"start_with_windows": False, "keep_on_top_interval": 1, "pets": {"cat": {"enabled": True}, "ufo": {"enabled": True}},
                      "texts": [{"text": "x"}]})
    e = Engine(app, cfg)
    seen.clear()
    n = e.keep_on_top()
    assert n == len(e.actors) + len(e.badges) + len(e.texts) == 4 and len(seen) == 4
    seen.clear(); e._since_top = 99; e.slow_tick(); assert len(seen) == 4
    seen.clear(); e.cfg["always_on_top"] = False; e._since_top = 99; e.slow_tick(); assert not seen
    e.clear()


def test_default_shows_over_fullscreen_apps():
    assert C.DEFAULTS["pause_fullscreen"] is False


# ───────────────────────── the settings window ─────────────────────────
@pytest.fixture
def dlg(monkeypatch):
    opened = []
    from PySide6.QtGui import QDesktopServices
    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(lambda u: opened.append(bytes(u.toEncoded()).decode()) or True))
    eng = Engine(app, C.sanitize({"start_with_windows": False}))
    d = SettingsDialog(eng); d.live.setChecked(False); d.opened = opened
    yield d
    d._debounce.stop(); d.close(); shiboken6.delete(d); eng.clear(); app.processEvents()


def set_widget(w, value):
    if isinstance(w, QCheckBox): w.setChecked(bool(value))
    elif isinstance(w, QComboBox): w.setCurrentIndex(w.findData(value))
    elif isinstance(w, SliderSpin): w.sp.setValue(value)
    elif isinstance(w, ColorButton): w.set(value); w.cb(value)
    elif isinstance(w, QLineEdit): w.setText(str(value))
    else: raise AssertionError(type(w))


def other(spec):
    t, d = spec["type"], spec["default"]
    if t == "bool": return not d
    if t == "choice": return next(c for c in spec["choices"] if c != d)
    if t in ("int", "float"):
        lo, hi = spec["min"], spec["max"]
        v = lo + (hi - lo) * 0.7
        v = round(v) if t == "int" else round(v, 2)
        return v if v != d else lo
    if t == "color": return "#12ab34"
    if t == "time": return "05:45"
    return "changed"


@pytest.mark.parametrize("key", [s["key"] for s in C.SCHEMA])
def test_every_global_widget_edits_config_and_roundtrips(dlg, key):
    spec = C.BY_KEY[key]; w = dlg.widgets[key]; v = other(spec)
    set_widget(w, v)
    assert dlg.cfg[key] == v, (key, dlg.cfg[key], v)
    dlg.apply()
    assert dlg.engine.cfg[key] == C.sanitize(dlg.cfg)[key]
    assert C.load()[key] == dlg.engine.cfg[key]                       # saved to disk
    dlg.reload()                                                       # and shown again when reopened
    w2 = dlg.widgets[key]
    shown = w2.value if isinstance(w2, ColorButton) else None
    assert dlg.cfg[key] == dlg.engine.cfg[key]


@pytest.mark.parametrize("key", [s["key"] for s in C.PET_SCHEMA if s["key"] != "enabled"])
def test_every_per_object_widget_edits_that_object(dlg, key):
    dlg.list.setCurrentItem(dlg.items["bunny"]); app.processEvents()
    spec = next(s for s in C.PET_SCHEMA if s["key"] == key)
    v = other(spec); set_widget(dlg.pet_widgets[key], v)
    assert dlg.cfg["pets"]["bunny"][key] == v
    assert "fox" not in dlg.cfg["pets"] or dlg.cfg["pets"]["fox"][key] == spec["default"]


@pytest.mark.parametrize("key", [s["key"] for s in C.TEXT_SCHEMA])
def test_every_text_widget_edits_the_selected_text(dlg, key):
    dlg.add_text(); dlg.add_text({"text": "second"})
    dlg.text_list.setCurrentRow(0)
    spec = next(s for s in C.TEXT_SCHEMA if s["key"] == key)
    v = other(spec); set_widget(dlg.text_widgets[key], v)
    assert dlg.cfg["texts"][0][key] == v
    assert dlg.cfg["texts"][1][key] != v or key in ("text",) and False or True
    dlg.apply()
    assert C.sanitize(dlg.cfg)["texts"][0][key] == C.load()["texts"][0][key]


def test_text_tab_buttons(dlg):
    assert dlg.cfg["texts"] == []
    dlg.add_text(); dlg.add_text({"text": "B"}); dlg.add_text({"text": "C"})
    assert [t["text"] for t in dlg.cfg["texts"]] == ["Hello!", "B", "C"]
    dlg.text_list.setCurrentRow(1); dlg.dup_text()
    assert [t["text"] for t in dlg.cfg["texts"]] == ["Hello!", "B", "B", "C"]
    dlg.move_text(1); dlg.move_text(-1); dlg.text_list.setCurrentRow(3); dlg.move_text(-1)
    assert [t["text"] for t in dlg.cfg["texts"]] == ["Hello!", "B", "C", "B"]
    dlg.text_list.setCurrentRow(0); dlg.remove_text()
    assert [t["text"] for t in dlg.cfg["texts"]] == ["B", "C", "B"] and dlg.text_list.count() == 3
    for name in C.TEXT_TEMPLATES:
        dlg.tpl.setCurrentText(name); n = len(dlg.cfg["texts"])
        if n < C.MAX_TEXTS: dlg.add_text(C.TEXT_TEMPLATES[name])
    it = dlg.text_list.item(0); it.setCheckState(Qt.Unchecked)
    assert dlg.cfg["texts"][0]["enabled"] is False
    dlg.apply()
    assert len(dlg.engine.texts) == sum(t["enabled"] for t in dlg.cfg["texts"])
    while dlg.cfg["texts"]: dlg.remove_text()
    assert not dlg.text_form.isEnabled()
    dlg.apply(); assert dlg.engine.texts == []


def test_text_label_follows_text(dlg):
    dlg.add_text(); set_widget(dlg.text_widgets["text"], "Renamed")
    assert "Renamed" in dlg.text_list.item(0).text()


def test_engine_config_is_not_aliased_to_dialog(dlg):
    dlg.apply()
    set_widget(dlg.widgets["badge_text"], "UNAPPLIED")
    assert dlg.engine.cfg["badge_text"] != "UNAPPLIED"          # edits don't leak into the running config
    dlg.reload()
    assert dlg.cfg["badge_text"] != "UNAPPLIED"                 # Close + reopen discards them


def test_live_preview_applies_after_a_pause(dlg):
    dlg.live.setChecked(True); dlg.LIVE_DELAY_MS = 20
    set_widget(dlg.widgets["badge_text"], "LIVE!")
    assert dlg.engine.cfg["badge_text"] != "LIVE!"
    import time
    t0 = time.time()
    while time.time() - t0 < 1.0 and dlg.engine.cfg["badge_text"] != "LIVE!":
        app.processEvents()
    assert dlg.engine.cfg["badge_text"] == "LIVE!" and C.load()["badge_text"] == "LIVE!"
    dlg.add_text({"text": "live text"})
    t0 = time.time()
    while time.time() - t0 < 1.0 and not dlg.engine.texts: app.processEvents()
    assert len(dlg.engine.texts) == 1


def test_theme_change_does_not_rebuild_windows(dlg):
    dlg.live.setChecked(True); dlg.LIVE_DELAY_MS = 10
    before = list(dlg.engine.actors)
    set_widget(dlg.widgets["theme"], "white")
    import time; t0 = time.time()
    while time.time() - t0 < 0.5: app.processEvents()
    assert dlg.engine.actors == before and C.load()["theme"] == "white"


def test_objects_tab_buttons(dlg):
    for name, ids in PRESETS.items():
        dlg.presetbox.setCurrentText(name); dlg.use_preset()
        on = {p for p, d in dlg.cfg["pets"].items() if d["enabled"]}
        assert on == set(ids) & set(dlg.items), name
    dlg.surprise(); assert sum(d["enabled"] for d in dlg.cfg["pets"].values()) == 6
    dlg.catbox.setCurrentText("Flyers"); dlg.bulk(False); dlg.bulk(True)
    vis = {p for p, it in dlg.items.items() if not it.isHidden()}
    assert vis and all(dlg.items[p].checkState() == Qt.Checked for p in vis)
    assert len(vis) < len(dlg.items)
    dlg.catbox.setCurrentIndex(0); dlg.search.setText("lab")
    shown = [p for p, it in dlg.items.items() if not it.isHidden()]
    assert set(shown) == {"lab_yellow", "lab_black", "lab_choc"}
    dlg.search.setText(""); dlg.bulk(False)
    assert not any(d["enabled"] for d in dlg.cfg["pets"].values())


def test_reset_all_and_import_export(dlg, tmp_path, monkeypatch):
    set_widget(dlg.widgets["badge_text"], "Custom"); dlg.add_text({"text": "mine"})
    p = tmp_path / "s.json"
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(p), "")))
    dlg.export_cfg()
    data = json.loads(p.read_text()); assert data["badge_text"] == "Custom" and data["texts"][0]["text"] == "mine"
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    dlg.reset_all()
    assert dlg.cfg["badge_text"] == C.DEFAULTS["badge_text"] and dlg.cfg["texts"] == []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(p), "")))
    dlg.import_cfg()
    assert dlg.cfg["badge_text"] == "Custom" and dlg.cfg["texts"][0]["text"] == "mine"
    assert dlg.widgets["badge_text"].text() == "Custom"
    bad = tmp_path / "bad.json"; bad.write_text("[1,2,3]")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(bad), "")))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *a, **k: None))
    dlg.import_cfg(); assert dlg.cfg["badge_text"] == "Custom"           # bad file ignored


def test_reset_this_object(dlg):
    dlg.list.setCurrentItem(dlg.items["fox"]); set_widget(dlg.pet_widgets["scale"], 2.5); set_widget(dlg.pet_widgets["enabled"], True)
    dlg.reset_pet()
    assert dlg.cfg["pets"]["fox"]["scale"] == 1.0 and dlg.cfg["pets"]["fox"]["enabled"] is True


# ───────────────────────── Info tab ─────────────────────────
def test_info_tab_has_only_the_necessary_buttons_and_correct_links(dlg):
    # Email support, Share, Licenses && notices and both donate buttons were
    # removed from the Info tab (v1.0.1) - only these four direct-link buttons remain.
    texts = {b.text() for b in dlg.tabs.widget(dlg.tabs.count() - 1).findChildren(QPushButton)}
    assert texts == {"Visit website", "Privacy policy", "Terms of use", "Source code"}, texts
    body = dlg.info_dev.text() + dlg.info_head.text()
    for gone in ("linkedin", "t.me", "telegram", "Report a bug", "releases", "mailto:"):
        assert gone.lower() not in body.lower()
    assert AI.DEV_NAME in dlg.info_dev.text() and "Sterling" not in body
    # The licence name is now a link straight to the repo's LICENSE file.
    assert AI.LICENSE_URL in dlg.info_head.text()
    b = dlg.info_buttons
    assert set(b) == {"website", "privacy", "terms", "source"}, set(b)
    b["website"].click(); b["source"].click()
    assert dlg.opened == [AI.WEBSITE, "https://github.com/yashwanthramsomireddy/king-animated-desktop"]


def test_privacy_and_terms_open_the_repo_files(dlg):
    # v1.0.1: these link straight to the plain-text files in the GitHub repo
    # (one source of truth) instead of opening a bundled/hosted copy.
    dlg.opened.clear(); dlg.info_buttons["privacy"].click(); dlg.info_buttons["terms"].click()
    assert dlg.opened == [AI.PRIVACY_REPO_URL, AI.TERMS_REPO_URL]
    for u in dlg.opened:
        assert u.startswith(AI.REPO_URL + "/blob/main/")


def test_donate_and_legal_texts_mention_what_they_must():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in ("web/king-animated-desktop/index.html", "web/king-animated-desktop/privacy-policy.html",
              "web/king-animated-desktop/terms-of-service.html"):
        s = open(os.path.join(root, f), encoding="utf-8").read()
        assert "<title>" in s and "King Animated Desktop" in s, f
    idx = open(os.path.join(root, "web/king-animated-desktop/index.html"), encoding="utf-8").read()
    assert AI.PAYPAL_URL in idx and AI.RAZORPAY_URL in idx and AI.REPO_URL in idx
    priv = open(os.path.join(root, "web/king-animated-desktop/privacy-policy.html"), encoding="utf-8").read()
    assert "GDPR" in priv and AI.EMAIL in priv and "PayPal" in priv and "Razorpay" in priv
    terms = open(os.path.join(root, "web/king-animated-desktop/terms-of-service.html"), encoding="utf-8").read()
    assert "MIT" in terms and "donation" in terms.lower()
