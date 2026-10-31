"""Settings schema + persistence. Every customisation is declared once in SCHEMA;
the settings window is generated from it, so adding a setting = adding one line."""
import json, os, sys, copy

APP_NAME = "King Animated Desktop"
VERSION = "1.0.1"


def S(key, label, typ, default, group, lo=None, hi=None, choices=None, tip=""):
    return dict(key=key, label=label, type=typ, default=default, group=group,
                min=lo, max=hi, choices=choices, tip=tip)


CORNERS = ["top-right", "top-left", "bottom-right", "bottom-left"]

SCHEMA = [
    # ── General ──────────────────────────────────────────────
    S("enabled", "Pets enabled", "bool", True, "General"),
    S("theme", "Settings window theme", "choice", "pitch-black", "General",
      choices=["pitch-black", "white", "system"]),
    S("ui_accent", "Settings window accent colour", "color", "#00ffd0", "General"),
    S("start_with_windows", "Start with Windows", "bool", True, "General"),
    S("fps", "Frame rate", "choice", 60, "General", choices=[30, 45, 60]),
    S("monitor", "Monitor (all = spread pets across screens)", "choice", "primary", "General",
      choices=["primary", "all", "1", "2", "3"]),
    S("always_on_top", "Always on top", "bool", True, "General"),
    S("click_through", "Click-through (never blocks your mouse)", "bool", True, "General"),
    S("pause_fullscreen", "Hide while a full-screen app/game is active (off = show over everything)", "bool", False, "General"),
    S("keep_on_top_interval", "Re-assert on-top every (seconds)", "int", 1, "General", 1, 30),
    S("pause_on_battery", "Hide when running on battery", "bool", False, "General"),
    S("quiet_hours", "Enable quiet hours (pets hidden)", "bool", False, "General"),
    S("quiet_start", "Quiet hours start (HH:MM)", "time", "23:00", "General"),
    S("quiet_end", "Quiet hours end (HH:MM)", "time", "07:00", "General"),
    S("global_scale", "Global size multiplier", "float", 1.0, "General", 0.3, 3.0),
    S("global_speed", "Global speed multiplier", "float", 1.0, "General", 0.1, 4.0),
    S("global_opacity", "Global opacity", "float", 1.0, "General", 0.1, 1.0),
    S("max_active", "Max pets on screen at once", "int", 20, "General", 1, 80),
    # ── Appearance ───────────────────────────────────────────
    S("hue_shift", "Hue shift (degrees)", "int", 0, "Appearance", 0, 360),
    S("saturation", "Saturation", "float", 1.0, "Appearance", 0.0, 2.0),
    S("brightness", "Brightness", "float", 1.0, "Appearance", 0.4, 1.6),
    S("grayscale", "Grayscale", "bool", False, "Appearance"),
    S("rainbow", "Rainbow mode (colours cycle)", "bool", False, "Appearance"),
    S("rainbow_speed", "Rainbow speed", "float", 0.15, "Appearance", 0.02, 1.0),
    S("outline", "Outline style", "choice", "auto", "Appearance",
      choices=["auto", "none", "black", "white"]),
    S("shadow", "Ground shadow", "bool", True, "Appearance"),
    S("shadow_opacity", "Shadow opacity", "float", 0.25, "Appearance", 0.0, 1.0),
    S("mirror_all", "Mirror all pets", "bool", False, "Appearance"),
    S("smooth", "Anti-aliasing (smooth edges)", "bool", True, "Appearance"),
    # ── Behaviour ────────────────────────────────────────────
    S("random_turn", "Pets turn around randomly", "bool", True, "Behaviour"),
    S("turn_chance", "Turn chance per second", "float", 0.05, "Behaviour", 0.0, 1.0),
    S("random_pause", "Pets stop and rest randomly", "bool", True, "Behaviour"),
    S("pause_chance", "Rest chance per second", "float", 0.06, "Behaviour", 0.0, 1.0),
    S("pause_length", "Rest length (seconds)", "float", 2.0, "Behaviour", 0.5, 10.0),
    S("edge_margin", "Walk past screen edge by (px)", "int", 0, "Behaviour", -200, 300),
    S("bottom_offset", "Lift ground pets above the bottom (px)", "int", 0, "Behaviour", 0, 500),
    S("top_offset", "Push top items down (px)", "int", 0, "Behaviour", 0, 500),
    S("walk_speed", "Walking speed (px/s)", "int", 70, "Behaviour", 10, 500),
    S("fly_speed", "Flying speed (px/s)", "int", 110, "Behaviour", 20, 700),
    S("float_speed", "Floating speed (px/s)", "int", 40, "Behaviour", 10, 300),
    S("fall_speed", "Falling speed (px/s)", "int", 70, "Behaviour", 20, 500),
    S("bounce_height", "Bounce height (px)", "int", 140, "Behaviour", 20, 500),
    S("hop_height", "Hop height (px)", "int", 14, "Behaviour", 0, 100),
    S("swing_speed", "Swing speed", "float", 0.9, "Behaviour", 0.2, 3.0),
    S("swing_amplitude", "Swing width (radians)", "float", 0.65, "Behaviour", 0.1, 1.2),
    S("swing_rope", "Swing rope length (px)", "int", 200, "Behaviour", 80, 600),
    S("fly_wobble", "Flying wobble (px)", "int", 18, "Behaviour", 0, 120),
    S("fall_sway", "Floating/falling sway (px)", "int", 24, "Behaviour", 0, 150),
    S("spread_lanes", "Spread flyers over different heights", "bool", True, "Behaviour"),
    # ── Badge ────────────────────────────────────────────────
    S("badge_enabled", "Show neon badge", "bool", True, "Badge"),
    S("badge_text", "Badge text", "text", "TeamExyKings", "Badge"),
    S("badge_corner", "Badge corner", "choice", "top-right", "Badge", choices=CORNERS),
    S("badge_color", "Neon colour", "color", "#00ffd0", "Badge"),
    S("badge_bg_color", "Badge background", "color", "#08080c", "Badge"),
    S("badge_bg_opacity", "Background opacity", "float", 0.92, "Badge", 0.0, 1.0),
    S("badge_glow", "Glow", "bool", True, "Badge"),
    S("badge_glow_strength", "Glow strength", "int", 5, "Badge", 1, 10),
    S("badge_pulse", "Pulse", "bool", True, "Badge"),
    S("badge_pulse_speed", "Pulse speed", "float", 2.5, "Badge", 0.2, 8.0),
    S("badge_font", "Font", "text", "Consolas", "Badge"),
    S("badge_font_size", "Font size", "int", 11, "Badge", 7, 40),
    S("badge_bold", "Bold text", "bool", True, "Badge"),
    S("badge_border_width", "Border width (px)", "int", 1, "Badge", 1, 6),
    S("badge_radius", "Corner radius", "int", 4, "Badge", 0, 30),
    S("badge_thread", "Hanging thread (top corners)", "bool", True, "Badge"),
    S("badge_thread_length", "Thread length (px)", "int", 26, "Badge", 0, 300),
    S("badge_margin", "Distance from screen edge (px)", "int", 16, "Badge", 0, 300),
    S("badge_sway", "Gentle sway", "bool", False, "Badge"),
]

