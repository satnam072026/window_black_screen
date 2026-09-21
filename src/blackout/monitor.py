"""
monitor.py - High-DPI aware multi-monitor coordinate detection for Windows.
Enumerates all active displays with exact physical pixel bounds.
"""

import ctypes
from ctypes import wintypes
from typing import List, Dict, Any


def enable_high_dpi_awareness() -> None:
    """
    Enables Per-Monitor DPI V2 awareness on Windows.
    Prevents Windows DWM from scaling or distorting multi-monitor coordinates.
    """
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass

    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]


MONITOR_ENUM_PROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HMONITOR,
    wintypes.HDC,
    ctypes.POINTER(RECT),
    wintypes.LPARAM,
)


def get_all_monitors() -> List[Dict[str, Any]]:
    """
    Returns a list of dictionaries for each physical monitor:
    [
        {
            "id": int,
            "x": int,
            "y": int,
            "width": int,
            "height": int,
            "is_primary": bool
        },
        ...
    ]
    Handles multi-monitor configurations, including negative coordinate offsets.
    """
    enable_high_dpi_awareness()

    monitors: List[Dict[str, Any]] = []

    def _callback(h_monitor, hdc, lprect, lparam):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if ctypes.windll.user32.GetMonitorInfoW(h_monitor, ctypes.byref(info)):
            r = info.rcMonitor
            monitors.append({
                "id": len(monitors),
                "x": int(r.left),
                "y": int(r.top),
                "width": int(r.right - r.left),
                "height": int(r.bottom - r.top),
                "is_primary": bool(info.dwFlags & 1),
            })
        return True

    cb = MONITOR_ENUM_PROC(_callback)
    success = ctypes.windll.user32.EnumDisplayMonitors(None, None, cb, 0)

    # Fallback to virtual screen or primary if enum failed or returned empty
    if not monitors or not success:
        x_virt = ctypes.windll.user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        y_virt = ctypes.windll.user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        cx_virt = ctypes.windll.user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        cy_virt = ctypes.windll.user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

        if cx_virt > 0 and cy_virt > 0:
            monitors.append({
                "id": 0,
                "x": int(x_virt),
                "y": int(y_virt),
                "width": int(cx_virt),
                "height": int(cy_virt),
                "is_primary": True,
            })
        else:
            cx = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
            cy = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            monitors.append({
                "id": 0,
                "x": 0,
                "y": 0,
                "width": int(cx),
                "height": int(cy),
                "is_primary": True,
            })

    monitors.sort(key=lambda m: (not m["is_primary"], m["id"]))
    return monitors
