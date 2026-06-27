# Aurora Studio - Run Tests
# Usage: .\scripts\run_tests.ps1
# Run from repository root or scripts folder.

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "src"))) {
    $RepoRoot = $PSScriptRoot
}

$env:PYTHONPATH = Join-Path $RepoRoot "src"
Set-Location $RepoRoot

Write-Host "[aurora-studio] Running tests..." -ForegroundColor Cyan
Write-Host "[aurora-studio] PYTHONPATH=$env:PYTHONPATH" -ForegroundColor DarkGray

python -m unittest
exit $LASTEXITCODE
