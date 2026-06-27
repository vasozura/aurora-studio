# scripts/stage_windows_portable.ps1
#
# Stage the Windows portable folder for aurora-studio.
# TASK-000047: Windows Portable Folder Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\stage_windows_portable.ps1
#
# Prerequisites:
#   Run .\scripts\build_windows_onefolder.ps1 first.
#
# This script does NOT build the EXE.
# This script does NOT create a ZIP release.
# This script does NOT install packages.
# This script does NOT require admin rights.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir  = $PSScriptRoot
$RepoRoot   = Split-Path $ScriptDir -Parent
$Version    = "0.1.0"
$FolderName = "AuroraStudio-v$Version-windows-portable"
$BuiltApp   = Join-Path $RepoRoot "dist\AuroraStudio"
$BuiltExe   = Join-Path $BuiltApp "AuroraStudio.exe"
$StagingDir = Join-Path $RepoRoot "dist-portable\$FolderName"
$AppDest    = Join-Path $StagingDir "app\AuroraStudio"
$Templates  = Join-Path $RepoRoot "packaging\portable"

Write-Host "[aurora-studio] Stage: Windows portable folder v$Version"
Write-Host "[aurora-studio] Staging to: $StagingDir"

# Verify built app exists
if (-not (Test-Path $BuiltExe)) {
    Write-Host ""
    Write-Host "ERROR: Built executable not found: $BuiltExe"
    Write-Host "Run the build first:"
    Write-Host "    .\scripts\build_windows_onefolder.ps1"
    Write-Host ""
    exit 1
}

# Clean and recreate staging folder (controlled path only)
Write-Host "[aurora-studio] Cleaning previous staging output..."
if (Test-Path $StagingDir) { Remove-Item -Recurse -Force $StagingDir }
New-Item -ItemType Directory -Path $StagingDir | Out-Null

# Copy PyInstaller one-folder output into app/AuroraStudio/
Write-Host "[aurora-studio] Copying built app..."
New-Item -ItemType Directory -Path (Split-Path $AppDest -Parent) | Out-Null
Copy-Item -Recurse -Force $BuiltApp $AppDest

# Create writable user-data folders
Write-Host "[aurora-studio] Creating portable folder structure..."
foreach ($folder in @("data", "logs", "samples", "tmp")) {
    New-Item -ItemType Directory -Path (Join-Path $StagingDir $folder) | Out-Null
}

# Create top-level run_desktop.bat
$RunBat = @'
@echo off
:: run_desktop.bat — Aurora Studio portable launcher
:: Launches the Aurora Studio desktop shell.
:: Requires a display.
cd /d "%~dp0"
app\AuroraStudio\AuroraStudio.exe
'@
Set-Content -Path (Join-Path $StagingDir "run_desktop.bat") -Value $RunBat -Encoding UTF8

# Create top-level smoke_desktop.bat
$SmokeBat = @'
@echo off
:: smoke_desktop.bat — Aurora Studio portable headless smoke
:: Runs the desktop shell in headless mode (no window).
:: Exits 0 on success, non-zero on failure.
cd /d "%~dp0"
app\AuroraStudio\AuroraStudio.exe --headless-smoke
if errorlevel 1 (
    echo ERROR: Portable smoke FAILED.
    exit /b 1
)
echo Portable smoke PASSED.
'@
Set-Content -Path (Join-Path $StagingDir "smoke_desktop.bat") -Value $SmokeBat -Encoding UTF8

# Copy templates as rendered text files
Write-Host "[aurora-studio] Copying README and NOTICE..."
Copy-Item (Join-Path $Templates "README.txt.template") (Join-Path $StagingDir "README.txt")
Copy-Item (Join-Path $Templates "NOTICE.txt.template") (Join-Path $StagingDir "NOTICE.txt")

Write-Host ""
Write-Host "[aurora-studio] Staging complete."
Write-Host "[aurora-studio] Staged folder: $StagingDir"
Write-Host "[aurora-studio] Run smoke: .\scripts\smoke_portable_folder.ps1"

exit 0
