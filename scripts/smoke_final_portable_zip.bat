@echo off
rem smoke_final_portable_zip.bat
rem Verifies and smoke-tests the final promoted v0.1.0 portable ZIP via PowerShell.
rem Does not rebuild. Does not install packages. Does not open GUI. Does not call providers.
setlocal

set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%smoke_final_portable_zip.ps1

powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%PS1%"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo smoke_final_portable_zip.bat: FAILED with exit code %EXIT_CODE%
    exit /b %EXIT_CODE%
)
exit /b 0
