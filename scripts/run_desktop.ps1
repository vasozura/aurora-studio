# Aurora Studio - Run Desktop Shell
# Usage: .\scripts\run_desktop.ps1
# Run from repository root or scripts folder.

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "src"))) {
    $RepoRoot = $PSScriptRoot
}

$env:PYTHONPATH = Join-Path $RepoRoot "src"
Set-Location $RepoRoot

Write-Host "[aurora-studio] Starting desktop shell..." -ForegroundColor Cyan
Write-Host "[aurora-studio] PYTHONPATH=$env:PYTHONPATH" -ForegroundColor DarkGray

python -m aurora_studio.ui.desktop_shell
exit $LASTEXITCODE
