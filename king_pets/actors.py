"""One transparent, click-through window per object (pet / badge)."""
import zlib
import math, random
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QPainterPath
from PySide6.QtWidgets import QWidget

from .render import Ctx, draw_shapes, draw_legs, draw_shadow, _line
from .config import pet_cfg


class OverlayWindow(QWidget):
    def __init__(self, cfg):
        super().__init__()
        flags = Qt.FramelessWindowHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        if cfg["always_on_top"]:
            flags |= Qt.WindowStaysOnTopHint
        if cfg["click_through"]:
            flags |= Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        if cfg["click_through"]:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)


def zone_lane(zone):
    return {"top": 0.0, "middle": 0.5, "bottom": 1.0}.get(zone.split("-")[0] if "-" in zone else zone, None)


class PetActor(OverlayWindow):
    PAD = 22          # extra logical room for rotating "fall" sprites

    def __init__(self, spec, cfg, screen, index=0):
        super().__init__(cfg)
        self.spec, self.cfg, self.index = spec, cfg, index
        pc = pet_cfg(cfg, spec.id)
        self.pc = pc
        self.s = pc["scale"] * cfg["global_scale"]
        self.spd = pc["speed"] * cfg["global_speed"]
        self.kind = spec.kind
        self.geo = screen.geometry()
        self.avail = screen.availableGeometry()
        self.rng = random.Random(zlib.crc32(f"{spec.id}:{index}".encode()))
        self.t = self.rng.random() * 10
        self.gait = 0.0
        self.rot = 0.0
        self.dir = 1 if (pc["flip"] != cfg["mirror_all"]) else -1   # default: start right, walk left
        self.rest_until = 0.0
        self.now = 0.0
        self.moving = True
        self.rope = cfg["swing_rope"]

        # logical (unscaled) size
        if self.kind == "swing":
            amp = cfg["swing_amplitude"]
            self.LW = int(2 * (self.rope * math.sin(min(amp, 1.2)) + 70))
            self.LH = int(self.rope + 120)
            self.off = (0, 0)
        elif self.kind == "fall":
            self.LW = spec.w + 2 * self.PAD
            self.LH = spec.h + 2 * self.PAD
            self.off = (self.PAD, self.PAD)
        else:
            self.LW, self.LH = spec.w, spec.h
            self.off = (0, 0)
        self.resize(int(self.LW * self.s) + 1, int(self.LH * self.s) + 1)
        self.setWindowOpacity(pc["opacity"] * cfg["global_opacity"])
        self._place_initial()

    # ── geometry helpers ──
    @property
    def Wp(self): return self.width()
    @property
    def Hp(self): return self.height()

    def _lane_y(self):
        c, z = self.cfg, self.pc["zone"]
        lane = zone_lane(z)
        if lane is None or z == "auto":
            lane = 1.0 if self.kind in ("walk", "hop", "bounce") else None
        top = self.geo.top() + c["top_offset"]
        bot = self.avail.bottom() - self.Hp + 1 - c["bottom_offset"]
        if self.kind in ("walk", "hop", "bounce"):
            return top + (bot - top) * (lane if lane is not None else 1.0)
        if self.kind == "fly":
            if z == "auto":
                frac = (0.10 + (self.index * 0.137 + (sum(map(ord, self.spec.id)) % 7) * 0.05) % 0.5) \
                    if c["spread_lanes"] else 0.15
            else:
                frac = {0.0: 0.12, 0.5: 0.45, 1.0: 0.8}[lane]
            return top + frac * (bot - top)
        return top

    def _swing_x(self):
        z = self.pc["zone"]
        if "left" in z: return self.geo.left() + 8
        if "right" in z: return self.geo.right() - self.Wp - 8
        return self.geo.left() + (self.geo.width() - self.Wp) // 2

    def _corner(self):
        z = self.pc["zone"]
        corner = z if "-" in z and z.split("-")[0] in ("top", "bottom") else None
        if corner is None:
            corner = ["bottom-left", "top-left", "bottom-right"][sum(map(ord, self.spec.id)) % 3]
        m = 14
        x = self.geo.left() + m if "left" in corner else self.geo.right() - self.Wp - m
        y = self.geo.top() + self.cfg["top_offset"] + m if "top" in corner else self.avail.bottom() - self.Hp - m
        return x, y

    def _place_initial(self):
        g, k = self.geo, self.kind
        self.y0 = self._lane_y()
        if k == "swing":
            self.fx = self._swing_x(); self.fy = g.top() + self.cfg["top_offset"]
        elif k == "idle":
            self.fx, self.fy = self._corner()
        elif k == "float":
            self.x0 = self.rng.uniform(g.left(), g.right() - self.Wp)
            self.fx, self.fy = self.x0, self.rng.uniform(g.top(), g.bottom())
        elif k == "fall":
            self.x0 = self.rng.uniform(g.left(), g.right() - self.Wp)
            self.fx, self.fy = self.x0, self.rng.uniform(g.top() - self.Hp, g.bottom())
        else:
            right_start = "right" in self.pc["zone"] or self.pc["zone"] == "auto"
            span = g.width() - self.Wp
            self.fx = g.left() + (span * (0.85 if right_start else 0.15)) + self.rng.uniform(-60, 60)
            self.fy = self.y0
        self.move(int(self.fx), int(self.fy))

    # ── simulation ──
    def step(self, dt):
        c, k = self.cfg, self.kind
        self.now += dt
        self.t += dt * self.spd
        g = self.geo
        if k in ("swing", "idle"):
            return
        mg = c["edge_margin"]
        if k in ("walk", "hop", "bounce", "fly"):
            if self.now >= self.rest_until:
                self.moving = True
                if c["random_pause"] and k in ("walk", "hop") and self.rng.random() < c["pause_chance"] * dt:
                    self.moving = False
                    self.rest_until = self.now + c["pause_length"] * self.rng.uniform(0.6, 1.4)
            else:
                self.moving = False
            if c["random_turn"] and self.rng.random() < c["turn_chance"] * dt:
                self.dir *= -1
            sp = {"walk": c["walk_speed"], "hop": c["walk_speed"] * 1.1, "bounce": c["walk_speed"] * 1.3,
                  "fly": c["fly_speed"]}[k] * self.spd
            if self.moving:
                self.fx += self.dir * sp * dt
                self.gait += dt * self.spd
            lo, hi = g.left() - mg, g.right() - self.Wp + mg
            if self.fx < lo: self.fx, self.dir = lo, 1
            if self.fx > hi: self.fx, self.dir = hi, -1
            y = self.y0
            if k == "hop":
                y -= abs(math.sin(self.t * 5)) * c["hop_height"] * self.s
            elif k == "bounce":
                y -= abs(math.sin(self.t * 2.2)) * c["bounce_height"] * self.s
            elif k == "fly":
                y += math.sin(self.t * 1.6 + self.index) * c["fly_wobble"] * self.s
            self.fy = y
        elif k == "float":
            self.fy -= c["float_speed"] * self.spd * dt
            self.fx = self.x0 + math.sin(self.t * 0.9) * c["fall_sway"] * self.s
            if self.fy < g.top() - self.Hp:
                self.fy = g.bottom() + 5
                self.x0 = self.rng.uniform(g.left(), g.right() - self.Wp)
        elif k == "fall":
            self.fy += c["fall_speed"] * self.spd * dt
            self.fx = self.x0 + math.sin(self.t * 1.1) * c["fall_sway"] * self.s
            self.rot = math.sin(self.t * 1.1) * 35
            if self.fy > g.bottom():
                self.fy = g.top() - self.Hp
                self.x0 = self.rng.uniform(g.left(), g.right() - self.Wp)
        self.move(int(self.fx), int(self.fy))

    # ── drawing ──
    def make_ctx(self, hue_extra=0.0):
        c = self.cfg
        return Ctx(t=self.t, dir=self.dir, hue=(self.pc["hue"] + c["hue_shift"] + hue_extra) % 360,
                   sat=c["saturation"], bri=c["brightness"], gray=c["grayscale"],
                   outline=c["outline"], shadow=c["shadow"], shadow_op=c["shadow_opacity"],
                   W=self.LW, H=self.LH, rope=self.rope,
                   ang=math.sin(self.t * c["swing_speed"]) * c["swing_amplitude"],
                   rot=self.rot, gait=self.gait)

    hue_extra = 0.0

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, self.cfg["smooth"])
        p.scale(self.s, self.s)
        paint_sprite(p, self.spec, self.make_ctx(self.hue_extra), self.off, self.dir)


