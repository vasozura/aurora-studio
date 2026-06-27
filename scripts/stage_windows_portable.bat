@echo off
:: scripts\stage_windows_portable.bat
::
:: Stage the Windows portable folder for aurora-studio.
:: TASK-000047: Windows Portable Folder Pack
::
:: Usage (from repo root or scripts folder):
::   scripts\stage_windows_portable.bat
::
:: Prerequisites:
::   Run scripts\build_windows_onefolder.bat first.
::
:: This script does NOT build the EXE.
:: This script does NOT create a ZIP release.
:: This script does NOT install packages.
:: This script does NOT require admin rights.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set VERSION=0.1.0
set FOLDER_NAME=AuroraStudio-v%VERSION%-windows-portable
set BUILT_APP=%REPO_ROOT%\dist\AuroraStudio
set BUILT_EXE=%REPO_ROOT%\dist\AuroraStudio\AuroraStudio.exe
set STAGING_DIR=%REPO_ROOT%\dist-portable\%FOLDER_NAME%
set APP_DEST=%STAGING_DIR%\app\AuroraStudio
set TEMPLATES=%REPO_ROOT%\packaging\portable

echo [aurora-studio] Stage: Windows portable folder v%VERSION%
echo [aurora-studio] Staging to: %STAGING_DIR%

:: Verify built app exists
if not exist "%BUILT_EXE%" (
    echo.
    echo ERROR: Built executable not found: %BUILT_EXE%
    echo Run the build first:
    echo     scripts\build_windows_onefolder.bat
    echo.
    exit /b 1
)

:: Clean and recreate staging folder (controlled path only)
echo [aurora-studio] Cleaning previous staging output...
if exist "%STAGING_DIR%" rmdir /s /q "%STAGING_DIR%"
mkdir "%STAGING_DIR%"

:: Copy PyInstaller one-folder output into app\AuroraStudio\
echo [aurora-studio] Copying built app...
mkdir "%STAGING_DIR%\app"
xcopy /e /i /q "%BUILT_APP%" "%APP_DEST%"
if errorlevel 1 (
    echo ERROR: Failed to copy built app.
    exit /b 1
)

:: Create writable user-data folders
echo [aurora-studio] Creating portable folder structure...
mkdir "%STAGING_DIR%\data"
mkdir "%STAGING_DIR%\logs"
mkdir "%STAGING_DIR%\samples"
mkdir "%STAGING_DIR%\tmp"

:: Create top-level run_desktop.bat
(
echo @echo off
echo :: run_desktop.bat -- Aurora Studio portable launcher
echo :: Launches the Aurora Studio desktop shell.
echo :: Requires a display.
echo cd /d "%%~dp0"
echo app\AuroraStudio\AuroraStudio.exe
) > "%STAGING_DIR%\run_desktop.bat"

:: Create top-level smoke_desktop.bat
(
echo @echo off
echo :: smoke_desktop.bat -- Aurora Studio portable headless smoke
echo :: Runs headless mode. No window opens. Exits 0 on success.
echo cd /d "%%~dp0"
echo app\AuroraStudio\AuroraStudio.exe --headless-smoke
echo if errorlevel 1 ^(
echo     echo ERROR: Portable smoke FAILED.
echo     exit /b 1
echo ^)
echo echo Portable smoke PASSED.
) > "%STAGING_DIR%\smoke_desktop.bat"

:: Copy templates as text files
echo [aurora-studio] Copying README and NOTICE...
copy /y "%TEMPLATES%\README.txt.template" "%STAGING_DIR%\README.txt" >nul
copy /y "%TEMPLATES%\NOTICE.txt.template" "%STAGING_DIR%\NOTICE.txt" >nul

echo.
echo [aurora-studio] Staging complete.
echo [aurora-studio] Staged folder: %STAGING_DIR%
echo [aurora-studio] Run smoke: scripts\smoke_portable_folder.bat

endlocal
exit /b 0
