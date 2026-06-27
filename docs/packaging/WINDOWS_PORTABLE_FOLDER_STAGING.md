# Windows Portable Folder Staging

Document ID: WINDOWS_PORTABLE_FOLDER_STAGING
Version: 0.1.0
Status: Staging only — no final ZIP in this task
Task: TASK-000047

---

## Purpose

Document the staging process for the Windows portable folder of Aurora Studio.

Staging assembles the PyInstaller one-folder build output into the full portable
folder layout defined in `PORTABLE_FOLDER_LAYOUT.md`. The result is a folder
that can be inspected, smoke-tested, and later zipped in a separate release task.

This task does not create a final ZIP release.
This task does not create an installer.
This task does not add provider integration.
This task does not enable plugin execution.
Staging output is disposable and can be regenerated at any time.

---

## Prerequisites

1. Python 3.11+ installed on the build machine.
2. PyInstaller installed via build requirements:

```bash
python -m pip install -r build\requirements-build.txt
```

3. One-folder build completed:

```bat
scripts\build_windows_onefolder.bat
```

PowerShell:

```powershell
.\scripts\build_windows_onefolder.ps1
```

The staging script will fail with a clear error if the build has not been run.

---

## Staging Command

After a successful build, stage the portable folder:

```bat
scripts\stage_windows_portable.bat
```

PowerShell:

```powershell
.\scripts\stage_windows_portable.ps1
```

The staging script:

1. Verifies `dist\AuroraStudio\AuroraStudio.exe` exists.
2. Cleans `dist-portable\AuroraStudio-v0.1.0-windows-portable\` if present.
3. Copies the PyInstaller build into `app\AuroraStudio\`.
4. Creates `data\`, `logs\`, `samples\`, `tmp\` subdirectories.
5. Writes top-level `run_desktop.bat` and `smoke_desktop.bat`.
6. Copies `README.txt` and `NOTICE.txt` from templates.

Staging is fast (seconds) and idempotent. Re-run any time.

---

## Smoke Command

After staging:

```bat
scripts\smoke_portable_folder.bat
```

PowerShell:

```powershell
.\scripts\smoke_portable_folder.ps1
```

The smoke script:

1. Verifies the staged folder and executable exist.
2. Runs `dist-portable\AuroraStudio-v0.1.0-windows-portable\smoke_desktop.bat`.
3. The smoke bat runs `app\AuroraStudio\AuroraStudio.exe --headless-smoke`.
4. Exits 0 on success.

No window opens during the smoke test.

---

## Expected Folder Layout

After successful staging:

```text
dist-portable/
  AuroraStudio-v0.1.0-windows-portable/
    app/
      AuroraStudio/
        AuroraStudio.exe
        _internal/
        ...
    data/
    logs/
    samples/
    tmp/
    run_desktop.bat
    smoke_desktop.bat
    README.txt
    NOTICE.txt
```

The `dist-portable/` directory is listed in `.gitignore` and must not be
committed to the repository.

---

## What Is Included

- `app/AuroraStudio/` — PyInstaller one-folder bundle (EXE + Python runtime)
- `run_desktop.bat` — launches the desktop shell
- `smoke_desktop.bat` — headless smoke (no window)
- `README.txt` — user instructions
- `NOTICE.txt` — build notices, license attributions
- `data/`, `logs/`, `samples/`, `tmp/` — empty writable directories

---

## What Is Not Included

- No provider API keys
- No plugin code or plugin execution
- No database engine
- No installer
- No final release ZIP (that is a later task)
- No code signing
- No auto-update

---

## Cleanup Behavior

The staging script removes only the controlled path:

```text
dist-portable\AuroraStudio-v0.1.0-windows-portable\
```

It does not delete `dist\AuroraStudio\` (the PyInstaller build output).
It does not delete any user data or source files.

To fully clean all build and staging output:

```bat
rmdir /s /q dist
rmdir /s /q dist-portable
rmdir /s /q build\pyinstaller_work
```

PowerShell:

```powershell
Remove-Item -Recurse -Force dist, dist-portable, build\pyinstaller_work
```

---

## Troubleshooting

**Built executable not found:**

```text
ERROR: Built executable not found: ...\dist\AuroraStudio\AuroraStudio.exe
```

→ Run the build first:

```bat
python -m pip install -r build\requirements-build.txt
scripts\build_windows_onefolder.bat
```

**Staged folder not found (smoke):**

```text
ERROR: Staged portable folder not found
```

→ Run staging first:

```bat
scripts\stage_windows_portable.bat
```

**Headless smoke exits non-zero:**

→ Check that the PyInstaller build is correct by running the built app smoke:

```bat
scripts\smoke_built_app.bat
```

→ If `smoke_built_app.bat` also fails, re-run the build from scratch.

**xcopy fails on Windows (batch):**

→ Ensure `dist\AuroraStudio\` is not locked by another process.
→ Close any running AuroraStudio.exe instances before staging.

---

## Future Release ZIP Task

This staging task prepares the folder layout only.

A later task (TASK-000048 or similar) will:

1. Verify the staged folder.
2. Run portable smoke.
3. Zip the staged folder into:

```text
AuroraStudio-v0.1.0-windows-portable.zip
```

4. Verify the ZIP contents.
5. Document the release artifact.

No ZIP is created by TASK-000047.
