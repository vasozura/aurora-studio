@echo off
REM promote_v0_4_rc_to_final.bat
REM v0.4 RC to Final Promotion Script (Batch)
REM
REM Usage: promote_v0_4_rc_to_final.bat
REM
REM Requirements:
REM   - docs\qa\V0_4_FINAL_RELEASE_DECISION_REPORT.md must exist
REM   - Decision must be GO or GO WITH KNOWN LIMITATIONS
REM   - Script fails clearly for PENDING or NO-GO
REM
REM Does NOT build installer. Does NOT sign code.
REM Does NOT download dependencies. Does NOT call provider APIs.
REM Does NOT bundle secrets.

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set REPORT_PATH=%SCRIPT_DIR%..\docs\qa\V0_4_FINAL_RELEASE_DECISION_REPORT.md

echo === v0.4 RC to Final Promotion ===

REM Check decision report exists
if not exist "%REPORT_PATH%" (
    echo BLOCKED: Decision report not found.
    echo Expected: docs\qa\V0_4_FINAL_RELEASE_DECISION_REPORT.md
    exit /b 1
)

echo Decision report found: %REPORT_PATH%

REM Check decision value using findstr
findstr /i "Final Decision: PENDING" "%REPORT_PATH%" >nul 2>&1
if %errorlevel%==0 (
    echo BLOCKED: Decision is PENDING. Promotion requires GO or GO WITH KNOWN LIMITATIONS.
    exit /b 1
)

findstr /i "Final Decision: NO-GO" "%REPORT_PATH%" >nul 2>&1
if %errorlevel%==0 (
    echo BLOCKED: Decision is NO-GO. Promotion is not allowed.
    exit /b 1
)

REM Check for GO decision
findstr /i "Final Decision: GO" "%REPORT_PATH%" >nul 2>&1
if %errorlevel%==0 (
    echo Decision is GO - promotion check passed.
    goto promotion_ok
)

findstr /i "Decision: GO WITH KNOWN LIMITATIONS" "%REPORT_PATH%" >nul 2>&1
if %errorlevel%==0 (
    echo Decision is GO WITH KNOWN LIMITATIONS - promotion check passed.
    goto promotion_ok
)

echo BLOCKED: Could not confirm GO decision in report.
exit /b 1

:promotion_ok
echo.
echo Promotion check complete.
echo Next steps (manual):
echo   1. Tag the source revision.
echo   2. Archive the release folder.
echo   3. Update release-notes\AuroraStudio-v0.4.0.md with final date and decision.
echo.
echo NOTE: This script does not build an installer, sign code,
echo       download dependencies, call provider APIs, or bundle secrets.
exit /b 0
