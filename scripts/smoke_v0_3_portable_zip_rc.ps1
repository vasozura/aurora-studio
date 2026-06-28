# Smoke test the v0.3.0-rc1 portable ZIP release candidate
# Validates ZIP exists, SHA256 matches, and required files are present.

param(
    [string]$RcDir = ".\release-candidates",
    [string]$Version = "v0.3.0-rc1"
)

$ErrorActionPreference = "Stop"
$ZipName = "AuroraStudio-$Version-windows-portable.zip"
$Sha256Name = "$ZipName.sha256"
$ZipPath = Join-Path $RcDir $ZipName
$Sha256Path = Join-Path $RcDir $Sha256Name

# Validate ZIP exists
if (-not (Test-Path $ZipPath)) {
    Write-Error "FAIL: ZIP not found: $ZipPath"
    exit 1
}

# Validate SHA256 file exists
if (-not (Test-Path $Sha256Path)) {
    Write-Error "FAIL: SHA256 file not found: $Sha256Path"
    exit 1
}

# Validate checksum
$expectedLine = Get-Content $Sha256Path
$expectedHash = ($expectedLine -split "\s+")[0].ToUpper()
$actualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpper()
if ($expectedHash -ne $actualHash) {
    Write-Error "FAIL: SHA256 mismatch. Expected: $expectedHash  Got: $actualHash"
    exit 1
}
Write-Host "SHA256 OK: $actualHash"

# Extract to temp and validate top-level files
$TempDir = Join-Path $env:TEMP "aurora_rc_smoke_$(Get-Random)"
Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force

$required = @("run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt")
foreach ($file in $required) {
    $fp = Join-Path $TempDir $file
    if (-not (Test-Path $fp)) {
        Remove-Item -Recurse -Force $TempDir
        Write-Error "FAIL: Required file missing in ZIP: $file"
        exit 1
    }
}
Remove-Item -Recurse -Force $TempDir

Write-Host "Smoke PASS: all required files present in ZIP."
Write-Host "Done."
