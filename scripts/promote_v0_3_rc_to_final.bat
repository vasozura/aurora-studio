@echo off
REM Promote v0.3 RC to final. Blocked if decision is PENDING or NO-GO.
powershell -ExecutionPolicy Bypass -File "%~dp0promote_v0_3_rc_to_final.ps1" %*