def paint_sprite(p, spec, ctx, off=(0, 0), direction=1):
    """Shared by live windows, previews and tests."""
    k = spec.kind
    if k == "swing":
        if spec.custom:
            spec.custom(p, ctx)
            return
        p.save()
        p.translate(ctx.W / 2, 0)
        p.rotate(math.degrees(ctx.ang))
        _line(p, ctx, 0, 0, 0, ctx.rope + 4, "#dddddd", 1.5)
        p.translate(-50, ctx.rope)
        draw_shapes(p, spec.shapes, ctx)
        p.restore()
        return
    p.save()
    p.translate(*off)
    if k == "fall":
        p.translate(spec.w / 2, spec.h / 2); p.rotate(ctx.rot); p.translate(-spec.w / 2, -spec.h / 2)
    if direction < 0 and k != "fall":
        p.translate(spec.w, 0); p.scale(-1, 1)
    if spec.ground:
        draw_shadow(p, ctx, spec.w / 2, spec.h - 4, spec.w * 0.34, 4 if spec.h < 120 else 5)
    if spec.custom:
        spec.custom(p, ctx)
    else:
        if spec.legs:
            from .render import draw_legs
            draw_legs(p, spec.legs, ctx)
        draw_shapes(p, spec.shapes, ctx)
    p.restore()


