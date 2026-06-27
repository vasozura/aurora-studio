# Aurora Studio - Headless Smoke
# Usage: .\scripts\smoke_desktop.ps1
# Run from repository root or scripts folder.
# Stops on first failure.

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "src"))) {
    $RepoRoot = $PSScriptRoot
}

$env:PYTHONPATH = Join-Path $RepoRoot "src"
Set-Location $RepoRoot

Write-Host "[aurora-studio] Running headless smoke..." -ForegroundColor Cyan

# Clean demo project to avoid duplicate-project errors
$DemoPath = Join-Path $RepoRoot "tmp-demo-project"
if (Test-Path $DemoPath) {
    Remove-Item -Recurse -Force $DemoPath
    Write-Host "[aurora-studio] Removed existing tmp-demo-project" -ForegroundColor DarkGray
}

function Run-Step {
    param([string]$Label, [string[]]$Args)
    Write-Host "[aurora-studio] $Label" -ForegroundColor DarkCyan
    & python @Args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[aurora-studio] FAILED: $Label (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Run-Step "desktop --headless-smoke" @("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
Run-Step "cli smoke"                @("-m", "aurora_studio.cli", "smoke")
Run-Step "cli create-demo"          @("-m", "aurora_studio.cli", "create-demo", "--path", ".\tmp-demo-project", "--title", "Demo Project")
Run-Step "cli validate-bundle"      @("-m", "aurora_studio.cli", "validate-bundle", "--path", ".\tmp-demo-project")
Run-Step "cli rehydrate-bundle"     @("-m", "aurora_studio.cli", "rehydrate-bundle", "--path", ".\tmp-demo-project")

Write-Host "[aurora-studio] All smoke checks passed." -ForegroundColor Green
exit 0
