@echo off
:: scripts\create_portable_zip.bat
::
:: Create the portable ZIP release candidate for aurora-studio.
:: TASK-000048: Portable ZIP Release Candidate Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\create_portable_zip.bat
::
:: Prerequisites:
::   scripts\build_windows_onefolder.bat
::   scripts\stage_windows_portable.bat
::   scripts\smoke_portable_folder.bat   (recommended before zipping)
::
:: This script does NOT build the EXE.
:: This script does NOT stage the portable folder.
:: This script does NOT create an installer.
:: This script does NOT install packages.
:: This script does NOT require admin rights.
::
:: Uses PowerShell internally for Compress-Archive and Get-FileHash.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set VERSION=0.1.0
set RC_TAG=rc1
set FOLDER_NAME=AuroraStudio-v%VERSION%-windows-portable
set ZIP_BASENAME=AuroraStudio-v%VERSION%-%RC_TAG%-windows-portable
set STAGED_FOLDER=%REPO_ROOT%\dist-portable\%FOLDER_NAME%
set RC_DIR=%REPO_ROOT%\release-candidates
set ZIP_PATH=%RC_DIR%\%ZIP_BASENAME%.zip
set SHA256_PATH=%RC_DIR%\%ZIP_BASENAME%.sha256

echo [aurora-studio] Create portable ZIP release candidate
echo [aurora-studio] Version: v%VERSION%-%RC_TAG%
echo [aurora-studio] Source:  %STAGED_FOLDER%
echo [aurora-studio] Output:  %ZIP_PATH%

:: Verify staged portable folder exists
if not exist "%STAGED_FOLDER%" (
    echo.
    echo ERROR: Staged portable folder not found: %STAGED_FOLDER%
    echo Run staging first:
    echo     scripts\stage_windows_portable.bat
    echo.
    exit /b 1
)

:: Create release-candidates directory
if not exist "%RC_DIR%" mkdir "%RC_DIR%"

:: Remove prior controlled outputs only
if exist "%ZIP_PATH%"    del /f /q "%ZIP_PATH%"
if exist "%SHA256_PATH%" del /f /q "%SHA256_PATH%"

:: Create ZIP archive using PowerShell
echo [aurora-studio] Creating ZIP archive...
powershell -NoProfile -NonInteractive -Command ^
  "Compress-Archive -Path '%STAGED_FOLDER%' -DestinationPath '%ZIP_PATH%' -CompressionLevel Optimal"
if errorlevel 1 (
    echo ERROR: Failed to create ZIP archive.
    exit /b 1
)
if not exist "%ZIP_PATH%" (
    echo ERROR: ZIP was not created.
    exit /b 1
)
echo [aurora-studio] ZIP created: %ZIP_PATH%

:: Create SHA-256 checksum using PowerShell
echo [aurora-studio] Computing SHA-256 checksum...
powershell -NoProfile -NonInteractive -Command ^
  "$h = (Get-FileHash -Path '%ZIP_PATH%' -Algorithm SHA256).Hash.ToLower(); " ^
  "Set-Content -Path '%SHA256_PATH%' -Value ($h + '  %ZIP_BASENAME%.zip') -Encoding UTF8; " ^
  "Write-Host ('[aurora-studio] Checksum: ' + $h)"
if errorlevel 1 (
    echo ERROR: Failed to compute checksum.
    exit /b 1
)

echo.
echo [aurora-studio] Release candidate created.
echo [aurora-studio] Run smoke: scripts\smoke_portable_zip.bat

endlocal
exit /b 0
