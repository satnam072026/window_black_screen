"""
app.py - Main BlackoutMode application controller.
Coordinates event loop, system tray, global hotkeys, and multi-monitor overlays.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import ctypes

from blackout.monitor import enable_high_dpi_awareness
from blackout.overlay import BlackoutOverlayManager
from blackout.hotkey import GlobalHotkeyManager
from blackout.tray import TrayManager
from blackout.icon_gen import generate_all_icons


def get_resource_path(relative_name: str) -> str:
    """Resolves resource path for both development and PyInstaller single-file bundles."""
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir:
        target = os.path.join(base_dir, relative_name)
        if os.path.exists(target):
            return target

    # Search common development paths: assets/, current dir, project root
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, "..", ".."))

    search_candidates = [
        os.path.join(project_root, "assets", relative_name),
        os.path.join(project_root, relative_name),
        os.path.join(here, relative_name),
    ]

    for cand in search_candidates:
        if os.path.exists(cand):
            return cand

    # Default fallback
    return os.path.join(project_root, "assets", relative_name)


def ensure_icons_exist(png_path: str, ico_path: str) -> None:
    """Ensures icon files exist on disk, generating on the fly if needed."""
    if not os.path.exists(png_path) or not os.path.exists(ico_path):
        target_dir = os.path.dirname(ico_path)
        generate_all_icons(target_dir)


class BlackoutApp:
    """
    Main application controller managing lifecycle and cross-component dispatching.
    """

    def __init__(self):
        # 1. Enforce Per-Monitor DPI awareness
        enable_high_dpi_awareness()

        # 2. Check single instance using Windows Mutex
        self.mutex = None
        self._ensure_single_instance()

        # 3. Prepare icons
        self.png_icon_path = get_resource_path("icon.png")
        self.ico_icon_path = get_resource_path("icon.ico")
        ensure_icons_exist(self.png_icon_path, self.ico_icon_path)

        # 4. Initialize hidden Tkinter root
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("BlackoutMode Controller")
        try:
            if os.path.exists(self.ico_icon_path):
                self.root.iconbitmap(self.ico_icon_path)
        except Exception:
            pass

        # 5. Initialize components
        self.overlay_manager = BlackoutOverlayManager(
            root=self.root,
            on_deactivate=self._on_overlay_deactivated,
        )

        self.hotkey_manager = GlobalHotkeyManager(
            on_trigger_blackout=lambda: self.root.after(0, self.activate_blackout),
            on_dismiss_blackout=lambda: self.root.after(0, self.deactivate_blackout),
        )

        self.tray_manager = TrayManager(
            icon_path=self.png_icon_path,
            on_activate_blackout=lambda: self.root.after(0, self.activate_blackout),
            on_exit_app=lambda: self.root.after(0, self.quit_app),
            on_show_info=lambda: self.root.after(0, self.show_instructions),
        )

        self._is_shutting_down = False

    def _ensure_single_instance(self) -> None:
        """Prevents multiple concurrent instances using a named Win32 Mutex."""
        try:
            mutex_name = "Global\\BlackoutMode_SingleInstance_Mutex_v1"
            self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            last_error = ctypes.windll.kernel32.GetLastError()
            ERROR_ALREADY_EXISTS = 183
            if last_error == ERROR_ALREADY_EXISTS:
                ctypes.windll.user32.MessageBoxW(
                    None,
                    "BlackoutMode is already running in your system tray.\nPress Ctrl+Alt+B to activate.",
                    "BlackoutMode",
                    0x40 | 0x00010000,
                )
                sys.exit(0)
        except Exception:
            pass

    def start(self) -> None:
        """Starts background listeners, system tray, and main message loop."""
        self.hotkey_manager.start()
        self.tray_manager.start()

        self.root.after(
            600,
            lambda: self.tray_manager.notify(
                "BlackoutMode is active in your tray.\n• Press Ctrl+Alt+B to blackout\n• Press ESC anytime to exit blackout",
                "BlackoutMode Ready",
            ),
        )

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

    def activate_blackout(self) -> None:
        """Activates full screen blackout on all connected monitors."""
        if self._is_shutting_down:
            return
        self.overlay_manager.activate()
        self.hotkey_manager.set_blackout_active(True)

    def deactivate_blackout(self) -> None:
        """Deactivates blackout and restores desktop interaction."""
        self.overlay_manager.deactivate()
        self.hotkey_manager.set_blackout_active(False)

    def _on_overlay_deactivated(self) -> None:
        """Callback invoked whenever overlay windows close."""
        self.hotkey_manager.set_blackout_active(False)

    def show_instructions(self) -> None:
        """Displays informative help dialog for user hotkeys."""
        messagebox.showinfo(
            "BlackoutMode - Instructions",
            "BlackoutMode controls:\n\n"
            "• Trigger Blackout:\n"
            "   - Press Ctrl + Alt + B from anywhere\n"
            "   - Or click the tray icon\n\n"
            "• Dismiss Blackout:\n"
            "   - Press ESC at any time\n\n"
            "• Background apps, downloads, and music continue running uninterrupted.\n\n"
            "• To close BlackoutMode completely, right-click the tray icon and select Exit.",
            parent=self.root,
        )

    def quit_app(self) -> None:
        """Cleanly shuts down all components and exits."""
        if self._is_shutting_down:
            return
        self._is_shutting_down = True

        try:
            self.hotkey_manager.stop()
        except Exception:
            pass

        try:
            self.overlay_manager.deactivate()
        except Exception:
            pass

        try:
            self.tray_manager.stop()
        except Exception:
            pass

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

        if self.mutex:
            try:
                ctypes.windll.kernel32.CloseHandle(self.mutex)
            except Exception:
                pass

        sys.exit(0)


def main():
    app = BlackoutApp()
    app.start()


if __name__ == "__main__":
    main()
