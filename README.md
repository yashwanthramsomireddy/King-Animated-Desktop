<div align="center">

# 👑 King Animated Desktop

**Free, open-source animated companions for your Windows desktop** — a web-swinging hero, a Labrador trotting along the taskbar, a neon **TeamExyKings** badge, **61 objects** to mix and match, and **your own custom text** with animation and swing. They float over every app you have open.

[![CI](https://github.com/yashwanthramsomireddy/king-animated-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/yashwanthramsomireddy/king-animated-desktop/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-00ffd0.svg)](LICENSE)

![King Animated Desktop gallery](docs/gallery.png)

</div>

## Features

- **61 objects** – animals, birds, characters, swingers, flyers, floaters, fallers, sports balls and corner decor
- **Custom text objects** (up to 20): any text, font, colour, glow, box style, exact position (corner presets or % + pixel offsets, any monitor), 16 animations (pulse, float, bounce, shake, blink, wave, rainbow, spin, typewriter, marquee, rise, fall, walk, fly) and an optional **swing** from a thread — 31 options each, plus 8 templates
- **68 global settings + 7 per-object settings**: size, speed, opacity, hue, lane/corner, rainbow mode, outline style, shadows, swing physics, quiet hours, full-screen auto-hide, multi-monitor and more
- **Live preview** – changes apply on screen as you adjust them
- **Neon badge** with 19 options (text, colour, glow, pulse, font, thread, corner…)
- **Pitch-black and white themes** for the settings window (plus *System*), with your own accent colour
- **Info tab** with developer details, privacy policy, terms, source code, licences and optional **Donate** buttons (PayPal / Razorpay) — donations unlock nothing, everything is free
- **Click-through** – pets never block your mouse; always on top of other apps (re-asserted every second so they stay visible); real per-pixel transparency
- **Autostart** with Windows (on by default, switchable), desktop shortcut, tray icon
- **No ads, no telemetry, no accounts.** The app itself makes no network connections. Settings live in `%APPDATA%\KingAnimatedDesktop\config.json`

| Pitch black (default) | White |
|---|---|
| ![Pitch black](docs/settings.png) | ![White](docs/settings_white.png) |

## Install (Windows 10 / 11)

### Option A – Installer (recommended)
Download **[`KingAnimatedDesktop_Setup_1.0.0.exe`](https://github.com/yashwanthramsomireddy/king-animated-desktop/releases/download/v1.0.0/KingAnimatedDesktop_Setup_1.0.0.exe)** (all versions: [Releases](https://github.com/yashwanthramsomireddy/king-animated-desktop/releases)), accept the licence, and click through. It installs to `C:\Program Files\King Animated Desktop`, and offers a **desktop shortcut** and **start with Windows** (both ticked by default).

### Option B – Run from source
```bat
git clone https://github.com/yashwanthramsomireddy/king-animated-desktop
cd king-animated-desktop
run_pets.bat          :: installs PySide6 and starts the pets
```
or `pip install -r requirements.txt && python run.py --settings`

### Build the installer yourself
Double-click **`build_windows_installer.bat`** (installs PyInstaller + Inno Setup via winget if needed) → `dist\KingAnimatedDesktop_Setup_1.0.0.exe`.
Maintainers: pushing a tag like `v1.0.0` makes GitHub Actions build and publish the installer automatically.

## Using it

| Action | How |
|---|---|
| Pick objects, presets, customise | Tray icon → double-click (or *Settings*) |
| Pause / resume | Tray icon → right-click |
| Quit | Tray icon → right-click → *Quit King Animated Desktop* |
| Open settings from a shortcut | `KingAnimatedDesktop.exe --settings` |
| Start hidden (autostart does this) | `KingAnimatedDesktop.exe --background` |

Settings tabs: **Objects** (gallery with search, categories, presets, *Surprise me*, per-object overrides), **Text**, **General**, **Appearance**, **Behaviour**, **Badge**, **Info**. Export / import your setup as JSON.

> Known limits: exclusive full-screen games (true DirectX full-screen) draw over everything, so overlays can't appear on top of them; borderless-window games work. Objects live on the virtual desktop where they were started. The unsigned installer may trigger a Windows SmartScreen prompt (*More info → Run anyway*).

> Tip: every enabled object is its own tiny window. 10–20 at once is smooth on any PC; the *Everything* preset is capped by **Max pets on screen** (default 20).

## Add your own object (5 minutes)
Objects are vector shapes in a 100×100 box – no image files. See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome!

## Development
```bash
pip install -r requirements.txt pytest pillow
QT_QPA_PLATFORM=offscreen python -m pytest tests     # headless tests (Linux/macOS/Windows)
python tools/make_docs.py && python tools/make_web.py  # regenerate docs/*.png and the website pages
```
Platform notes: the overlay works on Windows (primary target); it also runs on macOS/Linux desktops that support transparent windows, but autostart / full-screen detection are Windows-only.

## Website pages
`web/king-animated-desktop/` holds the project's `index.html`, `privacy-policy.html` and `terms-of-service.html` (self-contained, no external assets). They are also bundled in the installer so the in-app links work offline.

## License
[MIT](LICENSE) © 2026 Yashwanth Ram Somireddy / TeamExyKings
