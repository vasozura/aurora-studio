@echo off
rem promote_rc_to_final.bat
rem Promotes v0.1.0-rc1 release candidate to final v0.1.0 artifact via PowerShell.
rem Requires decision report to be GO or GO WITH KNOWN LIMITATIONS.
rem Does not rebuild. Does not install packages. Does not code-sign.
setlocal

set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%promote_rc_to_final.ps1

powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%PS1%"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo promote_rc_to_final.bat: FAILED with exit code %EXIT_CODE%
    exit /b %EXIT_CODE%
)
exit /b 0
