"""
tests/test_blackout.py - Comprehensive unit & integration tests for BlackoutMode.
"""

import os
import sys
import unittest
import tkinter as tk

# Ensure src is in sys.path
here = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(here, ".."))
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from blackout.monitor import get_all_monitors, enable_high_dpi_awareness
from blackout.overlay import BlackoutOverlayManager
from blackout.hotkey import GlobalHotkeyManager
from blackout.icon_gen import create_blackout_icon


class TestBlackoutModeSuite(unittest.TestCase):

    def test_dpi_and_monitors(self):
        enable_high_dpi_awareness()
        monitors = get_all_monitors()
        self.assertGreaterEqual(len(monitors), 1)
        for m in monitors:
            self.assertIn("x", m)
            self.assertIn("y", m)
            self.assertIn("width", m)
            self.assertIn("height", m)
            self.assertIn("is_primary", m)
            self.assertGreater(m["width"], 0)
            self.assertGreater(m["height"], 0)

    def test_icon_generator(self):
        img = create_blackout_icon(256)
        self.assertEqual(img.size, (256, 256))
        self.assertEqual(img.mode, "RGBA")

    def test_overlay_lifecycle(self):
        root = tk.Tk()
        root.withdraw()

        deactivated_signals = []
        mgr = BlackoutOverlayManager(root, on_deactivate=lambda: deactivated_signals.append(True))
        self.assertFalse(mgr.is_active)

        # Activate
        mgr.activate()
        root.update()
        self.assertTrue(mgr.is_active)
        self.assertEqual(len(mgr._windows), len(get_all_monitors()))

        for win in mgr._windows:
            self.assertTrue(win.winfo_exists())
            self.assertEqual(win.cget("bg"), "#000000")

        # Deactivate
        mgr.deactivate()
        root.update()
        self.assertFalse(mgr.is_active)
        self.assertEqual(len(mgr._windows), 0)
        self.assertEqual(len(deactivated_signals), 1)

        root.destroy()

    def test_hotkey_manager(self):
        hotkeys = GlobalHotkeyManager(
            on_trigger_blackout=lambda: None,
            on_dismiss_blackout=lambda: None,
        )
        hotkeys.start()
        self.assertIsNotNone(hotkeys._listener)

        hotkeys.set_blackout_active(True)
        self.assertTrue(hotkeys._blackout_active)

        hotkeys.set_blackout_active(False)
        self.assertFalse(hotkeys._blackout_active)

        hotkeys.stop()
        self.assertIsNone(hotkeys._listener)

    def test_dist_binary_verification(self):
        dist_exe = os.path.join(project_root, "dist", "BlackoutMode.exe")
        if os.path.exists(dist_exe):
            size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
            self.assertGreater(size_mb, 10.0, "Compiled executable should be > 10MB standalone")


if __name__ == "__main__":
    unittest.main(verbosity=2)
