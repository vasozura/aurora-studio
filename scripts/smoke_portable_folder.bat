@echo off
:: scripts\smoke_portable_folder.bat
::
:: Smoke-test the staged Windows portable folder for aurora-studio.
:: TASK-000047: Windows Portable Folder Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\smoke_portable_folder.bat
::
:: Prerequisites:
::   Run scripts\build_windows_onefolder.bat first.
::   Run scripts\stage_windows_portable.bat first.
::
:: This script does NOT open a GUI window.
:: This script does NOT install packages.
:: This script does NOT call providers.
:: This script does NOT execute plugins.
:: This script does NOT require admin rights.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set VERSION=0.1.0
set FOLDER_NAME=AuroraStudio-v%VERSION%-windows-portable
set STAGING_DIR=%REPO_ROOT%\dist-portable\%FOLDER_NAME%
set STAGED_EXE=%STAGING_DIR%\app\AuroraStudio\AuroraStudio.exe
set SMOKE_BAT=%STAGING_DIR%\smoke_desktop.bat

echo [aurora-studio] Smoke: staged portable folder v%VERSION%
echo [aurora-studio] Folder: %STAGING_DIR%

:: Verify staged folder exists
if not exist "%STAGING_DIR%" (
    echo.
    echo ERROR: Staged portable folder not found: %STAGING_DIR%
    echo Run staging first:
    echo     scripts\stage_windows_portable.bat
    echo.
    exit /b 1
)

:: Verify staged executable exists
if not exist "%STAGED_EXE%" (
    echo.
    echo ERROR: Staged executable not found: %STAGED_EXE%
    echo Re-run build and staging:
    echo     scripts\build_windows_onefolder.bat
    echo     scripts\stage_windows_portable.bat
    echo.
    exit /b 1
)

:: Run the portable folder's own smoke script
echo [aurora-studio] Running portable smoke via smoke_desktop.bat...
call "%SMOKE_BAT%"

if errorlevel 1 (
    echo.
    echo ERROR: Portable smoke FAILED.
    exit /b 1
)

echo.
echo [aurora-studio] Portable smoke PASSED (exit 0).

endlocal
exit /b 0
