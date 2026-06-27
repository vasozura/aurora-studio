# scripts/create_portable_zip.ps1
#
# Create the portable ZIP release candidate for aurora-studio.
# TASK-000048: Portable ZIP Release Candidate Pack
#
# Usage (from repo root or scripts folder):
#   .\scripts\create_portable_zip.ps1
#
# Prerequisites:
#   .\scripts\build_windows_onefolder.ps1
#   .\scripts\stage_windows_portable.ps1
#   .\scripts\smoke_portable_folder.ps1   (recommended before zipping)
#
# This script does NOT build the EXE.
# This script does NOT stage the portable folder.
# This script does NOT create an installer.
# This script does NOT install packages.
# This script does NOT require admin rights.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir     = $PSScriptRoot
$RepoRoot      = Split-Path $ScriptDir -Parent
$Version       = "0.1.0"
$RcTag         = "rc1"
$FolderName    = "AuroraStudio-v$Version-windows-portable"
$ZipBaseName   = "AuroraStudio-v$Version-$RcTag-windows-portable"
$StagedFolder  = Join-Path $RepoRoot "dist-portable\$FolderName"
$RcDir         = Join-Path $RepoRoot "release-candidates"
$ZipPath       = Join-Path $RcDir "$ZipBaseName.zip"
$Sha256Path    = Join-Path $RcDir "$ZipBaseName.sha256"

Write-Host "[aurora-studio] Create portable ZIP release candidate"
Write-Host "[aurora-studio] Version: v$Version-$RcTag"
Write-Host "[aurora-studio] Source:  $StagedFolder"
Write-Host "[aurora-studio] Output:  $ZipPath"

# Verify staged portable folder exists
if (-not (Test-Path $StagedFolder)) {
    Write-Host ""
    Write-Host "ERROR: Staged portable folder not found: $StagedFolder"
    Write-Host "Run staging first:"
    Write-Host "    .\scripts\stage_windows_portable.ps1"
    Write-Host ""
    exit 1
}

# Create release-candidates output directory
if (-not (Test-Path $RcDir)) {
    New-Item -ItemType Directory -Path $RcDir | Out-Null
}

# Remove prior controlled outputs only
if (Test-Path $ZipPath)    { Remove-Item -Force $ZipPath }
if (Test-Path $Sha256Path) { Remove-Item -Force $Sha256Path }

# Create ZIP archive
# Compress-Archive requires the parent of the folder to get the folder as top-level entry
Write-Host "[aurora-studio] Creating ZIP archive..."
$StagedParent = Split-Path $StagedFolder -Parent
Compress-Archive -Path $StagedFolder -DestinationPath $ZipPath -CompressionLevel Optimal

if (-not (Test-Path $ZipPath)) {
    Write-Host "ERROR: ZIP was not created."
    exit 1
}

$ZipSize = (Get-Item $ZipPath).Length
Write-Host "[aurora-studio] ZIP created: $ZipPath ($ZipSize bytes)"

# Create SHA-256 checksum
Write-Host "[aurora-studio] Computing SHA-256 checksum..."
$Hash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToLower()
$ChecksumLine = "$Hash  $ZipBaseName.zip"
Set-Content -Path $Sha256Path -Value $ChecksumLine -Encoding UTF8

Write-Host "[aurora-studio] Checksum: $Hash"
Write-Host "[aurora-studio] Checksum file: $Sha256Path"
Write-Host ""
Write-Host "[aurora-studio] Release candidate created."
Write-Host "[aurora-studio] Run smoke: .\scripts\smoke_portable_zip.ps1"

exit 0
