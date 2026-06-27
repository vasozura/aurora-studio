@echo off
:: Aurora Studio - Headless Smoke
:: Usage: scripts\smoke_desktop.bat
:: Run from repository root or scripts folder.
:: Stops on first failure.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..

cd /d "%REPO_ROOT%"
set PYTHONPATH=%REPO_ROOT%\src

echo [aurora-studio] Running headless smoke...

:: Clean demo project to avoid duplicate-project errors
if exist tmp-demo-project (
    rmdir /s /q tmp-demo-project
    echo [aurora-studio] Removed existing tmp-demo-project
)

echo [aurora-studio] desktop --headless-smoke
python -m aurora_studio.ui.desktop_shell --headless-smoke
if %ERRORLEVEL% neq 0 ( echo [aurora-studio] FAILED & exit /b %ERRORLEVEL% )

echo [aurora-studio] cli smoke
python -m aurora_studio.cli smoke
if %ERRORLEVEL% neq 0 ( echo [aurora-studio] FAILED & exit /b %ERRORLEVEL% )

echo [aurora-studio] cli create-demo
python -m aurora_studio.cli create-demo --path .\tmp-demo-project --title "Demo Project"
if %ERRORLEVEL% neq 0 ( echo [aurora-studio] FAILED & exit /b %ERRORLEVEL% )

echo [aurora-studio] cli validate-bundle
python -m aurora_studio.cli validate-bundle --path .\tmp-demo-project
if %ERRORLEVEL% neq 0 ( echo [aurora-studio] FAILED & exit /b %ERRORLEVEL% )

echo [aurora-studio] cli rehydrate-bundle
python -m aurora_studio.cli rehydrate-bundle --path .\tmp-demo-project
if %ERRORLEVEL% neq 0 ( echo [aurora-studio] FAILED & exit /b %ERRORLEVEL% )

echo [aurora-studio] All smoke checks passed.
exit /b 0
