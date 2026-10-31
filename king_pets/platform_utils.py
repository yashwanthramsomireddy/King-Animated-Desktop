"""Windows-only helpers (autostart, full-screen / battery detection). Safe no-ops elsewhere."""
import sys, os, datetime

IS_WIN = sys.platform.startswith("win")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "KingAnimatedDesktop"


def launch_command():
    """Command line that starts King Animated Desktop (installed .exe, or pythonw + run.py)."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = sys.executable
    if IS_WIN and exe.lower().endswith("python.exe"):
        exe = exe[:-10] + "pythonw.exe"
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "run.py"))
    return f'"{exe}" "{script}"'


def set_autostart(enabled):
    """Add/remove the HKCU Run entry. Returns True if state was applied."""
    if not IS_WIN:
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if enabled:
                winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, launch_command() + " --background")
            else:
                try:
                    winreg.DeleteValue(k, RUN_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception:
        return False


def autostart_enabled():
    if not IS_WIN:
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, RUN_NAME)
            return True
    except Exception:
        return False


def fullscreen_app_active(screen_geo):
    """True if the foreground window covers the whole screen (game / video / slideshow)."""
    if not IS_WIN:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return False
        buf = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(hwnd, buf, 64)
        if buf.value in ("Progman", "WorkerW", "Shell_TrayWnd"):   # desktop itself
            return False
        r = wintypes.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(r))
        return (r.left <= screen_geo.left() and r.top <= screen_geo.top() and
                r.right >= screen_geo.right() + 1 and r.bottom >= screen_geo.bottom() + 1)
    except Exception:
        return False


def on_battery():
    if not IS_WIN:
        return False
    try:
        import ctypes

        class PS(ctypes.Structure):
            _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                        ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                        ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]
        s = PS()
        ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
        return s.ACLineStatus == 0
    except Exception:
        return False


def in_quiet_hours(start, end, now=None):
    def parse(s):
        h, m = str(s).split(":")
        return int(h) * 60 + int(m)
    try:
        a, b = parse(start), parse(end)
    except Exception:
        return False
    now = now or datetime.datetime.now()
    n = now.hour * 60 + now.minute
    if a == b:
        return False
    return (a <= n < b) if a < b else (n >= a or n < b)


# Win32 constants
_HWND_TOPMOST = -1
_SWP_NOSIZE, _SWP_NOMOVE, _SWP_NOACTIVATE, _SWP_SHOWWINDOW, _SWP_NOOWNERZORDER = 0x1, 0x2, 0x10, 0x40, 0x200
_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW, _WS_EX_NOACTIVATE, _WS_EX_TRANSPARENT, _WS_EX_LAYERED, _WS_EX_TOPMOST = 0x80, 0x08000000, 0x20, 0x80000, 0x8


# Keeps the ctypes callback (and the hook handle) alive for the life of the
# process; if either got garbage-collected the hook would silently stop firing.
_fg_hook_handle = None
_fg_hook_proc = None


def install_foreground_hook(callback):
    """Call `callback()` the instant ANY window becomes the foreground window.

    Windows keeps "always on top" windows in their own z-order band above
    everything else, but that band has its own internal order, and any app
    that (even briefly) asserts its own topmost-ness on gaining focus -
    common in Explorer and in Electron-based apps - can land above us in
    that band. Re-asserting our topmost style on a ~1s poll (see
    keep_on_top_interval) leaves a window where that app wins the race every
    time it regains focus. Reacting to the OS's own foreground-change
    notification instead of waiting for the next poll closes most of that gap.

    No-op (returns None) off Windows, or if the hook can't be installed -
    the periodic poll in Engine.slow_tick keeps working as the fallback
    either way, so a failed hook degrades gracefully rather than breaking
    anything."""
    global _fg_hook_handle, _fg_hook_proc
    if not IS_WIN:
        return None
    try:
        import ctypes
        from ctypes import wintypes
        EVENT_SYSTEM_FOREGROUND = 0x0003
        WINEVENT_OUTOFCONTEXT = 0x0000
        WinEventProcType = ctypes.WINFUNCTYPE(
            None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
            wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)

        def _proc(hook, event, hwnd, id_object, id_child, thread, event_time):
            try:
                callback()
            except Exception:
                pass

        proc = WinEventProcType(_proc)
        handle = ctypes.windll.user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, 0, proc, 0, 0, WINEVENT_OUTOFCONTEXT)
        if not handle:
            return None
        _fg_hook_proc, _fg_hook_handle = proc, handle   # keep alive, see note above
        return handle
    except Exception:
        return None


def uninstall_foreground_hook():
    global _fg_hook_handle, _fg_hook_proc
    if IS_WIN and _fg_hook_handle:
        try:
            import ctypes
            ctypes.windll.user32.UnhookWinEvent(_fg_hook_handle)
        except Exception:
            pass
    _fg_hook_handle = None
    _fg_hook_proc = None


def force_topmost(hwnd, click_through=True):
    """Put a window above every other window (including other 'always on top' apps) without stealing focus.
    Windows can quietly drop topmost when another app claims it, so the engine calls this about once a second.
    Returns True if the Win32 call was made."""
    if not IS_WIN or not hwnd:
        return False
    try:
        import ctypes
        u = ctypes.windll.user32
        hwnd = int(hwnd)
        ex = u.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        want = ex | _WS_EX_TOOLWINDOW | _WS_EX_NOACTIVATE | _WS_EX_LAYERED | _WS_EX_TOPMOST
        if click_through:
            want |= _WS_EX_TRANSPARENT
        if want != ex:
            u.SetWindowLongW(hwnd, _GWL_EXSTYLE, want)
        u.SetWindowPos(hwnd, _HWND_TOPMOST, 0, 0, 0, 0,
                       _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE | _SWP_SHOWWINDOW | _SWP_NOOWNERZORDER)
        return True
    except Exception:
        return False
