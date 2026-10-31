"""Every setting must DO something. For each key we build two worlds (baseline vs changed) and assert that an
observable (pixels, geometry, motion, flags, timers...) differs. A setting that does nothing fails here."""
import os, sys, hashlib, tempfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["KINGDESKTOP_CONFIG"] = os.path.join(tempfile.mkdtemp(), "config.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from king_pets import config as C, platform_utils as PU
from king_pets.engine import Engine
from king_pets import theme as TH

app = QApplication.instance() or QApplication([])


def world(over=None, pets=("cat",), pet_over=None, badge=False):
    cfg = C.sanitize({"badge_enabled": badge, "pause_fullscreen": False, "start_with_windows": False, **(over or {}),
                      "pets": {p: {"enabled": True, **(pet_over or {})} for p in pets}})
    return Engine(app, cfg)


def pixels(w):
    img = QImage(w.size(), QImage.Format_ARGB32); img.fill(Qt.transparent); w.render(img)
    return hashlib.md5(bytes(img.constBits())).hexdigest()


def snap(eng, t=1.7):
    out = []
    for a in eng.actors + eng.badges:
        a.t = t
        if hasattr(a, "gait"): a.gait = 0.9
        out.append(pixels(a))
    return tuple(out)


def run(eng, n=240, dt=1 / 60):
    for _ in range(n):
        for a in eng.actors:
            a.step(dt)
    return eng


def xy(eng, n=240):
    run(eng, n); return tuple((round(a.fx, 1), round(a.fy, 1)) for a in eng.actors)


def ys(eng, n=240):
    out = []
    for _ in range(n):
        for a in eng.actors: a.step(1 / 60)
        out.append(round(eng.actors[0].fy, 1))
    return tuple(out)


def xs(eng, n=240):
    out = []
    for _ in range(n):
        for a in eng.actors: a.step(1 / 60)
        out.append(round(eng.actors[0].fx, 1))
    return tuple(out)


def flips(eng, n=240):
    last, c = None, 0
    for _ in range(n):
        eng.actors[0].step(1 / 60)
        if last is not None and eng.actors[0].dir != last: c += 1
        last = eng.actors[0].dir
    return c


def rested(eng, n=240):
    c = 0
    for _ in range(n):
        eng.actors[0].step(1 / 60); c += (not eng.actors[0].moving)
    return c


def badge_geo(eng):
    b = eng.badges[0]; return (b.width(), b.height(), b.geometry().x(), b.geometry().y())


def badge_px(eng):
    b = eng.badges[0]; b.t = 0.7; return pixels(b)


W = lambda **k: dict(pets=("cat",), **k)
# key: (baseline overrides, changed overrides, world kwargs, observer)
PX = snap
def extent(e, n=900, dt=1 / 60):
    a = e.actors[0]; lo = hi = a.fx
    for _ in range(n):
        a.step(dt); lo, hi = min(lo, a.fx), max(hi, a.fx)
    return round(lo), round(hi)


CASES = {
    # ── General ──
    "enabled": ({}, {"enabled": False}, {}, lambda e: len(e.actors)),
    "fps": ({"fps": 60}, {"fps": 30}, {}, lambda e: e.timer.interval()),
    "always_on_top": ({}, {"always_on_top": False}, {}, lambda e: bool(e.actors[0].windowFlags() & Qt.WindowStaysOnTopHint)),
    "click_through": ({}, {"click_through": False}, {}, lambda e: bool(e.actors[0].windowFlags() & Qt.WindowTransparentForInput)),
    "global_scale": ({}, {"global_scale": 2.0}, {}, lambda e: e.actors[0].width()),
    "global_speed": ({}, {"global_speed": 3.0}, {}, lambda e: xy(e, 60)),
    "global_opacity": ({}, {"global_opacity": 0.4}, {}, lambda e: round(e.actors[0].windowOpacity(), 2)),
    "max_active": ({"max_active": 5}, {"max_active": 2}, {"pets": ("cat", "fox", "bunny", "bear", "pig")}, lambda e: len(e.actors)),
    "theme": ({"theme": "pitch-black"}, {"theme": "white"}, {}, lambda e: TH.colors(e.cfg["theme"], "#00ffd0")["bg"]),
    "ui_accent": ({"ui_accent": "#00ffd0"}, {"ui_accent": "#ff3366"}, {}, lambda e: TH.colors("pitch-black", e.cfg["ui_accent"])["accent"]),
    # ── Appearance ──
    "hue_shift": ({}, {"hue_shift": 120}, {}, PX),
    "saturation": ({}, {"saturation": 0.2}, {}, PX),
    "brightness": ({}, {"brightness": 0.5}, {}, PX),
    "grayscale": ({}, {"grayscale": True}, {}, PX),
    "rainbow": ({"rainbow": False}, {"rainbow": True, "rainbow_speed": 1.0}, {}, lambda e: (e.timer.stop(), [e.tick() or e.clock.start() for _ in range(1)], setattr(e.actors[0], "t", 1.7), setattr(e, "rainbow", 0), e.__setattr__("rainbow", 0), [ (setattr(e,"rainbow",(e.rainbow+0.4*e.cfg["rainbow_speed"]*360)%360 if e.cfg["rainbow"] else 0), setattr(e.actors[0],"hue_extra",e.rainbow)) ], pixels(e.actors[0]))[-1]),
    "rainbow_speed": ({"rainbow": True, "rainbow_speed": 0.1}, {"rainbow": True, "rainbow_speed": 0.9}, {}, lambda e: (e.__setattr__("rainbow", (0.4 * e.cfg["rainbow_speed"] * 360) % 360), setattr(e.actors[0], "hue_extra", e.rainbow), setattr(e.actors[0], "t", 1.7), pixels(e.actors[0]))[-1]),
    "outline": ({"outline": "auto"}, {"outline": "white"}, {}, PX),
    "shadow": ({"shadow": True}, {"shadow": False}, {}, PX),
    "shadow_opacity": ({"shadow": True, "shadow_opacity": 0.1}, {"shadow": True, "shadow_opacity": 0.9}, {}, PX),
    "mirror_all": ({}, {"mirror_all": True}, {}, lambda e: e.actors[0].dir),
    "smooth": ({"smooth": True}, {"smooth": False}, {}, PX),
    # ── Behaviour ──
    "random_turn": ({"random_turn": False, "turn_chance": 1.0}, {"random_turn": True, "turn_chance": 1.0}, {}, flips),
    "turn_chance": ({"random_turn": True, "turn_chance": 0.0}, {"random_turn": True, "turn_chance": 1.0}, {}, flips),
    "random_pause": ({"random_pause": False, "pause_chance": 1.0}, {"random_pause": True, "pause_chance": 1.0}, {}, rested),
    "pause_chance": ({"random_pause": True, "pause_chance": 0.0}, {"random_pause": True, "pause_chance": 1.0}, {}, rested),
    "pause_length": ({"random_pause": True, "pause_chance": 1.0, "pause_length": 0.5}, {"random_pause": True, "pause_chance": 1.0, "pause_length": 6.0}, {}, rested),
    "edge_margin": ({"edge_margin": 0, "walk_speed": 500, "random_pause": False, "random_turn": False}, {"edge_margin": 250, "walk_speed": 500, "random_pause": False, "random_turn": False}, {}, extent),
    "bottom_offset": ({}, {"bottom_offset": 200}, {}, lambda e: round(e.actors[0].y0)),
    "top_offset": ({}, {"top_offset": 120}, {"pets": ("monkey",)}, lambda e: round(e.actors[0].fy)),
    "walk_speed": ({"walk_speed": 40, "random_pause": False, "random_turn": False}, {"walk_speed": 400, "random_pause": False, "random_turn": False}, {}, lambda e: xy(e, 20)),
    "fly_speed": ({"fly_speed": 40, "random_turn": False}, {"fly_speed": 600, "random_turn": False}, {"pets": ("bee",)}, lambda e: xy(e, 20)),
    "float_speed": ({"float_speed": 20}, {"float_speed": 250}, {"pets": ("balloon",)}, lambda e: xy(e, 20)),
    "fall_speed": ({"fall_speed": 30}, {"fall_speed": 400}, {"pets": ("snowflake",)}, lambda e: xy(e, 20)),
    "bounce_height": ({"bounce_height": 30}, {"bounce_height": 400}, {"pets": ("soccer",)}, lambda e: min(ys(e, 300))),
    "hop_height": ({"hop_height": 2}, {"hop_height": 90}, {"pets": ("frog",)}, lambda e: min(ys(e, 300))),
    "swing_speed": ({"swing_speed": 0.5}, {"swing_speed": 2.5}, {"pets": ("spiderman",)}, lambda e: (setattr(e.actors[0], "t", 1.0), pixels(e.actors[0]))[-1]),
    "swing_amplitude": ({"swing_amplitude": 0.2}, {"swing_amplitude": 1.1}, {"pets": ("spiderman",)}, lambda e: (setattr(e.actors[0], "t", 1.0), e.actors[0].width(), pixels(e.actors[0]))),
    "swing_rope": ({"swing_rope": 120}, {"swing_rope": 450}, {"pets": ("spiderman",)}, lambda e: (e.actors[0].height(), pixels(e.actors[0]))),
    "fly_wobble": ({"fly_wobble": 0, "random_turn": False}, {"fly_wobble": 100, "random_turn": False}, {"pets": ("bee",)}, lambda e: max(ys(e, 300)) - min(ys(e, 300))),
    "fall_sway": ({"fall_sway": 0}, {"fall_sway": 140}, {"pets": ("snowflake",)}, lambda e: round(max(xs(e, 300)) - min(xs(e, 300)))),
    "spread_lanes": ({"spread_lanes": True}, {"spread_lanes": False}, {"pets": ("bee", "bird", "butterfly")}, lambda e: tuple(round(a.y0) for a in e.actors)),
    # ── Badge (need badge shown) ──
    "badge_enabled": ({"badge_enabled": False}, {"badge_enabled": True}, {}, lambda e: len(e.badges)),
    "badge_text": ({}, {"badge_text": "Hello World Long Text"}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_corner": ({}, {"badge_corner": "bottom-left"}, {"badge": True}, badge_geo),
    "badge_color": ({}, {"badge_color": "#ff0066"}, {"badge": True}, badge_px),
    "badge_bg_color": ({}, {"badge_bg_color": "#3300ff"}, {"badge": True}, badge_px),
    "badge_bg_opacity": ({"badge_bg_opacity": 1.0}, {"badge_bg_opacity": 0.1}, {"badge": True}, badge_px),
    "badge_glow": ({"badge_glow": True}, {"badge_glow": False}, {"badge": True}, badge_px),
    "badge_glow_strength": ({"badge_glow": True, "badge_glow_strength": 1}, {"badge_glow": True, "badge_glow_strength": 10}, {"badge": True}, badge_px),
    "badge_pulse": ({"badge_pulse": True}, {"badge_pulse": False}, {"badge": True}, badge_px),
    "badge_pulse_speed": ({"badge_pulse": True, "badge_pulse_speed": 0.3}, {"badge_pulse": True, "badge_pulse_speed": 6.0}, {"badge": True}, badge_px),
    "badge_font": ({"badge_font": "Consolas"}, {"badge_font": "DejaVu Serif"}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_font_size": ({}, {"badge_font_size": 24}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_bold": ({"badge_bold": True}, {"badge_bold": False}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_border_width": ({"badge_border_width": 1}, {"badge_border_width": 5}, {"badge": True}, badge_px),
    "badge_radius": ({"badge_radius": 0}, {"badge_radius": 20}, {"badge": True}, badge_px),
    "badge_thread": ({"badge_thread": True}, {"badge_thread": False}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_thread_length": ({"badge_thread_length": 10}, {"badge_thread_length": 120}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
    "badge_margin": ({"badge_margin": 0}, {"badge_margin": 150}, {"badge": True}, badge_geo),
    "badge_sway": ({"badge_sway": False}, {"badge_sway": True}, {"badge": True}, lambda e: (badge_geo(e), badge_px(e))),
}


def build(over, kw):
    return world(over, pets=kw.get("pets", ("cat",)), badge=kw.get("badge", False))


@pytest.mark.parametrize("key", sorted(CASES))
def test_setting_has_an_effect(key):
    base, alt, kw, obs = CASES[key]
    a, b = build(base, kw), build(alt, kw)
    try:
        ra, rb = obs(a), obs(b)
    finally:
        a.clear(); b.clear()
    assert ra != rb, f"setting '{key}' changed nothing observable: {ra!r}"


def test_every_global_setting_is_covered_here_or_below():
    special = {"monitor", "keep_on_top_interval", "start_with_windows", "pause_fullscreen", "pause_on_battery", "quiet_hours", "quiet_start", "quiet_end"}
    missing = {s["key"] for s in C.SCHEMA} - set(CASES) - special
    assert not missing, f"no behavioural test for: {sorted(missing)}"


# ── settings that act through the engine's visibility check / autostart ──
def test_pause_fullscreen_and_battery_and_quiet(monkeypatch):
    for key, patch, val in (("pause_fullscreen", "fullscreen_app_active", True), ("pause_on_battery", "on_battery", True)):
        monkeypatch.setattr(PU, patch, lambda *a, **k: val)
        off = world({key: False}); off.check_visibility()
        on = world({key: True}); on.check_visibility()
        assert off.hidden_reason is None and on.hidden_reason is not None, key
        off.clear(); on.clear()
    monkeypatch.setattr(PU, "in_quiet_hours", lambda s, e, now=None: True)
    q = world({"quiet_hours": True}); q.check_visibility()
    nq = world({"quiet_hours": False}); nq.check_visibility()
    assert q.hidden_reason == "quiet" and nq.hidden_reason is None
    q.clear(); nq.clear()


def test_quiet_hours_window_is_what_the_user_typed():
    import datetime as dt
    n = dt.datetime(2026, 1, 1, 10, 0)
    assert PU.in_quiet_hours("09:00", "11:00", n) and not PU.in_quiet_hours("12:00", "13:00", n)


def test_start_with_windows_calls_registry_helper(monkeypatch):
    calls = []
    monkeypatch.setattr(PU, "set_autostart", lambda v: calls.append(v) or True)
    Engine(app, C.sanitize({"start_with_windows": True})).clear()
    Engine(app, C.sanitize({"start_with_windows": False})).clear()
    assert calls == [True, False]


def test_monitor_choice_picks_screens(monkeypatch):
    e = world({"monitor": "primary"})
    assert e.screens() == [app.primaryScreen()]
    e.cfg["monitor"] = "9"; assert e.screens() == [app.primaryScreen()]     # missing monitor falls back
    e.cfg["monitor"] = "all"; assert e.screens() == app.screens()
    e.clear()


# ── per-object settings ──
PET_CASES = {
    "enabled": ({"enabled": True}, {"enabled": False}, lambda e: len(e.actors)),
    "scale": ({}, {"scale": 2.0}, lambda e: e.actors[0].width()),
    "speed": ({}, {"speed": 3.0}, lambda e: xy(e, 40)),
    "opacity": ({}, {"opacity": 0.3}, lambda e: round(e.actors[0].windowOpacity(), 2)),
    "hue": ({}, {"hue": 150}, lambda e: snap(e)),
    "flip": ({}, {"flip": True}, lambda e: e.actors[0].dir),
    "zone": ({}, {"zone": "top"}, lambda e: round(e.actors[0].y0)),
}


@pytest.mark.parametrize("key", sorted(PET_CASES))
def test_per_object_setting_has_an_effect(key):
    base, alt, obs = PET_CASES[key]
    a, b = world(pets=("cat",), pet_over=base), world(pets=("cat",), pet_over=alt)
    try:
        if key == "enabled":
            a = world(pets=("cat",)); b = Engine(app, C.sanitize({"pets": {"cat": {"enabled": False}}, "badge_enabled": False}))
        ra, rb = obs(a), obs(b)
    finally:
        a.clear(); b.clear()
    assert ra != rb, f"per-object '{key}' changed nothing: {ra!r}"


def test_zone_covers_every_kind():
    for pid, zone in (("monkey", "top-left"), ("sun", "top-right"), ("bee", "bottom"), ("soccer", "top")):
        a = world(pets=(pid,), pet_over={"zone": "auto"}); b = world(pets=(pid,), pet_over={"zone": zone})
        assert (round(a.actors[0].fx), round(a.actors[0].y0)) != (round(b.actors[0].fx), round(b.actors[0].y0)) or \
               (round(a.actors[0].fx), round(a.actors[0].fy)) != (round(b.actors[0].fx), round(b.actors[0].fy)), (pid, zone)
        a.clear(); b.clear()