ZONES = ["auto", "top", "middle", "bottom", "top-left", "top-right",
         "bottom-left", "bottom-right"]
PET_SCHEMA = [
    S("enabled", "Show this object", "bool", False, "Pet"),
    S("scale", "Size", "float", 1.0, "Pet", 0.3, 3.0),
    S("speed", "Speed", "float", 1.0, "Pet", 0.1, 4.0),
    S("opacity", "Opacity", "float", 1.0, "Pet", 0.1, 1.0),
    S("hue", "Hue shift", "int", 0, "Pet", 0, 360),
    S("flip", "Face the other way", "bool", False, "Pet"),
    S("zone", "Where (lane / corner)", "choice", "auto", "Pet", choices=ZONES),
]

ANCHORS = ["top-left", "top-center", "top-right", "middle-left", "center", "middle-right",
           "bottom-left", "bottom-center", "bottom-right", "custom"]
TEXT_ANIMS = ["none", "pulse", "float", "bounce", "shake", "blink", "wave", "rainbow", "spin", "typewriter",
              "marquee-left", "marquee-right", "rise", "fall", "walk", "fly"]
TEXT_STYLES = ["none", "pill", "neon-box", "sticker", "underline"]

TEXT_SCHEMA = [
    S("enabled", "Show this text", "bool", True, "Text"),
    S("text", "Text", "text", "Hello!", "Text"),
    S("font", "Font", "text", "Segoe UI", "Text"),
    S("font_size", "Font size", "int", 28, "Text", 8, 200),
    S("bold", "Bold", "bool", True, "Text"),
    S("italic", "Italic", "bool", False, "Text"),
    S("color", "Text colour", "color", "#00ffd0", "Text"),
    S("outline", "Black outline on text", "bool", False, "Text"),
    S("glow", "Neon glow", "bool", True, "Text"),
    S("glow_strength", "Glow strength", "int", 4, "Text", 1, 10),
    S("style", "Box style", "choice", "none", "Text", choices=TEXT_STYLES),
    S("bg_color", "Box colour", "color", "#08080c", "Text"),
    S("bg_opacity", "Box opacity", "float", 0.92, "Text", 0.0, 1.0),
    S("border_width", "Border width (px)", "int", 2, "Text", 1, 10),
    S("radius", "Corner radius", "int", 8, "Text", 0, 60),
    S("opacity", "Opacity", "float", 1.0, "Text", 0.1, 1.0),
    S("scale", "Size multiplier", "float", 1.0, "Text", 0.3, 4.0),
    S("anchor", "Position", "choice", "top-center", "Position", choices=ANCHORS),
    S("x_pct", "Custom X (% of screen width)", "int", 50, "Position", 0, 100),
    S("y_pct", "Custom Y (% of screen height)", "int", 50, "Position", 0, 100),
    S("offset_x", "Nudge X (px)", "int", 0, "Position", -3000, 3000),
    S("offset_y", "Nudge Y (px)", "int", 0, "Position", -3000, 3000),
    S("monitor", "Monitor", "choice", "primary", "Position", choices=["primary", "2", "3", "4"]),
    S("animation", "Animation", "choice", "none", "Animation", choices=TEXT_ANIMS),
    S("anim_speed", "Animation speed", "float", 1.0, "Animation", 0.1, 5.0),
    S("anim_range", "Animation range (px)", "int", 30, "Animation", 0, 800),
    S("swing", "Hang from a thread and swing", "bool", False, "Swing"),
    S("swing_rope", "Thread length (px)", "int", 120, "Swing", 20, 900),
    S("swing_amp", "Swing width (radians)", "float", 0.5, "Swing", 0.05, 1.2),
    S("swing_speed", "Swing speed", "float", 1.0, "Swing", 0.1, 4.0),
    S("thread_color", "Thread colour", "color", "#dddddd", "Swing"),
]
TEXT_DEFAULTS = {s["key"]: s["default"] for s in TEXT_SCHEMA}
MAX_TEXTS = 20

