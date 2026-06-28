@echo off
REM Create Aurora Studio v0.3.0-rc1 portable ZIP
REM Requires PowerShell 5.1+
powershell -ExecutionPolicy Bypass -File "%~dp0create_v0_3_portable_zip_rc.ps1" %*
