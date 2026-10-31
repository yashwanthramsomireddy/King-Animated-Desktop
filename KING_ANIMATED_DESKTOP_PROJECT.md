# King Animated Desktop – project handoff (paste/attach at the start of a new chat)

**Status:** v1.0.0 released (Oct 2026). Features complete; further work = new features / fixes only.
**Owner:** Yashwanth Ram Somireddy (Yash92Duster), TeamExyKings, Chennai, India
**Repo:** https://github.com/yashwanthramsomireddy/king-animated-desktop
**Release:** https://github.com/yashwanthramsomireddy/king-animated-desktop/releases/download/v1.0.0/KingAnimatedDesktop_Setup_1.0.0.exe
**Licence:** MIT · **Contact:** Yashwanthramsomireddy@gmail.com · **Site:** https://teamexykings.in

## What it is
Free, open-source Windows app: transparent, click-through, always-on-top animated objects over all apps (web-swinging hero shown as "Web Swinger", Labrador, neon TeamExyKings badge, 61 objects total) plus **custom text objects** (position, 16 animations, swing from a thread). Settings window + tray menu. Previously called "King Pets" / "King Animated Windows" (renamed: "Windows" is a Microsoft trademark; Spider-Man display name changed to "Web Swinger" for the same reason).

## Tech
- Python 3 + **PySide6 (Qt 6)**; frameless translucent windows (`FramelessWindowHint | Tool | WindowDoesNotAcceptFocus | WindowStaysOnTopHint | WindowTransparentForInput`, `WA_TranslucentBackground`). The earlier tkinter version showed a black screen on Yash's PC – do not go back to tkinter.
- Always-on-top over other apps: Win32 `SetWindowPos(HWND_TOPMOST, NOACTIVATE|NOMOVE|NOSIZE)` re-asserted ~every second (`keep_on_top_interval`), ex-styles via ctypes (`platform_utils.force_topmost`).
- Sprites are vector shape lists (100×100 box, no image files). Per-object config; schema-driven settings UI (`SCHEMA`, `PET_SCHEMA`, `TEXT_SCHEMA` generate widgets).
- Live preview: debounced (500 ms) save + engine rebuild; theme/accent changes restyle only.
- Packaging: PyInstaller one-folder → **Inno Setup 6** installer (licence page, privacy notice shown, 13 EU languages guarded by `FileExists`, installs to `C:\Program Files\King Animated Desktop`, desktop shortcut + autostart both default on, HKCU Run `--background`, uninstall offers to delete settings).
- GitHub Actions: `ci.yml` (tests), `release.yml` (windows runner builds installer on `v*` tag).

## Layout
```
run.py                      entry: [--settings] [--background]
king_pets/                  package (name kept from old project)
  config.py                 SCHEMA(68 global) PET_SCHEMA(7) TEXT_SCHEMA(31), sanitize(), config_path(), APP_NAME, VERSION
  engine.py                 Engine: actors/badges/texts, rebuild(), slow_tick(), tray, single instance (QLockFile)
  actors.py                 OverlayWindow, PetActor, BadgeActor, TextActor
  ui.py                     SettingsDialog (tabs: Objects, Text, General, Appearance, Behaviour, Badge, Info)
  theme.py                  pitch-black / white / system QSS, accent colour
  sprites.py, custom.py, render.py    object definitions + drawing
  about_info.py             developer info, URLs (PAYPAL_URL, RAZORPAY_URL, PRIVACY_URL ...)
  platform_utils.py         autostart, fullscreen detect, battery, quiet hours, force_topmost
tests/                      test_core.py, test_every_setting.py, test_text_and_ui.py (254 tests, ~70 s)
tools/                      make_docs.py (screenshots), make_web.py (site pages), make_icon.py
web/king-animated-desktop/  index.html, privacy-policy.html, terms-of-service.html (+img)  -> also copied to TeamExyKings Pages repo
installer/KingAnimatedDesktop.iss, build_windows_installer.bat, run_pets.bat
LICENSE EULA.txt PRIVACY.txt THIRD_PARTY_NOTICES.txt licenses/  README.md CHANGELOG.md CONTRIBUTING.md
```
Config file on user PC: `%APPDATA%\KingAnimatedDesktop\config.json` (env `KINGDESKTOP_CONFIG` overrides, used by tests).

## How to test (headless, Linux works)
```
pip install -r requirements.txt pytest pillow
QT_QPA_PLATFORM=offscreen python -m pytest tests -q
python tools/make_docs.py && python tools/make_web.py     # regenerate screenshots + site pages
```
Every global/per-object/text setting has a test proving it changes something observable and round-trips UI→config→save→reload. Keep that standard for new settings (add to the matching `CASES`/schema tests).

## Gotchas learned (don't repeat)
- Don't name attributes `x`/`y` on QWidget subclasses (shadows methods) – pets use `fx`/`fy`.
- `&` in Qt button/group titles is a mnemonic – write `&&`.
- `blockSignals` around item icon/check-state refresh, otherwise itemChanged wipes selection.
- Tests must really delete dialogs (`shiboken6.delete`), otherwise theme restyling slows the suite to minutes.
- Inno script: no `\` line continuations; keep UTF-8 BOM; languages/messages guarded by `#if FileExists`.
- Actor RNG seeded with `zlib.crc32` (Python `hash()` of str is per-process random → flaky tests).
- Dialog config must be deep-copied (no aliasing with engine cfg).

## Known limits (be honest in docs)
Exclusive-fullscreen games draw over overlays; objects live on one virtual desktop; installer unsigned (SmartScreen); nothing was tested on real Windows by Claude (Yash built and ran the installer himself and it worked); legal texts are not legal advice (governing law India).

## Decisions / user preferences
- README has **no donation links** (PayPal/Razorpay buttons exist only in the app's Info tab and the website pages; URLs in `about_info.py`).
- Do not mention Yash's employer anywhere public; credit name is "Yashwanth Ram Somireddy"; support-email greeting "Hi Yashwanth", subject "King Animated Desktop Support/Request - <timestamp>".
- Yash uploads to GitHub manually: always send a **full source zip** after changes (with README.md + CHANGELOG.md inside), and **list any files that must be deleted** (he overwrites files from the zip, no delete-and-add).
- Point out when a detail he gives looks wrong instead of silently following it.
- Version bumps: update `king_pets/config.py` `VERSION`, installer default `AppVersion`, `build_windows_installer.bat` output name/`/DAppVersion`, CHANGELOG, README download link.

## Release steps
1. Bump version, update CHANGELOG, run tests.
2. Push to GitHub; tag `vX.Y.Z` (Actions builds the installer) **or** run `build_windows_installer.bat` and attach `dist\KingAnimatedDesktop_Setup_X.Y.Z.exe` to the release manually.
3. Copy `web/king-animated-desktop/` into the TeamExyKings Pages repo (`yashwanthramsomireddy.github.io/TeamExyKings/king-animated-desktop/`) if the pages changed.

## Ideas not yet built (optional backlog)
Per-monitor object sets; interactive objects (follow cursor / react to clicks, would need non-click-through mode); more objects/seasonal packs; user-importable custom sprites; code-signing the installer; auto-update check (would break the "no network" promise – needs opt-in + privacy text update).
