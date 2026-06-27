# scripts/build_windows_onefolder.ps1
#
# Build aurora-studio as a Windows one-folder portable app using PyInstaller.
# TASK-000046: PyInstaller Build Smoke Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\build_windows_onefolder.ps1
#
# Prerequisites:
#   python -m pip install -r build\requirements-build.txt
#
# This script does NOT install packages automatically.
# This script does NOT require admin rights.
# This script does NOT modify system PATH.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Resolve repository root from script location
$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path $ScriptDir -Parent

Write-Host "[aurora-studio] Build: Windows one-folder portable app"
Write-Host "[aurora-studio] Repo root: $RepoRoot"

# Set PYTHONPATH for current process only
$env:PYTHONPATH = Join-Path $RepoRoot "src"

# Check PyInstaller is available
Write-Host "[aurora-studio] Checking PyInstaller availability..."
try {
    $pyiVersion = & python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller not found" }
    Write-Host "[aurora-studio] PyInstaller version: $pyiVersion"
} catch {
    Write-Host ""
    Write-Host "ERROR: PyInstaller is not installed."
    Write-Host "Install build dependencies first:"
    Write-Host "    python -m pip install -r build\requirements-build.txt"
    Write-Host ""
    exit 1
}

# Paths
$SpecFile    = Join-Path $RepoRoot "build\pyinstaller\aurora_studio_desktop.spec"
$WorkPath    = Join-Path $RepoRoot "build\pyinstaller_work"
$DistPath    = Join-Path $RepoRoot "dist"
$OutputDir   = Join-Path $DistPath "AuroraStudio"

# Clean previous build output (controlled paths only)
Write-Host "[aurora-studio] Cleaning previous build output..."
if (Test-Path $WorkPath)  { Remove-Item -Recurse -Force $WorkPath }
if (Test-Path $OutputDir) { Remove-Item -Recurse -Force $OutputDir }

# Run PyInstaller
Write-Host "[aurora-studio] Running PyInstaller (one-folder mode)..."
& python -m PyInstaller $SpecFile `
    --distpath $DistPath `
    --workpath $WorkPath `
    --noconfirm

$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "[aurora-studio] Build succeeded."
    Write-Host "[aurora-studio] Output: $OutputDir"
    Write-Host "[aurora-studio] Run smoke: .\scripts\smoke_built_app.ps1"
} else {
    Write-Host ""
    Write-Host "ERROR: PyInstaller build failed (exit $ExitCode)."
}

exit $ExitCode
