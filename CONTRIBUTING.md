# Contributing

Thanks for helping! Bug reports, new objects and translations are all welcome.

## Add a new object

1. Open `king_pets/sprites.py`.
2. Add a `reg(...)` call at the bottom:

```python
reg("octopus", "Octopus", "float", "Floaters", [
    ("e", 50, 40, 26, 26, "#b04ad8"),                 # head
    *eyes(42, 58, 38, 4),
    *[("anim", "rot", (50 + dx, 60), 14, 3 + abs(dx) / 8,
       [("l", 50 + dx, 60, 50 + dx, 92, "#b04ad8", 5)]) for dx in (-16, -6, 6, 16)],
])
```

* **id** – unique, lowercase · **name** – shown in the gallery · **kind** – how it moves:
  `walk` · `hop` · `bounce` · `fly` · `float` · `fall` · `swing` · `idle`
* **category** – one of `CATEGORIES` in `sprites.py`
* Draw in a **100×100** box, **facing right** (the engine mirrors it). `swing` sprites hang from `(50, 0)`.
* Shapes: `e` ellipse · `r` rounded rect · `l` line · `p` polygon · `a` arc · `t` text · `anim` animated group
  (`rot`, `scaley`, `scalex`, `spin`, `pulse`). Colours are `"#rrggbb"` or `("#rrggbb", alpha)`.
* Walkers can pass `legs=(color, [(x, y_top), ...], length, width)` for an animated gait.
* Need code instead of shapes? See `king_pets/custom.py` (web swinger, Labradors) – pass `custom=painter`.

3. Run `python -m pytest tests` (it renders every object in every state) and `python tools/make_docs.py`,
   then include the regenerated `docs/gallery.png` in your PR.

## Add a setting
Add one `S(...)` line to `SCHEMA` in `king_pets/config.py` and read `cfg["your_key"]`. The settings window builds the control automatically.

## Style
Plain Python 3.9+, PySide6, no extra dependencies. Keep it offline: **no network calls, no telemetry**.
