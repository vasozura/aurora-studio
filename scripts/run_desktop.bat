@echo off
:: Aurora Studio - Run Desktop Shell
:: Usage: scripts\run_desktop.bat
:: Run from repository root or scripts folder.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..

cd /d "%REPO_ROOT%"
set PYTHONPATH=%REPO_ROOT%\src

echo [aurora-studio] Starting desktop shell...
echo [aurora-studio] PYTHONPATH=%PYTHONPATH%

python -m aurora_studio.ui.desktop_shell
exit /b %ERRORLEVEL%
