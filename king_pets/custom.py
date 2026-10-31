"""Hand-coded characters (they need more than the shape DSL): the web-swinging hero and the Labradors."""
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen
from .render import _line
from .sprites import reg


def spiderman(p, ctx):
    """Swings from a web at the top. Window origin = pivot at (W/2, 0)."""
    px, py, rope = ctx.W / 2, 0, ctx.rope
    cx = px + rope * math.sin(ctx.ang)
    cy = py + rope * math.cos(ctx.ang)
    lean = ctx.ang * 0.55
    s, c = math.sin(lean), math.cos(lean)

    def rot(dx, dy):
        return cx + dx * c - dy * s, cy + dx * s + dy * c

    RED, BLUE, WEBP = "#e01010", "#1030d0", "#ff7070"
    L = lambda a, b, col, w: _line(p, ctx, a[0], a[1], b[0], b[1], col, w)
    L((px, py), rot(-18, -35), "#dddddd", 1.5)
    t1, t2 = rot(0, -29), rot(0, 2)
    for k, f in ((rot(-9, 18), rot(-16, 38)), (rot(11, 16), rot(19, 34))):
        L(t2, k, BLUE, 8); L(k, f, RED, 6)
    L(t1, t2, RED, 13)
    for dy in (-22, -12, -3):
        L(rot(-8, dy), rot(8, dy), WEBP, 1.2)
    L(rot(0, -29), rot(0, 2), WEBP, 1.2)
    L(rot(-11, -2), rot(11, -2), BLUE, 5)
    la, lh, ra, rh = rot(-18, -22), rot(-20, -36), rot(16, -18), rot(27, -6)
    L(t1, la, RED, 6); L(la, lh, RED, 5); L(t1, ra, RED, 6); L(ra, rh, RED, 5)
    hx, hy = rot(0, -44)
    p.setPen(QPen(ctx.c(BLUE), 2)); p.setBrush(ctx.c(RED))
    p.drawEllipse(QPointF(hx, hy), 15, 15)
    p.setPen(Qt.NoPen); p.setBrush(ctx.c("#ffffff"))
    for ox in (-5.5, 6):
        ex, ey = rot(ox, -47)
        p.drawEllipse(QPointF(ex, ey), 5, 4)


PALETTES = {
    "yellow": ("#e8b84a", "#b88418", "Yellow Labrador"),
    "black": ("#34343c", "#1c1c22", "Black Labrador"),
    "choc": ("#7a4a2c", "#523018", "Chocolate Labrador"),
}


def make_lab(pal):
    GOLD, DGOLD, _ = PALETTES[pal]

    def lab(p, ctx):
        """Walks along the bottom; logical canvas 220x150, faces right (engine flips)."""
        lt = ctx.gait
        dx, dy = 110, 50
        L = lambda x1, y1, x2, y2, col, w: _line(p, ctx, x1, y1, x2, y2, col, w)
        E = lambda x, y, rx, ry, col, pen=True: (p.setBrush(ctx.c(col)),
                                                 p.setPen(QPen(ctx.c(DGOLD), 2) if pen else Qt.NoPen),
                                                 p.drawEllipse(QPointF(x, y), rx, ry))
        wag = math.sin(ctx.t * 9) * 20
        L(dx - 32, dy + 14, dx - 55 - wag * 0.4, dy - 14 + wag * 0.3, DGOLD, 9)
        for off, ph in ((-22, 0), (22, math.pi), (-10, math.pi), (10, 0)):
            sw = math.sin(lt * 6 + ph) * 10
            lx = dx + off
            L(lx, dy + 38, lx + sw * 0.6, dy + 78 - max(0, sw) * 0.2, DGOLD, 9)
        E(dx, dy + 22, 42, 26, GOLD)
        hx, hy = dx + 38, dy - 4
        E(hx, hy, 24, 22, GOLD)
        es = math.sin(ctx.t * 8) * 3
        E(hx - 12, hy - 6 + es, 9, 17, DGOLD, False)
        sx = hx + 17
        E(sx, hy + 8, 13, 9, "#e8c27a" if pal == "yellow" else DGOLD, False)
        E(sx + 8, hy + 4, 4.5, 3.5, "#151515", False)
        tg = abs(math.sin(ctx.t * 5))
        E(sx, hy + 17 + tg * 3, 3.5, 4 + tg * 4, "#ff6b8b", False)
        E(hx + 7, hy - 6, 5, 5, "#ffffff", False)
        E(hx + 8, hy - 6, 3, 3, "#151515", False)
    return lab


reg("spiderman", "Web Swinger", "swing", "Swingers", custom=spiderman)  # id kept for old configs
for _pid, (_g, _d, _name) in PALETTES.items():
    reg("lab_" + ("choc" if _pid == "choc" else _pid), _name, "walk", "Animals",
        custom=make_lab(_pid), w=220, h=150)
