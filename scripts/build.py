"""
scripts/build.py - Automated PyInstaller build script for BlackoutMode.
Compiles src/blackout into a standalone single-file Windows executable with embedded assets.
"""

import os
import sys
import subprocess
import shutil


def kill_running_instances():
    """Kills any active BlackoutMode.exe processes to avoid Windows file locks."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "BlackoutMode.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def build():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(project_root)

    print(f"Project root: {project_root}")
    kill_running_instances()

    ico_path = os.path.join(project_root, "assets", "icon.ico")
    png_path = os.path.join(project_root, "assets", "icon.png")

    if not os.path.exists(ico_path) or not os.path.exists(png_path):
        print("Generating icons in assets/...")
        sys.path.insert(0, os.path.join(project_root, "src"))
        from blackout.icon_gen import generate_all_icons
        generate_all_icons(os.path.join(project_root, "assets"))

    print("Cleaning build folders...")
    for folder in ("build", "dist"):
        p = os.path.join(project_root, folder)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
            except Exception as e:
                print(f"Warning: could not delete {folder}: {e}")

    spec_file = os.path.join(project_root, "BlackoutMode.spec")
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
        except Exception:
            pass

    print("Running PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        f"--icon={ico_path}",
        "--name=BlackoutMode",
        f"--add-data={ico_path};.",
        f"--add-data={png_path};.",
        f"--paths={os.path.join(project_root, 'src')}",
        "--hidden-import=blackout",
        "--hidden-import=blackout.app",
        "--hidden-import=blackout.monitor",
        "--hidden-import=blackout.overlay",
        "--hidden-import=blackout.hotkey",
        "--hidden-import=blackout.tray",
        "--hidden-import=blackout.icon_gen",
        "--hidden-import=pystray._win32",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=PIL",
        "main.py",
    ]

    print("Executing command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

    dist_exe = os.path.join(project_root, "dist", "BlackoutMode.exe")
    if os.path.exists(dist_exe):
        size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print(f"Executable: {dist_exe}")
        print(f"Size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("\nERROR: dist/BlackoutMode.exe not created.")
        sys.exit(1)


if __name__ == "__main__":
    build()
