"""
hotkey.py - Global hotkey listener for BlackoutMode using pynput.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard


class GlobalHotkeyManager:
    """
    Manages low-level global keyboard hooks.
    Dispatches hotkey events safely to caller-provided callbacks.
    """

    def __init__(
        self,
        on_trigger_blackout: Callable[[], None],
        on_dismiss_blackout: Callable[[], None],
    ):
        self.on_trigger_blackout = on_trigger_blackout
        self.on_dismiss_blackout = on_dismiss_blackout

        self._blackout_active = False
        self._listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

        # Modifier key states
        self._ctrl_pressed = False
        self._alt_pressed = False

    def set_blackout_active(self, active: bool) -> None:
        """Updates blackout active state so ESC only intercepts when overlay is active."""
        with self._lock:
            self._blackout_active = active

    def start(self) -> None:
        """Starts the global keyboard listener in a background daemon thread."""
        if self._listener is not None:
            return

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Stops the global keyboard listener."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def _on_press(self, key) -> None:
        """Handles key down events globally across Windows."""
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self._ctrl_pressed = True
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self._alt_pressed = True

        # ESC key intercepts ONLY when blackout overlay is active
        if key == keyboard.Key.esc:
            with self._lock:
                active = self._blackout_active
            if active:
                if self.on_dismiss_blackout:
                    self.on_dismiss_blackout()
                return

        # Check for Ctrl + Alt + B trigger
        if self._ctrl_pressed and self._alt_pressed:
            char = None
            if hasattr(key, "char") and key.char:
                char = key.char.lower()
            elif hasattr(key, "vk") and key.vk == 66:  # VK_B
                char = "b"

            if char == "b":
                if self.on_trigger_blackout:
                    self.on_trigger_blackout()

    def _on_release(self, key) -> None:
        """Handles key release events."""
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self._ctrl_pressed = False
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self._alt_pressed = False
