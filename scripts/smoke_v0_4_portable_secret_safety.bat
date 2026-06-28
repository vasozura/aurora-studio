@echo off
REM smoke_v0_4_portable_secret_safety.bat
REM v0.4 Portable Secret Safety Smoke Script (Batch)
REM
REM Usage: smoke_v0_4_portable_secret_safety.bat [portable_path]
REM
REM Validates that a portable folder does not contain excluded secret files,
REM caches, or SDK packages. Does NOT call any network. Does NOT delete user data.
REM Fails clearly if violations are found.

setlocal enabledelayedexpansion

set PORTABLE_PATH=%1
if "%PORTABLE_PATH%"=="" set PORTABLE_PATH=.

set ERROR_COUNT=0
set WARN_COUNT=0

echo === v0.4 Portable Secret Safety Smoke ===
echo Path: %PORTABLE_PATH%
echo.

if not exist "%PORTABLE_PATH%" (
    echo ERROR: Path does not exist: %PORTABLE_PATH%
    exit /b 1
)

REM Check: no .env files
set FOUND_ENV=0
for /r "%PORTABLE_PATH%" %%f in (.env *.env) do (
    echo FAIL: .env file found: %%f
    set /a ERROR_COUNT+=1
    set FOUND_ENV=1
)
if %FOUND_ENV%==0 echo PASS: No .env files found

REM Check: no __pycache__ directories
set FOUND_CACHE=0
for /d /r "%PORTABLE_PATH%" %%d in (__pycache__) do (
    echo WARN: __pycache__ found: %%d
    set /a WARN_COUNT+=1
    set FOUND_CACHE=1
)
if %FOUND_CACHE%==0 echo PASS: No __pycache__ directories

REM Check: no .pytest_cache directories
set FOUND_PYTEST=0
for /d /r "%PORTABLE_PATH%" %%d in (.pytest_cache) do (
    echo WARN: .pytest_cache found: %%d
    set /a WARN_COUNT+=1
    set FOUND_PYTEST=1
)
if %FOUND_PYTEST%==0 echo PASS: No .pytest_cache directories

REM Check: no provider SDK package folders (spot check top-level site-packages style)
set SDK_FAIL=0
for %%s in (openai anthropic requests httpx aiohttp) do (
    if exist "%PORTABLE_PATH%\%%s" (
        echo FAIL: Provider SDK folder found: %PORTABLE_PATH%\%%s
        set /a ERROR_COUNT+=1
        set SDK_FAIL=1
    )
)
if %SDK_FAIL%==0 echo PASS: No provider SDK folders at root

REM Check: README or NOTICE present
set FOUND_README=0
if exist "%PORTABLE_PATH%\README.md" set FOUND_README=1
if exist "%PORTABLE_PATH%\README.txt" set FOUND_README=1
if exist "%PORTABLE_PATH%\NOTICE" set FOUND_README=1
if exist "%PORTABLE_PATH%\NOTICE.txt" set FOUND_README=1
if %FOUND_README%==1 (
    echo PASS: README/NOTICE present
) else (
    echo WARN: No README or NOTICE found at root
    set /a WARN_COUNT+=1
)

echo.
echo === Summary ===
echo Errors: %ERROR_COUNT%
echo Warnings: %WARN_COUNT%

if %ERROR_COUNT% GTR 0 (
    echo RESULT: FAIL
    exit /b 1
) else (
    echo RESULT: PASS
    exit /b 0
)
