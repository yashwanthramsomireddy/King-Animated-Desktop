# Changelog

## 1.0.1
- Fix: app could appear to stop responding to launches after running a while. If Explorer restarts or crashes (common after Windows updates or driver resets), Windows silently drops every running app's tray icon and never brings it back — King Animated Desktop kept running fine, but there was no way left to reach Settings. The tray icon now self-heals: it's automatically re-asserted every 10 seconds, so it reappears on its own.
- Fix: launching the app a second time while it's already running (e.g. double-clicking the shortcut when it's already open via autostart) used to exit silently with no feedback, making it look broken. It now shows a short message confirming it's already running and where to find the tray icon.
- Fix: the overlay could drop behind certain apps (seen with Claude desktop and Windows Explorer) instead of staying on top. It now reacts instantly when any window gains focus, instead of only re-asserting itself on a 1-second poll, closing the window where another app could win the on-top race.
- Info tab: removed the Email support, Share, and Licenses && notices buttons, and both donate buttons. Privacy policy and Terms of use now link straight to the plain-text files in the GitHub repo instead of opening a bundled/hosted copy; the licence name is now itself a link to the repo's LICENSE file. Added TERMS.txt (new, repo root) alongside the existing PRIVACY.txt.
- Performance: cut per-frame rendering cost, most visible with several objects on screen or custom text. Colour conversion for every shape of every object (the single hottest piece of code, run per shape x per object x every frame) now skips an unnecessary round trip for the default look (no hue shift/saturation/brightness change) - about 2x faster per call. Custom text no longer rebuilds its on-screen letter shapes from scratch every frame when the text hasn't changed; the neon badge no longer rebuilds its font every frame either.
- Build: moved the website pages (`index.html`, `privacy-policy.html`, `terms-of-service.html`, `img/`) from `web/king-animated-desktop/` to the repo root, and updated the installer to match. (The old nested path was also the cause of a local "No files found" build failure if that folder went missing from a working copy.)

## 1.0.0
- Name: **King Animated Desktop** ("Windows" avoided: Microsoft trademark).
- Settings window themes: pitch black (default), white, system + accent colour.
- Info tab: developer details, support email, privacy and licence documents.
- EU/GDPR: privacy notice + licence agreement shown by the installer, third-party (LGPL) notices, installer languages for 13 EU/EEA languages, option to delete settings on uninstall.
- First public release (MIT).
- 61 objects in 9 categories, 68 global settings, 7 per-object settings.
- Custom text objects: position, 16 animations, swing from a thread, templates (31 options each).
- Overlays re-assert always-on-top over other apps; live preview in settings.
- Info tab slimmed to what is needed; Donate (PayPal / Razorpay); bundled website pages (index, privacy policy, terms of use).
- Full-screen auto-hide is off by default.
- Settings window (gallery, search, presets, per-object overrides, import/export), tray icon.
- Neon TeamExyKings badge with 19 options.
- Windows installer: licence page, installs to Program Files, desktop shortcut, start-with-Windows.
- Rewrite on PySide6 for true per-pixel transparency (replaces the tkinter prototype).