class BadgeActor(OverlayWindow):
    def __init__(self, cfg, screen):
        super().__init__(cfg)
        self.cfg = cfg
        self.geo = screen.geometry()
        self.t = 0.0
        f = self._font()
        fm = QFontMetrics(f)
        self.tw = fm.horizontalAdvance(cfg["badge_text"] or " ")
        self.bw = self.tw + 28
        self.bh = f.pointSize() * 2 + 12
        self.top = cfg["badge_corner"].startswith("top")
        self.thread = cfg["badge_thread_length"] if (cfg["badge_thread"] and self.top) else 0
        self.pad = 14
        W = self.bw + 2 * self.pad + (40 if cfg["badge_sway"] else 0)
        H = self.thread + self.bh + 2 * self.pad
        self.resize(W, H)
        m = cfg["badge_margin"]
        self.move(self.geo.right() - W - m + 1 if "right" in cfg["badge_corner"] else self.geo.left() + m,
                  self.geo.top() if self.top else self.geo.bottom() - H - m + 1)
        self.setWindowOpacity(cfg["global_opacity"])

    def _font(self):
        f = QFont(self.cfg["badge_font"] or "Consolas")
        f.setPointSize(self.cfg["badge_font_size"]); f.setBold(self.cfg["badge_bold"])
        return f

    def step(self, dt):
        self.t += dt

    def paintEvent(self, _):
        c = self.cfg
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, c["smooth"])
        base = QColor(c["badge_color"])
        pulse = (0.5 + 0.5 * math.sin(self.t * c["badge_pulse_speed"])) if c["badge_pulse"] else 1.0
        neon = QColor(base)
        white = QColor("#ffffff")
        mix = 0.28 * pulse
        neon = QColor(int(base.red() + (255 - base.red()) * mix), int(base.green() + (255 - base.green()) * mix),
                      int(base.blue() + (255 - base.blue()) * mix))
        if c["badge_sway"]:
            p.translate(self.width() / 2, 0); p.rotate(math.sin(self.t * 1.2) * 3); p.translate(-self.width() / 2, 0)
        cx = self.width() / 2
        if self.thread:
            pen = QPen(neon, 1); p.setPen(pen)
            p.drawLine(QPointF(cx, 0), QPointF(cx, self.thread))
        rect = QRectF(cx - self.bw / 2, self.thread + (0 if self.top else 0) + (self.pad if not self.top else 0),
                      self.bw, self.bh)
        if self.top and self.thread == 0:
            rect.moveTop(self.pad)
        r = c["badge_radius"]
        if c["badge_glow"]:
            for i in range(c["badge_glow_strength"], 0, -1):
                g = QColor(neon); g.setAlpha(int(70 / i * (0.5 + 0.5 * pulse)))
                p.setPen(QPen(g, c["badge_border_width"] + i * 1.6)); p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(rect, r, r)
        bg = QColor(c["badge_bg_color"]); bg.setAlphaF(c["badge_bg_opacity"])
        p.setPen(QPen(neon, c["badge_border_width"])); p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font()); p.setPen(neon)
        p.drawText(rect, Qt.AlignCenter, c["badge_text"])


# ───────────────────────── custom text ─────────────────────────
IN_PLACE = {"pulse", "float", "bounce", "shake", "blink", "wave", "rainbow", "spin", "typewriter", "none"}
MOTION = {"marquee-left", "marquee-right", "rise", "fall", "walk", "fly"}


