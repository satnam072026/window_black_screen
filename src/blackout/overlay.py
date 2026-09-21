"""
overlay.py - Borderless, always-on-top, click-absorbing multi-monitor black overlay windows.
"""

import tkinter as tk
import ctypes
from typing import List, Callable, Optional
from blackout.monitor import get_all_monitors

# Win32 Constants
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_SHOWWINDOW = 0x0040
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008


def apply_win32_topmost_toolwindow(hwnd: int) -> None:
    """Enforces WS_EX_TOOLWINDOW and HWND_TOPMOST using Win32 API."""
    try:
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW,
        )
    except Exception:
        pass


class BlackoutOverlayManager:
    """
    Coordinates one fullscreen black window per connected display.
    """

    def __init__(self, root: tk.Tk, on_deactivate: Optional[Callable[[], None]] = None):
        self.root = root
        self.on_deactivate_callback = on_deactivate
        self._is_active: bool = False
        self._windows: List[tk.Toplevel] = []
        self._topmost_timer = None

    @property
    def is_active(self) -> bool:
        return self._is_active

    def activate(self) -> None:
        """Creates and shows the black overlay across all active displays."""
        if self._is_active:
            return

        self._is_active = True
        self._destroy_windows()

        monitors = get_all_monitors()

        for mon in monitors:
            win = tk.Toplevel(self.root)
            win.title("")
            win.configure(bg="#000000", cursor="none")

            # Borderless, always-on-top, not in taskbar
            win.overrideredirect(True)
            win.attributes("-topmost", True)

            # Exact display bounds
            geom_str = f"{mon['width']}x{mon['height']}+{mon['x']}+{mon['y']}"
            win.geometry(geom_str)

            # Canvas absorbs clicks and guarantees solid black background
            canvas = tk.Canvas(win, bg="#000000", highlightthickness=0, cursor="none")
            canvas.pack(fill=tk.BOTH, expand=True)

            # Absorb all mouse clicks and movements
            for event_name in (
                "<Button-1>", "<Button-2>", "<Button-3>",
                "<Double-Button-1>", "<Double-Button-2>", "<Double-Button-3>",
                "<Triple-Button-1>", "<Triple-Button-2>", "<Triple-Button-3>",
                "<ButtonPress>", "<ButtonRelease>", "<Motion>",
                "<B1-Motion>", "<B2-Motion>", "<B3-Motion>",
                "<MouseWheel>"
            ):
                win.bind(event_name, self._absorb_mouse)
                canvas.bind(event_name, self._absorb_mouse)

            # Direct keyboard bindings for immediate dismissal
            win.bind("<Escape>", self._on_escape_pressed)
            win.bind("<Key>", self._on_any_key)

            self._windows.append(win)

        self.root.update_idletasks()
        for win in self._windows:
            try:
                hwnd = win.winfo_id()
                apply_win32_topmost_toolwindow(hwnd)
            except Exception:
                pass
            win.lift()

        if self._windows:
            self._windows[0].focus_force()

        self._schedule_topmost_check()

    def deactivate(self) -> None:
        """Closes all black overlay windows and restores normal desktop interaction."""
        if not self._is_active:
            return

        self._is_active = False

        if self._topmost_timer:
            try:
                self.root.after_cancel(self._topmost_timer)
            except Exception:
                pass
            self._topmost_timer = None

        self._destroy_windows()

        if self.on_deactivate_callback:
            try:
                self.on_deactivate_callback()
            except Exception:
                pass

    def _schedule_topmost_check(self) -> None:
        """Periodically ensures overlay windows remain topmost."""
        if not self._is_active:
            return

        for win in self._windows:
            try:
                if win.winfo_exists():
                    win.attributes("-topmost", True)
                    win.lift()
            except Exception:
                pass

        self._topmost_timer = self.root.after(1000, self._schedule_topmost_check)

    def _destroy_windows(self) -> None:
        for win in self._windows:
            try:
                if win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
        self._windows.clear()

    def _absorb_mouse(self, event) -> str:
        return "break"

    def _on_escape_pressed(self, event=None) -> str:
        self.deactivate()
        return "break"

    def _on_any_key(self, event) -> str:
        if event.keysym in ("Escape", "Esc") or event.keycode == 27:
            self.deactivate()
            return "break"
        return "break"
