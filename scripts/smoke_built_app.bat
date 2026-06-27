@echo off
:: scripts\smoke_built_app.bat
::
:: Smoke-test the built one-folder aurora-studio portable app.
:: TASK-000046: PyInstaller Build Smoke Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\smoke_built_app.bat
::
:: Prerequisites:
::   Run scripts\build_windows_onefolder.bat first.
::
:: This script does NOT open a GUI window.
:: This script does NOT install packages.
:: This script does NOT call providers.
:: This script does NOT execute plugins.
:: This script does NOT require admin rights.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set EXE_PATH=%REPO_ROOT%\dist\AuroraStudio\AuroraStudio.exe

echo [aurora-studio] Smoke: built one-folder app
echo [aurora-studio] EXE path: %EXE_PATH%

:: Confirm the build artifact exists
if not exist "%EXE_PATH%" (
    echo.
    echo ERROR: Built executable not found: %EXE_PATH%
    echo Run the build first:
    echo     scripts\build_windows_onefolder.bat
    echo.
    exit /b 1
)

:: Run headless smoke (no window, JSON output, exit 0)
echo [aurora-studio] Running headless smoke...
"%EXE_PATH%" --headless-smoke

if errorlevel 1 (
    echo.
    echo ERROR: Smoke FAILED.
    exit /b 1
)

echo.
echo [aurora-studio] Smoke PASSED (exit 0).

endlocal
exit /b 0
