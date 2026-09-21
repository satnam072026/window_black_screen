# Root create_shortcut.ps1 wrapper delegating to scripts/create_shortcut.ps1
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetScript = Join-Path $ScriptDir "scripts\create_shortcut.ps1"
& $TargetScript
