# promote_rc_to_final.ps1
# Promotes the v0.1.0-rc1 release candidate ZIP to the final v0.1.0 artifact.
# Requires: docs/qa/V0_1_FINAL_RELEASE_DECISION_REPORT.md must contain Decision: GO
#           or Decision: GO WITH KNOWN LIMITATIONS
# Does not rebuild. Does not re-stage. Does not install packages. Does not code-sign.

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$DecisionReport = Join-Path $RepoRoot "docs\qa\V0_1_FINAL_RELEASE_DECISION_REPORT.md"
$RcZip   = Join-Path $RepoRoot "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip"
$RcHash  = Join-Path $RepoRoot "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256"
$RelDir  = Join-Path $RepoRoot "releases"
$FinalZip  = Join-Path $RelDir "AuroraStudio-v0.1.0-windows-portable.zip"
$FinalHash = Join-Path $RelDir "AuroraStudio-v0.1.0-windows-portable.sha256"

# --- 1. Check decision report ---
if (-not (Test-Path $DecisionReport)) {
    Write-Host "ERROR: Decision report not found: $DecisionReport"
    Write-Host "Run QA review and fill in docs\qa\V0_1_FINAL_RELEASE_DECISION_REPORT.md first."
    exit 1
}
$ReportContent = Get-Content $DecisionReport -Raw
$IsGo = $ReportContent -match "Decision: GO$" -or $ReportContent -match "Decision: GO WITH KNOWN LIMITATIONS"
$IsPending = $ReportContent -match "Decision: PENDING"
$IsNoGo = $ReportContent -match "Decision: NO-GO"

if ($IsPending) {
    Write-Host "ERROR: Decision report is PENDING. Final promotion is blocked."
    Write-Host "Complete QA review and update the decision report before promoting."
    exit 1
}
if ($IsNoGo) {
    Write-Host "ERROR: Decision report is NO-GO. Final promotion is forbidden."
    exit 1
}
if (-not $IsGo) {
    Write-Host "ERROR: Decision report does not contain GO or GO WITH KNOWN LIMITATIONS."
    Write-Host "Update docs\qa\V0_1_FINAL_RELEASE_DECISION_REPORT.md to an approved decision."
    exit 1
}
Write-Host "Decision check: PASSED (GO or GO WITH KNOWN LIMITATIONS found)"

# --- 2. Verify RC artifacts ---
if (-not (Test-Path $RcZip)) {
    Write-Host "ERROR: RC ZIP not found: $RcZip"
    Write-Host "Run scripts\create_portable_zip.bat first."
    exit 1
}
if (-not (Test-Path $RcHash)) {
    Write-Host "ERROR: RC checksum not found: $RcHash"
    exit 1
}

# --- 3. Verify RC checksum ---
Write-Host "Verifying RC checksum..."
$ActualHash = (Get-FileHash -Path $RcZip -Algorithm SHA256).Hash.ToLower()
$StoredLine = (Get-Content $RcHash)[0]
$StoredHash = $StoredLine.Split(" ")[0].ToLower()
if ($ActualHash -ne $StoredHash) {
    Write-Host "ERROR: RC checksum mismatch."
    Write-Host "  Actual:  $ActualHash"
    Write-Host "  Stored:  $StoredHash"
    exit 1
}
Write-Host "RC checksum verified: $ActualHash"

# --- 4. Create releases/ directory ---
if (-not (Test-Path $RelDir)) {
    New-Item -ItemType Directory -Path $RelDir | Out-Null
    Write-Host "Created: releases\"
}

# --- 5. Clean prior final outputs ---
if (Test-Path $FinalZip)  { Remove-Item $FinalZip  -Force }
if (Test-Path $FinalHash) { Remove-Item $FinalHash -Force }

# --- 6. Copy RC ZIP to final name ---
Write-Host "Promoting RC to final..."
Copy-Item -Path $RcZip -Destination $FinalZip
Write-Host "Copied: $FinalZip"

# --- 7. Create final checksum ---
$FinalActual = (Get-FileHash -Path $FinalZip -Algorithm SHA256).Hash.ToLower()
$FinalBaseName = [System.IO.Path]::GetFileName($FinalZip)
"$FinalActual  $FinalBaseName" | Set-Content -Path $FinalHash -Encoding ASCII
Write-Host "Final SHA-256: $FinalActual"

# --- 8. Verify final checksum ---
$VerifyLine = (Get-Content $FinalHash)[0]
$VerifyHash = $VerifyLine.Split(" ")[0].ToLower()
if ($FinalActual -ne $VerifyHash) {
    Write-Host "ERROR: Final checksum verification failed."
    exit 1
}
Write-Host "Final checksum verified."

Write-Host ""
Write-Host "Promotion complete."
Write-Host "  $FinalZip"
Write-Host "  $FinalHash"