TEXT_TEMPLATES = {
    "Neon sign - hangs and swings": dict(text="OPEN", style="neon-box", swing=True, anchor="top-center", font_size=34),
    "Scrolling ticker": dict(text="Welcome to TeamExyKings!", animation="marquee-left", anchor="bottom-center",
                             style="pill", font_size=22, glow=False, anim_speed=1.2),
    "Floating greeting": dict(text="Hello!", animation="float", anchor="middle-left", font_size=40),
    "Corner name tag": dict(text="TeamExyKings", style="neon-box", anchor="bottom-right", font_size=16, animation="pulse"),
    "Rainbow wave": dict(text="Have a great day", animation="wave", anchor="center", font_size=46, glow=False),
    "Falling confetti word": dict(text="PARTY", animation="fall", anchor="custom", x_pct=30, font_size=30),
    "Walking banner": dict(text="Back soon", animation="walk", anchor="bottom-center", style="sticker", color="#ffffff",
                           bg_color="#e8402a", font_size=20, glow=False),
    "Typewriter quote": dict(text="Code. Ship. Repeat.", animation="typewriter", anchor="top-left", font_size=24),
}

DEFAULT_ENABLED = ["spiderman", "lab_yellow"]
DEFAULTS = {s["key"]: s["default"] for s in SCHEMA}
PET_DEFAULTS = {s["key"]: s["default"] for s in PET_SCHEMA}
BY_KEY = {s["key"]: s for s in SCHEMA}


def config_path():
    env = os.environ.get("KINGDESKTOP_CONFIG")
    if env:
        return env
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "KingAnimatedDesktop", "config.json")
    return os.path.join(os.path.expanduser("~"), ".config", "king-animated-desktop", "config.json")


def _coerce(spec, v):
    t = spec["type"]
    try:
        if t == "bool":
            return bool(v)
        if t == "int":
            v = int(round(float(v)))
        elif t == "float":
            v = float(v)
        elif t == "choice":
            ch = spec["choices"]
            for c in ch:                       # accept "60" for 60 etc.
                if str(c) == str(v):
                    return c
            return spec["default"]
        else:
            return str(v)
        if spec["min"] is not None: v = max(spec["min"], v)
        if spec["max"] is not None: v = min(spec["max"], v)
        return v
    except Exception:
        return spec["default"]


def sanitize(raw):
    cfg = copy.deepcopy(DEFAULTS)
    raw = raw if isinstance(raw, dict) else {}
    for s in SCHEMA:
        if s["key"] in raw:
            cfg[s["key"]] = _coerce(s, raw[s["key"]])
    pets = {}
    rp = raw.get("pets") if isinstance(raw.get("pets"), dict) else None
    if rp is None:                                     # first run
        rp = {pid: {"enabled": True} for pid in DEFAULT_ENABLED}
    for pid, d in rp.items():
        if not isinstance(d, dict):
            continue
        pets[pid] = {s["key"]: _coerce(s, d.get(s["key"], s["default"])) for s in PET_SCHEMA}
    cfg["pets"] = pets
    texts = []
    rt = raw.get("texts")
    for d in (rt if isinstance(rt, list) else [])[:MAX_TEXTS]:
        if isinstance(d, dict):
            texts.append({s["key"]: _coerce(s, d.get(s["key"], s["default"])) for s in TEXT_SCHEMA})
    cfg["texts"] = texts
    return cfg


def pet_cfg(cfg, pid):
    return cfg["pets"].get(pid) or dict(PET_DEFAULTS)


def load(path=None):
    path = path or config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sanitize(json.load(f))
    except Exception:
        return sanitize({})


def save(cfg, path=None):
    path = path or config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def customisation_count(n_objects):
    return n_objects + len(SCHEMA) + len(PET_SCHEMA) * n_objects + len(TEXT_SCHEMA)
