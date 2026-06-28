@echo off
REM Smoke test v0.3.0-rc1 portable ZIP
powershell -ExecutionPolicy Bypass -File "%~dp0smoke_v0_3_portable_zip_rc.ps1" %*
