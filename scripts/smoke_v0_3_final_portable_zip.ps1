# Smoke test the Aurora Studio v0.3.0 final portable ZIP.

param(
    [string]$ReleasesDir = ".\releases",
    [string]$FinalZip = "AuroraStudio-v0.3.0-windows-portable.zip"
)

$ErrorActionPreference = "Stop"
$ZipPath = Join-Path $ReleasesDir $FinalZip
$ShaPath = "$ZipPath.sha256"

if (-not (Test-Path $ZipPath)) {
    Write-Error "FAIL: Final ZIP not found: $ZipPath"
    exit 1
}
if (-not (Test-Path $ShaPath)) {
    Write-Error "FAIL: SHA256 not found: $ShaPath"
    exit 1
}

$expectedLine = Get-Content $ShaPath
$expectedHash = ($expectedLine -split "\s+")[0].ToUpper()
$actualHash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToUpper()
if ($expectedHash -ne $actualHash) {
    Write-Error "FAIL: SHA256 mismatch. Expected: $expectedHash  Got: $actualHash"
    exit 1
}
Write-Host "SHA256 OK: $actualHash"

$TempDir = Join-Path $env:TEMP "aurora_final_smoke_$(Get-Random)"
Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force

$required = @("run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt")
foreach ($file in $required) {
    if (-not (Test-Path (Join-Path $TempDir $file))) {
        Remove-Item -Recurse -Force $TempDir
        Write-Error "FAIL: Required file missing: $file"
        exit 1
    }
}
Remove-Item -Recurse -Force $TempDir

Write-Host "Smoke PASS: final ZIP is valid."
Write-Host "Done."
