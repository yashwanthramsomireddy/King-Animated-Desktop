"""Tiny vector-sprite renderer. Sprites are lists of shape tuples in a 100x100 box:

  ("e", cx, cy, rx, ry, fill)            ellipse
  ("r", x, y, w, h, fill, radius)        rounded rectangle
  ("l", x1, y1, x2, y2, color, width)    line (round caps)
  ("p", [(x,y),...], fill)               polygon
  ("a", cx, cy, rx, ry, start, span, color, width)   arc (degrees)
  ("t", x, y, "text", color, size)       text
  ("anim", mode, (px,py), amp, speed, [shapes...])   animated group
        modes: rot | scaley | scalex | spin | pulse

Colours are "#rrggbb" or ("#rrggbb", alpha 0..1)."""
import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QPolygonF, QFont


class Ctx:
    def __init__(self, t=0.0, dir=1, hue=0, sat=1.0, bri=1.0, gray=False,
                 outline="auto", shadow=True, shadow_op=0.25, W=100, H=100,
                 rope=200, ang=0.0, rot=0.0, gait=0.0, hop=0.0):
        self.t, self.dir, self.hue, self.sat, self.bri, self.gray = t, dir, hue, sat, bri, gray
        self.outline, self.shadow, self.shadow_op = outline, shadow, shadow_op
        self.W, self.H, self.rope, self.ang, self.rot, self.gait, self.hop = W, H, rope, ang, rot, gait, hop

    def c(self, col):
        alpha = 1.0
        if isinstance(col, (tuple, list)):
            col, alpha = col
        q = QColor(col)
        h, s, l, _ = q.getHslF()
        if h >= 0 and s > 0.02 and self.hue:
            h = (h + self.hue / 360.0) % 1.0
        if self.gray:
            s = 0.0
        s = max(0.0, min(1.0, s * self.sat))
        l = max(0.0, min(1.0, l * self.bri))
        out = QColor.fromHslF(max(h, 0.0), s, l, alpha)
        return out

    def pen(self, brush_color):
        m = self.outline
        if m == "none":
            return QPen(Qt.NoPen)
        if m == "black":
            return QPen(QColor("#111111"), 1.3)
        if m == "white":
            return QPen(QColor("#ffffff"), 1.3)
        return QPen(brush_color.darker(160), 1.2)


def _line(p, ctx, x1, y1, x2, y2, col, w):
    pen = QPen(ctx.c(col), w)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def draw_shapes(p, shapes, ctx):
    for sh in shapes:
        op = sh[0]
        if op == "e":
            _, cx, cy, rx, ry, fill = sh
            b = ctx.c(fill)
            p.setBrush(b); p.setPen(ctx.pen(b))
            p.drawEllipse(QPointF(cx, cy), rx, ry)
        elif op == "r":
            _, x, y, w, h, fill, rad = sh
            b = ctx.c(fill)
            p.setBrush(b); p.setPen(ctx.pen(b))
            p.drawRoundedRect(QRectF(x, y, w, h), rad, rad)
        elif op == "l":
            _line(p, ctx, *sh[1:])
        elif op == "p":
            _, pts, fill = sh
            b = ctx.c(fill)
            p.setBrush(b); p.setPen(ctx.pen(b))
            p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
        elif op == "a":
            _, cx, cy, rx, ry, st, sp, col, w = sh
            pen = QPen(ctx.c(col), w); pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawArc(QRectF(cx - rx, cy - ry, 2 * rx, 2 * ry), int(st * 16), int(sp * 16))
        elif op == "t":
            _, x, y, txt, col, size = sh
            f = QFont("Arial"); f.setPixelSize(int(size)); f.setBold(True)
            p.setFont(f); p.setPen(ctx.c(col))
            p.drawText(QRectF(x - 50, y - size, 100, size * 2), Qt.AlignCenter, txt)
        elif op == "anim":
            _, mode, (px, py), amp, speed, sub = sh
            p.save()
            p.translate(px, py)
            a = math.sin(ctx.t * speed)
            if mode == "rot":
                p.rotate(amp * a)
            elif mode == "spin":
                p.rotate(math.degrees(ctx.t * speed) % 360)
            elif mode == "scaley":
                p.scale(1, 1 - amp * abs(a))
            elif mode == "scalex":
                p.scale(1 - amp * abs(a), 1)
            elif mode == "pulse":
                s = 1 + amp * a
                p.scale(s, s)
            p.translate(-px, -py)
            draw_shapes(p, sub, ctx)
            p.restore()


def draw_legs(p, legs, ctx):
    """legs = (color, [(x, y_top), ...], length, width). Alternating gait."""
    color, pts, length, width = legs
    for i, (x, y) in enumerate(pts):
        swing = math.sin(ctx.gait * 6 + (math.pi if i % 2 else 0)) * 6
        lift = max(0.0, math.sin(ctx.gait * 6 + (math.pi if i % 2 else 0))) * 3
        _line(p, ctx, x, y, x + swing, y + length - lift, color, width)


def draw_shadow(p, ctx, cx=50, cy=97, rx=32, ry=4):
    if not ctx.shadow:
        return
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, int(255 * ctx.shadow_op)))
    p.drawEllipse(QPointF(cx, cy), rx, ry)
