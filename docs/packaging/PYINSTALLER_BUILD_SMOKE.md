# PyInstaller Build Smoke

Document ID: PYINSTALLER_BUILD_SMOKE
Version: 0.1.0
Status: Build smoke only — not a final release
Task: TASK-000046

---

## Purpose

Document the controlled one-folder PyInstaller build smoke for Aurora Studio.

This is a local Windows build smoke. It proves the current desktop shell can be
frozen into a self-contained portable one-folder application without a Python
installation on the target machine.

This is not a final release. This is not an installer. This is not production-ready.

---

## Prerequisites

- Windows 10 or Windows 11 (64-bit) for the target portable app
- Python 3.11+ (CPython 64-bit) installed on the build machine
- Build dependencies installed (see below)
- Repository root accessible

Build is not supported on non-Windows platforms. PyInstaller can run on Linux
and macOS but will not produce a `.exe` suitable for Windows.

---

## Build-Time Dependency Rule

PyInstaller is a **build-time-only** dependency.

It must not be imported from application code.
It must not appear in `pyproject.toml` runtime dependencies.
It must not be required for normal `python -m unittest` execution.

The build dependency is declared separately:

```text
build/requirements-build.txt
```

---

## Install Build Dependency

Run once in your build environment:

```bash
python -m pip install -r build\requirements-build.txt
```

PowerShell:

```powershell
python -m pip install -r build\requirements-build.txt
```

This installs PyInstaller into the current Python environment.
It does not modify the application's runtime dependency set.

---

## Build One-Folder App

From the repository root:

```bat
scripts\build_windows_onefolder.bat
```

PowerShell:

```powershell
.\scripts\build_windows_onefolder.ps1
```

The build script:

1. Checks PyInstaller availability and exits with instructions if missing.
2. Cleans `build\pyinstaller_work\` and `dist\AuroraStudio\` before running.
3. Invokes PyInstaller with the spec file at `build\pyinstaller\aurora_studio_desktop.spec`.
4. Produces output at `dist\AuroraStudio\`.

Build time is typically 30–120 seconds depending on machine.

---

## Smoke-Test Built App

After a successful build:

```bat
scripts\smoke_built_app.bat
```

PowerShell:

```powershell
.\scripts\smoke_built_app.ps1
```

The smoke script runs:

```bat
dist\AuroraStudio\AuroraStudio.exe --headless-smoke
```

Expected: exits 0, prints valid JSON.

No window opens during the smoke test.

---

## Expected Output

After a successful build:

```text
dist/
  AuroraStudio/
    AuroraStudio.exe        <- GUI / headless entry point
    _internal/              <- PyInstaller runtime (Python + stdlib)
    ...

build/
  pyinstaller_work/         <- PyInstaller intermediate files (gitignored)
```

The `dist/` and `build/` directories are listed in `.gitignore` and must not be
committed to the repository.

The expected full portable folder layout (for a later rename/packaging task) is
documented in `docs/packaging/PORTABLE_FOLDER_LAYOUT.md`.

---

## Known Limitations

- Build-time only. Not a final release.
- No installer is created.
- No final release ZIP is created.
- No code signing is applied.
- No auto-update is implemented.
- No provider API keys are bundled.
- No plugin code is executed at runtime.
- No database is added.
- One-file mode (`--onefile`) is not used — one-folder mode only for this smoke.
- SmartScreen warning is expected on first launch (unsigned EXE).
- Antivirus false positives are possible. Document with `virustotal.com` scan.
- tkinter must be present in the build Python installation. Embeddable Python
  distributions do not include tkinter.
- `unittest` module is excluded from the frozen bundle to reduce size.
  Run `python -m unittest` from source for testing.

---

## Troubleshooting

**PyInstaller not found:**

```text
ERROR: PyInstaller is not installed.
```

→ Run: `python -m pip install -r build\requirements-build.txt`

**tkinter ImportError at runtime:**

```text
ImportError: No module named '_tkinter'
```

→ Use a full CPython installer, not an embeddable Python zip.
→ Confirm `tcl86t.dll` and `tk86t.dll` are present in the build Python.
→ Add explicit `--collect-all tkinter` to the spec if needed.

**Module not found at runtime:**

```text
ModuleNotFoundError: No module named 'aurora_studio.managers...'
```

→ Add the missing module path to `hiddenimports` in
  `build/pyinstaller/aurora_studio_desktop.spec`.

**Headless smoke fails (non-zero exit):**

→ Run from source first:
  `PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke`
→ If source smoke passes but built smoke fails, check hidden imports in the spec.

**Build artifact is very large (>150 MB):**

→ Review `excludes` in the spec. Add unused stdlib modules.
→ `unittest` is already excluded in this spec.

---

## Non-Goals

This task does not implement:

- Final release ZIP (`AuroraStudio-v0.1.0-windows-portable.zip`)
- Windows installer (NSIS, WiX, MSIX)
- Code signing (Authenticode / EV certificate)
- Auto-update mechanism
- One-file EXE (`--onefile` mode)
- Provider API integration
- Plugin execution
- Database persistence
- Production release pipeline
- Binary dependency audit
- Antivirus submission

Those require later tasks.