class TextActor(OverlayWindow):
    """User-defined text: any font/colour/box style, anchored anywhere, with an animation and/or a swing."""
    def __init__(self, tc, cfg, screen, index=0):
        super().__init__(cfg)
        from PySide6.QtGui import QFontMetricsF
        self.tc, self.cfg, self.index = tc, cfg, index
        self.geo, self.avail = screen.geometry(), screen.availableGeometry()
        self.t = 0.0
        self.sc = tc["scale"] * cfg["global_scale"]
        f = QFont(tc["font"] or "Segoe UI"); f.setPixelSize(max(6, int(tc["font_size"] * self.sc)))
        f.setBold(tc["bold"]); f.setItalic(tc["italic"])
        self.font_ = f
        fm = QFontMetricsF(f)
        self.fm = fm
        text = tc["text"] if tc["text"] != "" else " "
        self.tw = fm.horizontalAdvance(text) + 2
        boxed = tc["style"] != "none"
        self.padx = (fm.height() * 0.6 if boxed else 4)
        self.pady = (fm.height() * 0.25 if boxed else 2)
        self.bw = self.tw + 2 * self.padx
        self.bh = fm.height() + 2 * self.pady
        glow = (tc["glow_strength"] * 2.2 + 6) if tc["glow"] or tc["style"] == "neon-box" else 6
        anim = tc["animation"]
        rng = tc["anim_range"] * self.sc if anim in ("float", "bounce", "shake") else 0
        wave = fm.height() * 0.5 if anim == "wave" else 0
        self.m = glow + max(rng, wave) + tc["border_width"]
        self.swing = tc["swing"]
        self.rope = tc["swing_rope"] * self.sc
        if self.swing:
            reach = self.rope * math.sin(min(tc["swing_amp"], 1.2)) + self.bw / 2 + self.bh
            self.W = int(2 * reach + 2 * self.m)
            self.H = int(self.rope + self.bh * 1.6 + 2 * self.m)
        else:
            self.W = int(self.bw + 2 * self.m)
            self.H = int(self.bh + 2 * self.m)
        self.resize(self.W, self.H)
        self.setWindowOpacity(tc["opacity"] * cfg["global_opacity"])
        self.dir = 1
        self.typed = 0.0
        self._place()

    # base position from the anchor
    def _place(self):
        tc, g, W, H = self.tc, self.geo, self.W, self.H
        a, edge = tc["anchor"], 16
        if a == "custom":
            x = g.left() + tc["x_pct"] / 100 * g.width() - W / 2
            y = g.top() + tc["y_pct"] / 100 * g.height() - (0 if self.swing else H / 2)
        else:
            v, h = (a.split("-") + ["center"])[:2] if "-" in a else ("middle", "center")
            if a == "center": v, h = "middle", "center"
            x = {"left": g.left() + edge, "center": g.left() + (g.width() - W) / 2, "right": g.right() - W - edge}[h]
            y = {"top": g.top() + (0 if self.swing else edge), "middle": g.top() + (g.height() - H) / 2,
                 "bottom": self.avail.bottom() - H - edge}[v]
        x += tc["offset_x"]; y += tc["offset_y"]
        if tc["animation"] not in MOTION or tc["animation"] in ("walk",):
            x = min(max(x, g.left() - 2 * W), g.right() + W)
        self.bx, self.by = x, y
        self.fx, self.fy = x, y
        if tc["animation"] in ("marquee-right",): self.fx = g.left() - W
        if tc["animation"] == "marquee-left": self.fx = g.right()
        if tc["animation"] == "fall": self.fy = g.top() - H
        if tc["animation"] == "rise": self.fy = g.bottom()
        if tc["animation"] in ("walk", "fly"): self.fx = g.left() + (g.width() - W) * 0.5
        self.move(int(self.fx), int(self.fy))

    def step(self, dt):
        tc, g = self.tc, self.geo
        sp = tc["anim_speed"] * self.cfg["global_speed"]
        self.t += dt * sp
        an = tc["animation"]
        v = 120 * sp
        if an == "marquee-left":
            self.fx -= v * dt
            if self.fx + self.W < g.left(): self.fx = g.right()
        elif an == "marquee-right":
            self.fx += v * dt
            if self.fx > g.right(): self.fx = g.left() - self.W
        elif an == "fall":
            self.fy += v * dt
            if self.fy > g.bottom(): self.fy = g.top() - self.H
        elif an == "rise":
            self.fy -= v * dt
            if self.fy + self.H < g.top(): self.fy = g.bottom()
        elif an in ("walk", "fly"):
            self.fx += self.dir * v * dt
            lo, hi = g.left(), g.right() - self.W
            if self.fx < lo: self.fx, self.dir = lo, 1
            if self.fx > hi: self.fx, self.dir = hi, -1
            self.fy = self.by + (math.sin(self.t * 1.6) * tc["anim_range"] if an == "fly" else 0)
        if an == "typewriter":
            self.typed += dt * 6 * sp
            n = len(tc["text"])
            if self.typed > n + 8: self.typed = 0.0
        if an in MOTION:
            self.move(int(self.fx), int(self.fy))

    # ── painting ──
    def _colors(self):
        tc = self.tc
        col = QColor(tc["color"])
        if tc["animation"] == "rainbow":
            col = QColor.fromHslF((self.t * 0.25) % 1.0, 1.0, 0.6)
        return col

    def paintEvent(self, _):
        tc, an, t = self.tc, self.tc["animation"], self.t
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        if an == "blink" and math.sin(t * 5) < 0:
            return
        # attach point + body offset
        if self.swing:
            ang = math.sin(self.t * tc["swing_speed"]) * tc["swing_amp"]
            px, py = self.W / 2, 0
            p.setPen(QPen(QColor(tc["thread_color"]), max(1.0, self.sc * 1.2)))
            ax = px + self.rope * math.sin(ang); ay = self.rope * math.cos(ang)
            p.drawLine(QPointF(px, py), QPointF(ax, ay))
            p.translate(ax, ay); p.rotate(math.degrees(ang)); p.translate(0, self.bh / 2)
        else:
            p.translate(self.W / 2, self.H / 2)
        rng = tc["anim_range"] * self.sc
        if an == "float":  p.translate(0, math.sin(t * 2) * rng)
        elif an == "bounce": p.translate(0, -abs(math.sin(t * 3)) * rng)
        elif an == "shake": p.translate(math.sin(t * 40) * rng * 0.25, math.cos(t * 33) * rng * 0.12)
        elif an == "pulse":
            s = 1 + 0.12 * math.sin(t * 3); p.scale(s, s)
        elif an == "spin":
            p.scale(max(0.06, abs(math.cos(t * 1.5))), 1)
        self._draw_body(p)

    def _draw_body(self, p):
        tc, an = self.tc, self.tc["animation"]
        col = self._colors()
        style = tc["style"]
        rect = QRectF(-self.bw / 2, -self.bh / 2, self.bw, self.bh)
        r = tc["radius"] * self.sc if style != "pill" else self.bh / 2
        bwid = tc["border_width"] * (1.5 if style == "sticker" else 1)
        if style in ("pill", "neon-box", "sticker"):
            if style == "neon-box" or (tc["glow"] and style == "pill"):
                for i in range(tc["glow_strength"], 0, -1):
                    g = QColor(col); g.setAlpha(int(70 / i))
                    p.setPen(QPen(g, bwid + i * 1.7)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(rect, r, r)
            bg = QColor(tc["bg_color"]); bg.setAlphaF(tc["bg_opacity"])
            p.setPen(QPen(QColor("#111111") if style == "sticker" else col, bwid)); p.setBrush(bg)
            p.drawRoundedRect(rect, r, r)
        elif style == "underline":
            y = rect.bottom() - 1
            if tc["glow"]:
                for i in range(tc["glow_strength"], 0, -1):
                    g = QColor(col); g.setAlpha(int(70 / i)); p.setPen(QPen(g, bwid + i * 1.7)); p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            p.setPen(QPen(col, bwid)); p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
        text = tc["text"]
        if an == "typewriter":
            text = text[: int(self.typed)]
        fm = self.fm
        base_y = fm.ascent() - fm.height() / 2
        x0 = -self.tw / 2 + 1
        path = QPainterPath()
        if an == "wave":
            x = x0
            for i, ch in enumerate(text):
                dy = math.sin(self.t * 4 + i * 0.7) * fm.height() * 0.25
                path.addText(QPointF(x, base_y + dy), self.font_, ch)
                x += fm.horizontalAdvance(ch)
            fillcol = col
        else:
            path.addText(QPointF(x0, base_y), self.font_, text)
            fillcol = col
        if tc["glow"] and style != "sticker":
            for i in range(tc["glow_strength"], 0, -1):
                g = QColor(fillcol); g.setAlpha(int(60 / i))
                p.setPen(QPen(g, i * 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush); p.drawPath(path)
        if tc["outline"] or style == "sticker":
            p.setPen(QPen(QColor("#000000"), max(2.0, self.sc * 3), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush); p.drawPath(path)
        p.setPen(Qt.NoPen); p.setBrush(fillcol); p.drawPath(path)
