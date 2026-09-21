# scripts/install.ps1 - Installs BlackoutMode permanently into AppData\Local\Programs
# Allows deleting the source repository folder while keeping the app working on Desktop & Start Menu.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$SourceExe = Join-Path $ProjectRoot "dist\BlackoutMode.exe"
$SourceIcon = Join-Path $ProjectRoot "assets\icon.ico"

if (-not (Test-Path $SourceExe)) {
    Write-Error "dist\BlackoutMode.exe not found. Please compile the project first using 'python scripts/build.py'."
    exit 1
}

# Standard Windows user programs directory (no admin rights needed)
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\BlackoutMode"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

$DestExe = Join-Path $InstallDir "BlackoutMode.exe"
$DestIcon = Join-Path $InstallDir "icon.ico"

Copy-Item -Path $SourceExe -Destination $DestExe -Force
if (Test-Path $SourceIcon) {
    Copy-Item -Path $SourceIcon -Destination $DestIcon -Force
}

$WshShell = New-Object -ComObject WScript.Shell

# 1. Desktop Shortcut
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$DesktopShortcutPath = Join-Path $DesktopPath "BlackoutMode.lnk"
$Shortcut = $WshShell.CreateShortcut($DesktopShortcutPath)
$Shortcut.TargetPath = $DestExe
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = "$DestIcon,0"
$Shortcut.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
$Shortcut.Save()

# 2. Start Menu Shortcut
$StartMenuPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)
$StartMenuShortcutPath = Join-Path $StartMenuPath "BlackoutMode.lnk"
$StartShortcut = $WshShell.CreateShortcut($StartMenuShortcutPath)
$StartShortcut.TargetPath = $DestExe
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.IconLocation = "$DestIcon,0"
$StartShortcut.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
$StartShortcut.Save()

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "PERMANENT INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "App Installed to: $InstallDir" -ForegroundColor Cyan
Write-Host "Desktop Shortcut: $DesktopShortcutPath" -ForegroundColor Cyan
Write-Host "Start Menu:       $StartMenuShortcutPath" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
Write-Host "You can now safely delete the source/project folder without breaking the app!`n" -ForegroundColor Yellow
