# window_black_screen (BlackoutMode)

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)](https://github.com/satnam072026/window_black_screen)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Build-PyInstaller%20Onefile-success)](https://github.com/satnam072026/window_black_screen)

A production-ready, ultra-lightweight Windows desktop utility that instantly covers all connected displays with an always-on-top, borderless, pure `#000000` blackout overlay at the press of a hotkey or tray click.

All background applications, downloads, audio, render pipelines, and timers continue running uninterrupted. Pressing **`ESC`** instantly dismisses the blackout and restores your desktop state.

---

## ✨ Features

- **Instant Full Blackout**: Covers 100% of all connected monitors in pure black (`#000000`) without window chrome, titlebars, or borders.
- **Zero Process Interruption**: Purely visual overlay. Windows does **not** sleep, lock, or throttle background threads. Media, games, renderers, and downloads keep running at maximum speed.
- **DPI-Aware Multi-Monitor Geometry**: Uses Windows Per-Monitor DPI V2 awareness (`EnumDisplayMonitors`) to correctly span setups with mixed DPI scaling (100%, 125%, 150%, 200%) and negative coordinate offsets without gaps or misalignments.
- **Click Absorption**: Traps and consumes all mouse clicks, preventing accidental input from passing through to underlying desktop windows or apps.
- **Instant ESC Dismissal**: Pressing `ESC` anywhere instantly drops the overlay. Context-sensitive global keyboard hooking ensures `ESC` only intercepts when blackout is active, leaving normal desktop usage completely untouched.
- **System Tray Integration**: Runs discreetly in the Windows notification area (`pystray`) with quick trigger, user instructions, and clean application exit.
- **Global Hotkey Trigger**: Press **`Ctrl + Alt + B`** from any application or game to trigger Blackout immediately.
- **Single-Instance Mutex**: Protected by a named Win32 Mutex to prevent duplicate background instances.
- **Standalone Single-File Binary**: Packaged using PyInstaller into a zero-dependency `BlackoutMode.exe`.

---

## ⌨️ Controls & Shortcuts

| Action | Shortcut / Trigger | Description |
| :--- | :--- | :--- |
| **Activate Blackout** | `Ctrl + Alt + B` | Instantly blankets all monitors in black. |
| **Activate Blackout (Mouse)** | Click System Tray Icon | Primary click or context menu trigger. |
| **Dismiss Blackout** | `ESC` | Instantly closes overlay and restores desktop. |
| **Show Instructions** | Right-click Tray > Instructions | Displays shortcut guide. |
| **Exit Application** | Right-click Tray > Exit | Shuts down listeners and frees memory. |

---

## 📂 Project Architecture

```
window_black_screen/
├── assets/
│   ├── icon.ico                  # Multi-resolution ICO (16x16 to 256x256)
│   └── icon.png                  # High-res PNG master asset
├── src/
│   └── blackout/
│       ├── __init__.py           # Package metadata
│       ├── __main__.py           # Package execution entry point
│       ├── app.py                # Application controller & mutex enforcement
│       ├── monitor.py            # DPI-aware Win32 monitor coordinate detection
│       ├── overlay.py            # Multi-monitor borderless black windows
│       ├── hotkey.py             # Global keyboard hook manager (pynput)
│       ├── tray.py               # Notification area system tray manager (pystray)
│       └── icon_gen.py           # Programmatic icon generator (Pillow)
├── scripts/
│   ├── build.py                  # PyInstaller one-file packaging script
│   ├── create_shortcut.ps1       # Native PowerShell shortcut creation
│   └── create_shortcut.py        # Python Desktop shortcut generator
├── tests/
│   ├── __init__.py
│   └── test_blackout.py          # Automated test suite
├── main.py                       # Root launcher
├── requirements.txt              # Minimal pinned dependencies
├── pyproject.toml                # Project packaging specification
├── LICENSE                       # MIT License
└── README.md                     # Documentation
```

---

## 🚀 Quick Start (Running from Source)

### 1. Clone Repository
```bash
git clone https://github.com/satnam072026/window_black_screen.git
cd window_black_screen
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
python main.py
```
*Or execute as a module:*
```bash
python -m src.blackout
```

---

## 🔨 Compiling Standalone Executable

To build a standalone, zero-dependency `dist/BlackoutMode.exe` that runs without Python installed:

```bash
python scripts/build.py
```

*Or via PyInstaller directly:*
```bash
pyinstaller --noconfirm --onefile --noconsole --icon=assets/icon.ico --name=BlackoutMode --add-data="assets/icon.ico;." --add-data="assets/icon.png;." --paths=src --hidden-import=blackout --hidden-import=blackout.app --hidden-import=blackout.monitor --hidden-import=blackout.overlay --hidden-import=blackout.hotkey --hidden-import=blackout.tray --hidden-import=blackout.icon_gen --hidden-import=pystray._win32 --hidden-import=pynput.keyboard._win32 --hidden-import=PIL main.py
```

The compiled binary will be placed at:
```
dist/BlackoutMode.exe
```

---

## 🖥️ Desktop Shortcut Setup

Generate a Windows Desktop shortcut pointing directly to the compiled executable:

**PowerShell**:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_shortcut.ps1
```

**Python**:
```bash
python scripts/create_shortcut.py
```

The shortcut will appear on your Desktop as **`BlackoutMode.lnk`** with the custom icon.

---

## 🧪 Testing

Run the automated test suite:
```bash
python tests/test_blackout.py
```

Tests cover:
- Per-monitor DPI awareness and monitor enumeration.
- High-res icon generation.
- Overlay creation, mouse absorption, and clean destruction.
- Global hotkey listener start/stop and state transitions.
- Standalone binary integrity.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
