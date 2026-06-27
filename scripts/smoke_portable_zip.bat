@echo off
:: scripts\smoke_portable_zip.bat
::
:: Smoke-test the portable ZIP release candidate for aurora-studio.
:: TASK-000048: Portable ZIP Release Candidate Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\smoke_portable_zip.bat
::
:: Prerequisites:
::   scripts\create_portable_zip.bat
::
:: This script does NOT open a GUI window.
:: This script does NOT install packages.
:: This script does NOT call providers.
:: This script does NOT execute plugins.
:: This script does NOT require admin rights.
::
:: Uses PowerShell internally for Expand-Archive and Get-FileHash.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set VERSION=0.1.0
set RC_TAG=rc1
set FOLDER_NAME=AuroraStudio-v%VERSION%-windows-portable
set ZIP_BASENAME=AuroraStudio-v%VERSION%-%RC_TAG%-windows-portable
set RC_DIR=%REPO_ROOT%\release-candidates
set ZIP_PATH=%RC_DIR%\%ZIP_BASENAME%.zip
set SHA256_PATH=%RC_DIR%\%ZIP_BASENAME%.sha256
set SMOKE_DIR=%RC_DIR%\_smoke\%ZIP_BASENAME%
set EXTRACTED_ROOT=%SMOKE_DIR%\%FOLDER_NAME%
set SMOKE_BAT=%EXTRACTED_ROOT%\smoke_desktop.bat

echo [aurora-studio] Smoke: portable ZIP release candidate v%VERSION%-%RC_TAG%
echo [aurora-studio] ZIP: %ZIP_PATH%

:: Verify ZIP exists
if not exist "%ZIP_PATH%" (
    echo.
    echo ERROR: ZIP not found: %ZIP_PATH%
    echo Create ZIP first:
    echo     scripts\create_portable_zip.bat
    echo.
    exit /b 1
)

:: Verify checksum file exists
if not exist "%SHA256_PATH%" (
    echo ERROR: Checksum file not found: %SHA256_PATH%
    exit /b 1
)

:: Verify checksum using PowerShell
echo [aurora-studio] Verifying SHA-256 checksum...
powershell -NoProfile -NonInteractive -Command ^
  "$actual = (Get-FileHash -Path '%ZIP_PATH%' -Algorithm SHA256).Hash.ToLower(); " ^
  "$stored = ((Get-Content '%SHA256_PATH%' -Raw).Trim().Split(' ')[0]).ToLower(); " ^
  "if ($actual -ne $stored) { Write-Host ('ERROR: Checksum mismatch. Expected: ' + $stored + ' Actual: ' + $actual); exit 1 } " ^
  "Write-Host ('[aurora-studio] Checksum OK: ' + $actual)"
if errorlevel 1 (
    echo ERROR: Checksum verification failed.
    exit /b 1
)

:: Extract ZIP to controlled smoke folder
echo [aurora-studio] Extracting ZIP to smoke folder...
if exist "%SMOKE_DIR%" rmdir /s /q "%SMOKE_DIR%"
mkdir "%SMOKE_DIR%"
powershell -NoProfile -NonInteractive -Command ^
  "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%SMOKE_DIR%' -Force"
if errorlevel 1 (
    echo ERROR: Failed to extract ZIP.
    exit /b 1
)

:: Verify extracted top-level folder
if not exist "%EXTRACTED_ROOT%" (
    echo ERROR: Expected top-level folder not found inside ZIP: %FOLDER_NAME%
    exit /b 1
)
echo [aurora-studio] Extracted root: %EXTRACTED_ROOT%

:: Verify required files and folders
for %%I in (app run_desktop.bat smoke_desktop.bat README.txt NOTICE.txt data logs samples tmp) do (
    if not exist "%EXTRACTED_ROOT%\%%I" (
        echo ERROR: Missing from extracted ZIP: %%I
        exit /b 1
    )
)
echo [aurora-studio] Layout check passed.

:: Run smoke_desktop.bat from extracted folder
echo [aurora-studio] Running smoke_desktop.bat from extracted folder...
call "%SMOKE_BAT%"
set SMOKE_EXIT=%errorlevel%

:: Cleanup smoke folder
echo [aurora-studio] Cleaning up smoke folder...
rmdir /s /q "%SMOKE_DIR%"

if %SMOKE_EXIT% neq 0 (
    echo.
    echo ERROR: ZIP smoke FAILED.
    exit /b 1
)

echo.
echo [aurora-studio] ZIP smoke PASSED (exit 0).

endlocal
exit /b 0
