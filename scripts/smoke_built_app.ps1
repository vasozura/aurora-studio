# scripts/smoke_built_app.ps1
#
# Smoke-test the built one-folder aurora-studio portable app.
# TASK-000046: PyInstaller Build Smoke Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\smoke_built_app.ps1
#
# Prerequisites:
#   Run .\scripts\build_windows_onefolder.ps1 first.
#
# This script does NOT open a GUI window.
# This script does NOT install packages.
# This script does NOT call providers.
# This script does NOT execute plugins.
# This script does NOT require admin rights.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path $ScriptDir -Parent
$ExeDir    = Join-Path $RepoRoot "dist\AuroraStudio"
$ExePath   = Join-Path $ExeDir "AuroraStudio.exe"

Write-Host "[aurora-studio] Smoke: built one-folder app"
Write-Host "[aurora-studio] EXE path: $ExePath"

# Confirm the build artifact exists
if (-not (Test-Path $ExePath)) {
    Write-Host ""
    Write-Host "ERROR: Built executable not found: $ExePath"
    Write-Host "Run the build first:"
    Write-Host "    .\scripts\build_windows_onefolder.ps1"
    Write-Host ""
    exit 1
}

# Run headless smoke (no window, JSON output, exit 0)
Write-Host "[aurora-studio] Running headless smoke..."
& $ExePath --headless-smoke
$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "[aurora-studio] Smoke PASSED (exit 0)."
} else {
    Write-Host ""
    Write-Host "ERROR: Smoke FAILED (exit $ExitCode)."
}

exit $ExitCode
