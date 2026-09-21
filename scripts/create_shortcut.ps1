# scripts/create_shortcut.ps1 - Generates Windows Desktop shortcut for BlackoutMode

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$TargetExe = Join-Path $ProjectRoot "dist\BlackoutMode.exe"
$IconPath = Join-Path $ProjectRoot "assets\icon.ico"
if (-not (Test-Path $IconPath)) {
    $IconPath = Join-Path $ProjectRoot "icon.ico"
}

$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ShortcutPath = Join-Path $DesktopPath "BlackoutMode.lnk"

if (-not (Test-Path $TargetExe)) {
    Write-Error "Could not find BlackoutMode.exe at $TargetExe. Please run 'python scripts/build.py' first."
    exit 1
}

try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetExe
    $Shortcut.WorkingDirectory = Split-Path -Parent $TargetExe
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = "$IconPath,0"
    } else {
        $Shortcut.IconLocation = "$TargetExe,0"
    }
    $Shortcut.Description = "BlackoutMode - Instant Full-Screen Blackout Utility (Ctrl+Alt+B / ESC)"
    $Shortcut.Save()

    Write-Host "`n========================================================" -ForegroundColor Green
    Write-Host "SUCCESS: Desktop shortcut created!" -ForegroundColor Green
    Write-Host "Shortcut: $ShortcutPath" -ForegroundColor Cyan
    Write-Host "Target:   $TargetExe" -ForegroundColor Cyan
    Write-Host "========================================================`n"
} catch {
    Write-Error "Failed to create desktop shortcut: $_"
    exit 1
}
