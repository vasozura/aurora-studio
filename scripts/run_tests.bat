@echo off
:: Aurora Studio - Run Tests
:: Usage: scripts\run_tests.bat
:: Run from repository root or scripts folder.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..

cd /d "%REPO_ROOT%"
set PYTHONPATH=%REPO_ROOT%\src

echo [aurora-studio] Running tests...
echo [aurora-studio] PYTHONPATH=%PYTHONPATH%

python -m unittest
exit /b %ERRORLEVEL%
