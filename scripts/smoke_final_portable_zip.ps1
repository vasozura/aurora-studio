# smoke_final_portable_zip.ps1
# Verifies and smoke-tests the final promoted v0.1.0 portable ZIP.
# Does not rebuild. Does not install packages. Does not open GUI. Does not call providers.

$ErrorActionPreference = "Stop"

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$RelDir    = Join-Path $RepoRoot "releases"
$FinalZip  = Join-Path $RelDir "AuroraStudio-v0.1.0-windows-portable.zip"
$FinalHash = Join-Path $RelDir "AuroraStudio-v0.1.0-windows-portable.sha256"
$SmokeDir  = Join-Path $RelDir "_smoke\AuroraStudio-v0.1.0-windows-portable"
$ExtractedFolder = "AuroraStudio-v0.1.0-windows-portable"

# --- 1. Verify final ZIP ---
if (-not (Test-Path $FinalZip)) {
    Write-Host "ERROR: Final ZIP not found: $FinalZip"
    Write-Host "Run scripts\promote_rc_to_final.bat first."
    exit 1
}
if (-not (Test-Path $FinalHash)) {
    Write-Host "ERROR: Final checksum not found: $FinalHash"
    exit 1
}

# --- 2. Verify checksum ---
Write-Host "Verifying final ZIP checksum..."
$ActualHash = (Get-FileHash -Path $FinalZip -Algorithm SHA256).Hash.ToLower()
$StoredLine = (Get-Content $FinalHash)[0]
$StoredHash = $StoredLine.Split(" ")[0].ToLower()
if ($ActualHash -ne $StoredHash) {
    Write-Host "ERROR: Final ZIP checksum mismatch."
    Write-Host "  Actual:  $ActualHash"
    Write-Host "  Stored:  $StoredHash"
    exit 1
}
Write-Host "Checksum verified: $ActualHash"

# --- 3. Clean prior smoke folder ---
if (Test-Path $SmokeDir) {
    Remove-Item -Recurse -Force $SmokeDir
}
New-Item -ItemType Directory -Path $SmokeDir -Force | Out-Null

# --- 4. Extract ZIP ---
Write-Host "Extracting final ZIP to smoke folder..."
Expand-Archive -Path $FinalZip -DestinationPath $SmokeDir -Force

# --- 5. Verify extracted top-level folder ---
$ExtractedTop = Join-Path $SmokeDir $ExtractedFolder
if (-not (Test-Path $ExtractedTop)) {
    Write-Host "ERROR: Extracted top-level folder not found: $ExtractedTop"
    exit 1
}
Write-Host "Extracted folder found: $ExtractedFolder"

# --- 6. Verify required contents ---
$Required = @("app", "run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt", "data", "logs", "samples", "tmp")
foreach ($item in $Required) {
    $fullPath = Join-Path $ExtractedTop $item
    if (-not (Test-Path $fullPath)) {
        Write-Host "ERROR: Required item missing from extracted ZIP: $item"
        Remove-Item -Recurse -Force $SmokeDir
        exit 1
    }
}
Write-Host "All required items present."

# --- 7. Run smoke ---
$SmokeBat = Join-Path $ExtractedTop "smoke_desktop.bat"
Write-Host "Running smoke: $SmokeBat"
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$SmokeBat`"" -NoNewWindow -Wait -PassThru
$SmokeExit = $proc.ExitCode

# --- 8. Clean up ---
Remove-Item -Recurse -Force $SmokeDir

if ($SmokeExit -ne 0) {
    Write-Host "ERROR: Final ZIP smoke failed with exit code $SmokeExit"
    exit $SmokeExit
}

Write-Host ""
Write-Host "Final ZIP smoke: PASSED"
