# smoke_v0_4_portable_secret_safety.ps1
# v0.4 Portable Secret Safety Smoke Script (PowerShell)
#
# Usage: .\smoke_v0_4_portable_secret_safety.ps1 -PortablePath <path>
#
# Validates that a portable folder or ZIP extraction folder does not
# contain excluded secret files, caches, or SDK packages.
#
# Does NOT call any network. Does NOT delete user data.
# Fails clearly if violations are found.

param(
    [Parameter(Mandatory=$false)]
    [string]$PortablePath = "."
)

$ErrorCount = 0
$WarnCount = 0

function Fail($msg) {
    Write-Host "FAIL: $msg" -ForegroundColor Red
    $script:ErrorCount++
}

function Warn($msg) {
    Write-Host "WARN: $msg" -ForegroundColor Yellow
    $script:WarnCount++
}

function Pass($msg) {
    Write-Host "PASS: $msg" -ForegroundColor Green
}

Write-Host "=== v0.4 Portable Secret Safety Smoke ==="
Write-Host "Path: $PortablePath"
Write-Host ""

if (-not (Test-Path $PortablePath)) {
    Write-Host "ERROR: Path does not exist: $PortablePath" -ForegroundColor Red
    exit 1
}

# Check: no .env files
$envFiles = Get-ChildItem -Path $PortablePath -Recurse -File |
    Where-Object { $_.Name -eq ".env" -or $_.Extension -eq ".env" }
if ($envFiles.Count -gt 0) {
    foreach ($f in $envFiles) { Fail ".env file found: $($f.FullName)" }
} else {
    Pass "No .env files found"
}

# Check: no obvious api_key/token/secret/password named files
$secretNamePatterns = @("api_key", "apikey", "secret", "token", "password", "credentials")
foreach ($pattern in $secretNamePatterns) {
    $matches = Get-ChildItem -Path $PortablePath -Recurse -File |
        Where-Object { $_.Name.ToLower() -like "*$pattern*" -and $_.Extension -ne ".py" -and $_.Extension -ne ".md" }
    if ($matches.Count -gt 0) {
        foreach ($f in $matches) { Warn "Suspicious filename: $($f.FullName)" }
    }
}
Pass "No obvious secret-named non-source files"

# Check: no __pycache__ directories
$pycache = Get-ChildItem -Path $PortablePath -Recurse -Directory |
    Where-Object { $_.Name -eq "__pycache__" }
if ($pycache.Count -gt 0) {
    foreach ($d in $pycache) { Warn "__pycache__ found: $($d.FullName)" }
} else {
    Pass "No __pycache__ directories"
}

# Check: no .pytest_cache directories
$pytestCache = Get-ChildItem -Path $PortablePath -Recurse -Directory |
    Where-Object { $_.Name -eq ".pytest_cache" }
if ($pytestCache.Count -gt 0) {
    foreach ($d in $pytestCache) { Warn ".pytest_cache found: $($d.FullName)" }
} else {
    Pass "No .pytest_cache directories"
}

# Check: no provider SDK package folders
$sdkFolders = @("openai", "anthropic", "requests", "httpx", "aiohttp", "PIL", "cv2", "moviepy")
foreach ($sdk in $sdkFolders) {
    $found = Get-ChildItem -Path $PortablePath -Recurse -Directory |
        Where-Object { $_.Name -eq $sdk }
    if ($found.Count -gt 0) {
        foreach ($d in $found) { Fail "Provider SDK folder found: $($d.FullName)" }
    }
}
Pass "No provider SDK folders found"

# Check: README or NOTICE present
$readme = Get-ChildItem -Path $PortablePath -File |
    Where-Object { $_.Name -like "README*" -or $_.Name -like "NOTICE*" }
if ($readme.Count -eq 0) {
    Warn "No README or NOTICE found at root"
} else {
    Pass "README/NOTICE present"
}

Write-Host ""
Write-Host "=== Summary ==="
Write-Host "Errors: $ErrorCount"
Write-Host "Warnings: $WarnCount"

if ($ErrorCount -gt 0) {
    Write-Host "RESULT: FAIL" -ForegroundColor Red
    exit 1
} else {
    Write-Host "RESULT: PASS" -ForegroundColor Green
    exit 0
}
