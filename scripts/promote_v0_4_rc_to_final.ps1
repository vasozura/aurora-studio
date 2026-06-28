# promote_v0_4_rc_to_final.ps1
# v0.4 RC to Final Promotion Script (PowerShell)
#
# Usage: .\promote_v0_4_rc_to_final.ps1
#
# Requirements:
#   - docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md must exist
#   - Decision must be GO or GO WITH KNOWN LIMITATIONS
#   - Script fails clearly for PENDING or NO-GO
#
# Does NOT build installer. Does NOT sign code.
# Does NOT download dependencies. Does NOT call provider APIs.
# Does NOT bundle secrets.

$ErrorActionPreference = "Stop"

$ReportPath = Join-Path $PSScriptRoot "..\docs\qa\V0_4_FINAL_RELEASE_DECISION_REPORT.md"
$ReportPath = Resolve-Path $ReportPath -ErrorAction SilentlyContinue

Write-Host "=== v0.4 RC to Final Promotion ==="

# Check decision report exists
if (-not $ReportPath -or -not (Test-Path $ReportPath)) {
    Write-Host "BLOCKED: Decision report not found." -ForegroundColor Red
    Write-Host "Expected: docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md" -ForegroundColor Red
    exit 1
}

Write-Host "Decision report found: $ReportPath"

# Read and check decision
$content = Get-Content $ReportPath -Raw

# Extract decision line
$decisionMatch = [regex]::Match($content, "Final Decision:\s*(\S+)")
if (-not $decisionMatch.Success) {
    $decisionMatch = [regex]::Match($content, "Decision:\s*(GO|NO-GO|PENDING|GO WITH KNOWN LIMITATIONS)")
}

if (-not $decisionMatch.Success) {
    Write-Host "BLOCKED: Could not parse decision from report." -ForegroundColor Red
    exit 1
}

$decision = $decisionMatch.Groups[1].Value.Trim()
Write-Host "Decision found: $decision"

if ($decision -eq "PENDING") {
    Write-Host "BLOCKED: Decision is PENDING. Promotion requires GO or GO WITH KNOWN LIMITATIONS." -ForegroundColor Red
    exit 1
}

if ($decision -eq "NO-GO") {
    Write-Host "BLOCKED: Decision is NO-GO. Promotion is not allowed." -ForegroundColor Red
    exit 1
}

if ($decision -ne "GO" -and $decision -notlike "GO*") {
    Write-Host "BLOCKED: Unrecognized decision '$decision'. Must be GO or GO WITH KNOWN LIMITATIONS." -ForegroundColor Red
    exit 1
}

Write-Host "Decision is $decision — promotion check passed." -ForegroundColor Green

# Check RC release notes exist
$rcNotes = Join-Path $PSScriptRoot "..\release-notes\AuroraStudio-v0.4.0-rc1.md"
if (-not (Test-Path $rcNotes)) {
    Write-Host "WARN: RC release notes not found at $rcNotes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Promotion check complete." -ForegroundColor Green
Write-Host "Next steps (manual):"
Write-Host "  1. Tag the source revision."
Write-Host "  2. Archive the release folder."
Write-Host "  3. Update release-notes/AuroraStudio-v0.4.0.md with final date and decision."
Write-Host ""
Write-Host "NOTE: This script does not build an installer, sign code,"
Write-Host "      download dependencies, call provider APIs, or bundle secrets."
exit 0
