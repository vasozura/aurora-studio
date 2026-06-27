# scripts/smoke_portable_zip.ps1
#
# Smoke-test the portable ZIP release candidate for aurora-studio.
# TASK-000048: Portable ZIP Release Candidate Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\smoke_portable_zip.ps1
#
# Prerequisites:
#   .\scripts\create_portable_zip.ps1
#
# This script does NOT open a GUI window.
# This script does NOT install packages.
# This script does NOT call providers.
# This script does NOT execute plugins.
# This script does NOT require admin rights.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir     = $PSScriptRoot
$RepoRoot      = Split-Path $ScriptDir -Parent
$Version       = "0.1.0"
$RcTag         = "rc1"
$FolderName    = "AuroraStudio-v$Version-windows-portable"
$ZipBaseName   = "AuroraStudio-v$Version-$RcTag-windows-portable"
$RcDir         = Join-Path $RepoRoot "release-candidates"
$ZipPath       = Join-Path $RcDir "$ZipBaseName.zip"
$Sha256Path    = Join-Path $RcDir "$ZipBaseName.sha256"
$SmokeDir      = Join-Path $RcDir "_smoke\$ZipBaseName"
$ExtractedRoot = Join-Path $SmokeDir $FolderName
$SmokeBat      = Join-Path $ExtractedRoot "smoke_desktop.bat"

Write-Host "[aurora-studio] Smoke: portable ZIP release candidate v$Version-$RcTag"
Write-Host "[aurora-studio] ZIP: $ZipPath"

# Verify ZIP exists
if (-not (Test-Path $ZipPath)) {
    Write-Host ""
    Write-Host "ERROR: ZIP not found: $ZipPath"
    Write-Host "Create ZIP first:"
    Write-Host "    .\scripts\create_portable_zip.ps1"
    Write-Host ""
    exit 1
}

# Verify checksum file exists
if (-not (Test-Path $Sha256Path)) {
    Write-Host "ERROR: Checksum file not found: $Sha256Path"
    exit 1
}

# Verify checksum matches ZIP
Write-Host "[aurora-studio] Verifying SHA-256 checksum..."
$ActualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToLower()
$StoredLine = (Get-Content $Sha256Path -Raw).Trim()
$StoredHash = $StoredLine.Split(" ")[0].Trim()
if ($ActualHash -ne $StoredHash) {
    Write-Host "ERROR: Checksum mismatch."
    Write-Host "  Expected: $StoredHash"
    Write-Host "  Actual:   $ActualHash"
    exit 1
}
Write-Host "[aurora-studio] Checksum OK: $ActualHash"

# Extract ZIP to controlled smoke folder
Write-Host "[aurora-studio] Extracting ZIP to smoke folder..."
if (Test-Path $SmokeDir) { Remove-Item -Recurse -Force $SmokeDir }
New-Item -ItemType Directory -Path $SmokeDir | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $SmokeDir -Force

# Verify extracted top-level folder
if (-not (Test-Path $ExtractedRoot)) {
    Write-Host "ERROR: Expected top-level folder not found inside ZIP: $FolderName"
    exit 1
}
Write-Host "[aurora-studio] Extracted root: $ExtractedRoot"

# Verify required files and folders
$Required = @("app", "run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt", "data", "logs", "samples", "tmp")
foreach ($item in $Required) {
    $itemPath = Join-Path $ExtractedRoot $item
    if (-not (Test-Path $itemPath)) {
        Write-Host "ERROR: Missing from extracted ZIP: $item"
        exit 1
    }
}
Write-Host "[aurora-studio] Layout check passed."

# Run smoke_desktop.bat from extracted folder
Write-Host "[aurora-studio] Running smoke_desktop.bat from extracted folder..."
& cmd.exe /c $SmokeBat
$ExitCode = $LASTEXITCODE

# Cleanup smoke folder
Write-Host "[aurora-studio] Cleaning up smoke folder..."
Remove-Item -Recurse -Force $SmokeDir

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "[aurora-studio] ZIP smoke PASSED (exit 0)."
} else {
    Write-Host ""
    Write-Host "ERROR: ZIP smoke FAILED (exit $ExitCode)."
}

exit $ExitCode
