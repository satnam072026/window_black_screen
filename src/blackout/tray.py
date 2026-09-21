"""
tray.py - System tray icon management using pystray.
Provides tray notifications, menu controls, and clean exit.
"""

import threading
from typing import Callable
from PIL import Image
import pystray


class TrayManager:
    """
    Manages the Windows notification area (system tray) icon.
    """

    def __init__(
        self,
        icon_path: str,
        on_activate_blackout: Callable[[], None],
        on_exit_app: Callable[[], None],
        on_show_info: Callable[[], None],
    ):
        self.icon_path = icon_path
        self.on_activate_blackout = on_activate_blackout
        self.on_exit_app = on_exit_app
        self.on_show_info = on_show_info

        self._icon: pystray.Icon = None
        self._thread: threading.Thread = None

    def start(self) -> None:
        """Initializes and starts the system tray icon in a background thread."""
        try:
            image = Image.open(self.icon_path)
        except Exception:
            image = Image.new("RGBA", (64, 64), (20, 20, 20, 255))

        menu = pystray.Menu(
            pystray.MenuItem(
                "🌑 Activate Blackout (Ctrl+Alt+B)",
                self._on_activate_clicked,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "ℹ️ Instructions (ESC to Dismiss)",
                self._on_info_clicked,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ Exit BlackoutMode",
                self._on_exit_clicked,
            ),
        )

        self._icon = pystray.Icon(
            name="BlackoutMode",
            icon=image,
            title="BlackoutMode (Ctrl+Alt+B to Blackout, ESC to Exit)",
            menu=menu,
        )

        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def notify(self, message: str, title: str = "BlackoutMode") -> None:
        """Displays a native Windows notification balloon/toast."""
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass

    def stop(self) -> None:
        """Removes the system tray icon cleanly."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def _on_activate_clicked(self, icon, item) -> None:
        if self.on_activate_blackout:
            self.on_activate_blackout()

    def _on_info_clicked(self, icon, item) -> None:
        if self.on_show_info:
            self.on_show_info()

    def _on_exit_clicked(self, icon, item) -> None:
        if self.on_exit_app:
            self.on_exit_app()
