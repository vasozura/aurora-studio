@echo off
:: scripts\build_windows_onefolder.bat
::
:: Build aurora-studio as a Windows one-folder portable app using PyInstaller.
:: TASK-000046: PyInstaller Build Smoke Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\build_windows_onefolder.bat
::
:: Prerequisites:
::   python -m pip install -r build\requirements-build.txt
::
:: This script does NOT install packages automatically.
:: This script does NOT require admin rights.
:: This script does NOT modify system PATH.

setlocal enabledelayedexpansion

:: Resolve repository root from script location (%~dp0 = scripts\)
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..

echo [aurora-studio] Build: Windows one-folder portable app
echo [aurora-studio] Repo root: %REPO_ROOT%

:: Set PYTHONPATH for current process only
set PYTHONPATH=%REPO_ROOT%\src

:: Check PyInstaller is available
echo [aurora-studio] Checking PyInstaller availability...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller is not installed.
    echo Install build dependencies first:
    echo     python -m pip install -r build\requirements-build.txt
    echo.
    exit /b 1
)

for /f "tokens=*" %%v in ('python -m PyInstaller --version 2^>^&1') do (
    echo [aurora-studio] PyInstaller version: %%v
    goto :version_done
)
:version_done

:: Paths
set SPEC_FILE=%REPO_ROOT%\build\pyinstaller\aurora_studio_desktop.spec
set WORK_PATH=%REPO_ROOT%\build\pyinstaller_work
set DIST_PATH=%REPO_ROOT%\dist
set OUTPUT_DIR=%REPO_ROOT%\dist\AuroraStudio

:: Clean previous build output (controlled paths only)
echo [aurora-studio] Cleaning previous build output...
if exist "%WORK_PATH%"  rmdir /s /q "%WORK_PATH%"
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"

:: Run PyInstaller
echo [aurora-studio] Running PyInstaller (one-folder mode)...
python -m PyInstaller "%SPEC_FILE%" --distpath "%DIST_PATH%" --workpath "%WORK_PATH%" --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo [aurora-studio] Build succeeded.
echo [aurora-studio] Output: %OUTPUT_DIR%
echo [aurora-studio] Run smoke: scripts\smoke_built_app.bat

endlocal
exit /b 0
