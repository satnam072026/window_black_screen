"""
scripts/install.py - Python utility to permanently install BlackoutMode to AppData.
Allows safely deleting the source folder from Desktop without breaking the installed app.
"""

import os
import sys
import shutil
import subprocess


def install_app():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    source_exe = os.path.join(project_root, "dist", "BlackoutMode.exe")
    source_icon = os.path.join(project_root, "assets", "icon.ico")

    if not os.path.exists(source_exe):
        print("Error: dist/BlackoutMode.exe not found. Please run 'python scripts/build.py' first.")
        sys.exit(1)

    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    install_dir = os.path.join(local_app_data, "Programs", "BlackoutMode")
    os.makedirs(install_dir, exist_ok=True)

    dest_exe = os.path.join(install_dir, "BlackoutMode.exe")
    dest_icon = os.path.join(install_dir, "icon.ico")

    # Stop any running instance before overwriting
    subprocess.run(["taskkill", "/F", "/IM", "BlackoutMode.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    shutil.copy2(source_exe, dest_exe)
    if os.path.exists(source_icon):
        shutil.copy2(source_icon, dest_icon)

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")

        # 1. Desktop shortcut
        desktop_dir = shell.SpecialFolders("Desktop")
        desktop_lnk = os.path.join(desktop_dir, "BlackoutMode.lnk")
        s1 = shell.CreateShortcut(desktop_lnk)
        s1.TargetPath = dest_exe
        s1.WorkingDirectory = install_dir
        s1.IconLocation = f"{dest_icon},0"
        s1.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
        s1.Save()

        # 2. Start menu shortcut
        programs_dir = shell.SpecialFolders("Programs")
        start_lnk = os.path.join(programs_dir, "BlackoutMode.lnk")
        s2 = shell.CreateShortcut(start_lnk)
        s2.TargetPath = dest_exe
        s2.WorkingDirectory = install_dir
        s2.IconLocation = f"{dest_icon},0"
        s2.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
        s2.Save()

        print(f"Installed to: {dest_exe}")
        print(f"Desktop shortcut: {desktop_lnk}")
        print(f"Start Menu shortcut: {start_lnk}")
        print("\nSUCCESS: You can now safely delete the source/project folder!")
    except Exception:
        # Fallback to PowerShell installer
        ps_script = os.path.join(script_dir, "install.ps1")
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script], check=True)


if __name__ == "__main__":
    install_app()
