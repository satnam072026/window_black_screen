"""
scripts/create_shortcut.py - Python utility to create Windows Desktop shortcut.
"""

import os
import sys
import subprocess


def get_desktop_dir() -> str:
    """Finds the true active Windows Desktop folder path."""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        return shell.SpecialFolders("Desktop")
    except Exception:
        pass

    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
            text=True,
        ).strip()
        if out and os.path.exists(out):
            return out
    except Exception:
        pass

    userprofile = os.environ.get("USERPROFILE", "")
    onedrive = os.environ.get("OneDrive", "")
    if onedrive and os.path.exists(os.path.join(onedrive, "Desktop")):
        return os.path.join(onedrive, "Desktop")
    return os.path.join(userprofile, "Desktop")


def create_desktop_shortcut():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    target_exe = os.path.join(project_root, "dist", "BlackoutMode.exe")

    icon_path = os.path.join(project_root, "assets", "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(project_root, "icon.ico")

    if not os.path.exists(target_exe):
        print(f"Error: Executable not found at {target_exe}. Please run 'python scripts/build.py' first.")
        sys.exit(1)

    desktop_dir = get_desktop_dir()
    shortcut_path = os.path.join(desktop_dir, "BlackoutMode.lnk")

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target_exe
        shortcut.WorkingDirectory = os.path.dirname(target_exe)
        if os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        else:
            shortcut.IconLocation = f"{target_exe},0"
        shortcut.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
        shortcut.Save()
        print(f"Desktop shortcut created successfully: {shortcut_path}")
    except Exception:
        ps_script = os.path.join(script_dir, "create_shortcut.ps1")
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script], check=True)


if __name__ == "__main__":
    create_desktop_shortcut()
