# PyInstaller Future Build Boundary

Document ID: PYINSTALLER_FUTURE_BUILD_BOUNDARY
Version: 0.1.0
Status: Planning only — defines scope for TASK-000046
Task: TASK-000045

---

## Purpose

Define the strict boundary for the future PyInstaller build task.

This document specifies what TASK-000046 is allowed to do, what it is forbidden
from doing, what it must produce, and how it must be validated.

No build is performed in TASK-000045.

---

## Future Task Name

```text
TASK-000046: PyInstaller Build Smoke Pack
```

---

## Allowed Future Actions

The following actions are permitted only when TASK-000046 is explicitly approved
and executed:

```text
1. Add PyInstaller as an optional build dependency
   - May be installed in a separate build environment only
   - Must NOT be added to pyproject.toml [tool.poetry.dependencies]
   - May be listed in a separate requirements-build.txt if needed
   - Must NOT affect runtime or test dependencies

2. Create a PyInstaller spec file
   - File: aurora_studio.spec
   - Located at repository root
   - Must define entry point: aurora_studio/ui/desktop_shell.py
   - Must include all required hidden imports
   - Must configure one-folder mode (--onedir)

3. Create build scripts
   - scripts/build_windows.ps1
   - scripts/build_windows.bat
   - These must NOT be created by TASK-000045

4. Build a one-folder portable application
   - Output: dist/AuroraStudio-v{version}-windows-portable/
   - Layout must match PORTABLE_FOLDER_LAYOUT.md

5. Run headless smoke on built artifact
   - Must confirm AuroraStudio.exe --headless-smoke exits 0
   - Must confirm output is valid JSON

6. Run CLI smoke on built artifact
   - Must confirm create-demo / validate-bundle / rehydrate-bundle pass

7. Document build results
   - Size, antivirus scan results, known issues
```

---

## Forbidden Future Actions

The following actions are permanently forbidden from TASK-000046 and all future
tasks unless separately authorised by their own dedicated task:

```text
1. No provider API keys bundled
   - No OpenAI keys
   - No Anthropic keys
   - No RunwayML keys
   - No ElevenLabs keys
   - No provider credential of any kind

2. No plugin execution
   - Plugin metadata may be registered
   - Plugin code must never be loaded or executed
   - No importlib calls for plugin modules at startup

3. No database introduction
   - No SQLite
   - No Postgres
   - No ORM
   - No migration tooling

4. No web server
   - No Flask
   - No FastAPI
   - No Django
   - No HTTP listener of any kind

5. No installer unless separate task
   - No NSIS
   - No WiX
   - No MSIX
   - No ClickOnce

6. No code signing unless separate task
   - No Authenticode signing
   - No EV certificate usage

7. No auto-update unless separate task
   - No update check at startup
   - No network calls of any kind at startup

8. No modification of pyproject.toml for runtime dependencies
   - PyInstaller must remain a build-only tool

9. No hardcoded provider endpoints or model names in the EXE

10. No production release until a separate release task is approved
```

---

## Expected Build Commands

When TASK-000046 is executed, the expected build commands are:

```powershell
# Install build dependency (build environment only)
pip install pyinstaller

# Build portable folder
pyinstaller aurora_studio.spec --distpath ./dist --workpath ./build/pyinstaller

# Or via convenience script (to be created by TASK-000046):
.\scripts\build_windows.ps1
```

```bat
rem Batch equivalent
pip install pyinstaller
pyinstaller aurora_studio.spec
```

---

## Expected Smoke Commands

After build, the following must pass:

```bat
rem Headless smoke
dist\AuroraStudio-v0.1.0-windows-portable\AuroraStudio.exe --headless-smoke

rem CLI smoke (via bundled Python or wrapper)
dist\AuroraStudio-v0.1.0-windows-portable\smoke_desktop.bat
```

Expected: all commands exit with code 0 and print valid JSON.

---

## Expected Artifacts

After TASK-000046 completes:

```text
dist/
  AuroraStudio-v{version}-windows-portable/
    AuroraStudio.exe
    run_desktop.bat
    run_tests.bat
    smoke_desktop.bat
    README.txt
    NOTICE.txt
    _internal/
    data/
    logs/
    tmp/

build/                  <- PyInstaller work directory (gitignored)
aurora_studio.spec      <- PyInstaller spec file (committed)
scripts/build_windows.ps1
scripts/build_windows.bat
```

The `dist/` and `build/` directories must be listed in `.gitignore`.

---

## Rollback Plan

If TASK-000046 produces a broken or untestable build:

1. Delete `dist/` and `build/` directories.
2. Uninstall PyInstaller from the build environment.
3. The source code and unit tests must remain unaffected.
4. The `aurora_studio.spec` file may be deleted or kept for debugging.
5. Revert any changes to `scripts/` introduced by TASK-000046.
6. All existing unit tests must still pass from source without PyInstaller.

The codebase must at all times be runnable from source without PyInstaller.
PyInstaller is a packaging tool only and must not be a runtime dependency.

---

## Acceptance Criteria for TASK-000046

TASK-000046 is acceptable when:

1. PyInstaller one-folder build produces `AuroraStudio.exe`.
2. `AuroraStudio.exe --headless-smoke` exits 0 and outputs valid JSON.
3. Desktop shell opens on a machine with a display.
4. CLI smoke (create-demo / validate-bundle / rehydrate-bundle) passes.
5. `python -m unittest` still passes from source (no source code broken).
6. `dist/` is gitignored.
7. No provider keys are bundled.
8. No plugin code is executed.
9. No database is introduced.
10. `pyproject.toml` runtime dependencies are unchanged.
11. Antivirus scan results are documented.
12. Portable folder layout matches `PORTABLE_FOLDER_LAYOUT.md`.
13. Size is documented.
14. The task stops after reporting.
