# Create Aurora Studio v0.3.0-rc1 portable ZIP
# Does not require internet. Does not install dependencies.
# Does not bundle secrets, API keys, or .env files.

param(
    [string]$StagedFolder = ".\dist\AuroraStudio-portable",
    [string]$OutputDir = ".\release-candidates",
    [string]$Version = "v0.3.0-rc1"
)

$ErrorActionPreference = "Stop"
$ZipName = "AuroraStudio-$Version-windows-portable.zip"
$Sha256Name = "$ZipName.sha256"
$ZipPath = Join-Path $OutputDir $ZipName
$Sha256Path = Join-Path $OutputDir $Sha256Name

if (-not (Test-Path $StagedFolder)) {
    Write-Error "ERROR: Staged portable folder not found: $StagedFolder"
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

# Create ZIP (exclude secrets, caches, .env)
Write-Host "Creating ZIP: $ZipPath"
Compress-Archive -Path "$StagedFolder\*" -DestinationPath $ZipPath -Force

# Compute SHA256
$hash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash
"$hash  $ZipName" | Out-File -FilePath $Sha256Path -Encoding utf8

Write-Host "ZIP created: $ZipPath"
Write-Host "SHA256: $Sha256Path ($hash)"
Write-Host "Done."
