# scripts/smoke_portable_folder.ps1
#
# Smoke-test the staged Windows portable folder for aurora-studio.
# TASK-000047: Windows Portable Folder Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\smoke_portable_folder.ps1
#
# Prerequisites:
#   Run .\scripts\build_windows_onefolder.ps1 first.
#   Run .\scripts\stage_windows_portable.ps1 first.
#
# This script does NOT open a GUI window.
# This script does NOT install packages.
# This script does NOT call providers.
# This script does NOT execute plugins.
# This script does NOT require admin rights.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir    = $PSScriptRoot
$RepoRoot     = Split-Path $ScriptDir -Parent
$Version      = "0.1.0"
$FolderName   = "AuroraStudio-v$Version-windows-portable"
$StagingDir   = Join-Path $RepoRoot "dist-portable\$FolderName"
$StagedExe    = Join-Path $StagingDir "app\AuroraStudio\AuroraStudio.exe"
$SmokeBat     = Join-Path $StagingDir "smoke_desktop.bat"

Write-Host "[aurora-studio] Smoke: staged portable folder v$Version"
Write-Host "[aurora-studio] Folder: $StagingDir"

# Verify staged folder exists
if (-not (Test-Path $StagingDir)) {
    Write-Host ""
    Write-Host "ERROR: Staged portable folder not found: $StagingDir"
    Write-Host "Run staging first:"
    Write-Host "    .\scripts\stage_windows_portable.ps1"
    Write-Host ""
    exit 1
}

# Verify staged executable exists
if (-not (Test-Path $StagedExe)) {
    Write-Host ""
    Write-Host "ERROR: Staged executable not found: $StagedExe"
    Write-Host "Re-run build and staging:"
    Write-Host "    .\scripts\build_windows_onefolder.ps1"
    Write-Host "    .\scripts\stage_windows_portable.ps1"
    Write-Host ""
    exit 1
}

# Run the portable folder's own smoke script
Write-Host "[aurora-studio] Running portable smoke via smoke_desktop.bat..."
& cmd.exe /c $SmokeBat
$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "[aurora-studio] Portable smoke PASSED (exit 0)."
} else {
    Write-Host ""
    Write-Host "ERROR: Portable smoke FAILED (exit $ExitCode)."
}

exit $ExitCode
