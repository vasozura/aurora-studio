# Promote Aurora Studio v0.3 RC to final release.
# Requires decision report to exist and decision to be GO or GO WITH KNOWN LIMITATIONS.
# Fails clearly if decision is PENDING or NO-GO.

param(
    [string]$DecisionReport = ".\docs\qa\V0_3_FINAL_RELEASE_DECISION_REPORT.md",
    [string]$RcZip = ".\release-candidates\AuroraStudio-v0.3.0-rc1-windows-portable.zip",
    [string]$RcSha = ".\release-candidates\AuroraStudio-v0.3.0-rc1-windows-portable.zip.sha256",
    [string]$ReleasesDir = ".\releases",
    [string]$FinalZip = "AuroraStudio-v0.3.0-windows-portable.zip"
)

$ErrorActionPreference = "Stop"

# Check decision report exists
if (-not (Test-Path $DecisionReport)) {
    Write-Error "BLOCKED: Decision report not found: $DecisionReport"
    exit 2
}

# Read decision from report
$reportContent = Get-Content $DecisionReport -Raw
if ($reportContent -match "Decision.*PENDING" -or $reportContent -match "\*\*PENDING\*\*") {
    Write-Error "BLOCKED: Decision is PENDING. Cannot promote to final release."
    exit 2
}
if ($reportContent -match "Decision.*NO-GO" -or $reportContent -match "\*\*NO-GO\*\*") {
    Write-Error "BLOCKED: Decision is NO-GO. Cannot promote to final release."
    exit 2
}

# Check RC ZIP exists
if (-not (Test-Path $RcZip)) {
    Write-Error "ERROR: RC ZIP not found: $RcZip"
    exit 1
}
if (-not (Test-Path $RcSha)) {
    Write-Error "ERROR: RC SHA256 not found: $RcSha"
    exit 1
}

# Create releases dir
if (-not (Test-Path $ReleasesDir)) {
    New-Item -ItemType Directory -Force -Path $ReleasesDir | Out-Null
}

$FinalZipPath = Join-Path $ReleasesDir $FinalZip
$FinalShaPath = Join-Path $ReleasesDir "$FinalZip.sha256"

Copy-Item -Path $RcZip -Destination $FinalZipPath -Force
$hash = (Get-FileHash -Path $FinalZipPath -Algorithm SHA256).Hash
"$hash  $FinalZip" | Out-File -FilePath $FinalShaPath -Encoding utf8

Write-Host "Promoted: $FinalZipPath"
Write-Host "SHA256:   $FinalShaPath ($hash)"
Write-Host "Done."
