# Windows Portable EXE Plan

Document ID: WINDOWS_PORTABLE_EXE_PLAN
Version: 0.1.0
Status: Planning only — no EXE build in this task
Task: TASK-000045

---

## Purpose

Define the strategy for packaging Aurora Studio as a self-contained Windows
portable application for local use without requiring a Python installation.

This document is a planning artifact only. No build is performed here.

---

## Current Application Entry Points

The following entry points are currently functional and verified:

```text
python -m aurora_studio.ui.desktop_shell
python -m aurora_studio.ui.desktop_shell --headless-smoke
python -m aurora_studio.cli smoke
python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"
python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project
python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project
```

Both entry points — the GUI desktop shell and the CLI — must be reachable from a
future portable EXE or wrapper batch file.

---

## Target Windows Version Assumptions

- Windows 10 (64-bit) minimum
- Windows 11 (64-bit) supported
- No administrator rights required at runtime
- No Python installation required by end user
- No internet access required at runtime

---

## Python Version Assumption

```text
Python 3.11+ (CPython, 64-bit Windows build)
```

The Python interpreter will be bundled inside the portable application by the
future build tool. The end user does not install Python separately.

---

## Portable EXE Goal

Produce a single distributable folder (`AuroraStudio-v{version}-windows-portable/`)
that can be:

- Copied to any Windows machine
- Run without installation
- Run without Python installed
- Run without administrator rights
- Launched by double-clicking `AuroraStudio.exe` or `run_desktop.bat`

The folder layout is defined in `PORTABLE_FOLDER_LAYOUT.md`.

---

## Non-Goals

The following are explicitly out of scope for TASK-000045 and must not be
introduced until explicitly authorised by a later task:

- No EXE build in this task
- No installer in this task (NSIS, WiX, MSIX)
- No PyInstaller installation in this task
- No dependency changes in this task
- No provider integration (no API keys, no model calls)
- No plugin execution (plugin metadata only)
- No database (all state in-memory and bundle JSON)
- No code signing in this task
- No auto-update in this task
- No ZIP release artifact in this task

---

## Future Build Tool Candidate

```text
PyInstaller
```

PyInstaller is the planned tool for producing the portable Windows EXE.

**PyInstaller is planned for a later task and must not be added by TASK-000045.**

PyInstaller will be introduced only when TASK-000046 (PyInstaller Build Smoke Pack)
is explicitly approved and executed.

Alternative tools for later evaluation:

- `cx_Freeze` — alternative to PyInstaller, similar output
- `Nuitka` — compiles Python to C, produces smaller and faster EXEs
- `auto-py-to-exe` — GUI wrapper around PyInstaller

Recommendation: start with PyInstaller one-folder mode (`--onedir`) rather than
one-file mode (`--onefile`) to ease debugging and antivirus compatibility.

---

## Build Input

When the future build task runs, it will require:

```text
Source:        src/aurora_studio/
Entry module:  aurora_studio.ui.desktop_shell  (GUI)
               aurora_studio.cli               (CLI, optional secondary)
Assets:        None (no media, no external data files required yet)
Icon:          docs/packaging/assets/aurora_icon.ico  (future, not yet created)
Version file:  version string from pyproject.toml [tool.poetry.version] or equivalent
```

Hidden imports likely required by PyInstaller:

```text
aurora_studio.ui.desktop_shell
aurora_studio.ui.actions
aurora_studio.ui.view_models
aurora_studio.cli.main
aurora_studio.application.service
aurora_studio.application.workspace
aurora_studio.managers.*
tkinter
tkinter.ttk
json
pathlib
uuid
datetime
```

---

## Build Output

Future expected output:

```text
dist/
  AuroraStudio-v{version}-windows-portable/
    AuroraStudio.exe        <- main GUI entry point
    run_desktop.bat         <- convenience launcher
    run_tests.bat           <- test runner (bundled Python)
    smoke_desktop.bat       <- smoke runner
    README.txt
    NOTICE.txt
    _internal/              <- PyInstaller one-folder runtime (Python + stdlib)
    data/                   <- writable user data directory (empty at install)
    logs/                   <- writable logs directory (empty at install)
    tmp/                    <- writable temp directory (empty at install)
```

---

## Runtime Behavior

When running from a portable EXE:

- `sys.frozen` will be `True` (set by PyInstaller)
- The application's bundle directory is `sys._MEIPASS` (one-folder mode)
- All writable output (bundles, logs, temp) must be redirected to user-writable
  paths adjacent to the EXE, not inside `_internal/`
- The `aurora_studio.cli` module must be reachable via a bundled CLI entry point
  or via `AuroraStudio.exe --cli <subcommand>`
- The headless smoke command must work without a display:
  `AuroraStudio.exe --headless-smoke`

---

## Smoke Tests

The following checks must pass on any built portable artifact:

```text
1. AuroraStudio.exe --headless-smoke exits 0 and prints valid JSON
2. AuroraStudio.exe (or run_desktop.bat) opens window on a display machine
3. CLI smoke: all create-demo / validate-bundle / rehydrate-bundle commands pass
4. No dependency on Python system installation
5. No internet access required
6. No admin rights required
7. Antivirus scan log reviewed (false positives documented if any)
```

---

## Release Checklist

Future release checklist (not executed in this task):

```text
[ ] pyproject.toml version bumped
[ ] CHANGELOG updated
[ ] All unit tests pass from source
[ ] Build produced with PyInstaller one-folder mode
[ ] Headless smoke passes on built artifact
[ ] GUI smoke passes on a display machine
[ ] Portable folder layout matches PORTABLE_FOLDER_LAYOUT.md
[ ] No provider keys bundled
[ ] No plugin code executed
[ ] No database included
[ ] Antivirus scan reviewed
[ ] README.txt included in portable folder
[ ] NOTICE.txt included in portable folder
[ ] Artifact renamed to AuroraStudio-v{version}-windows-portable.zip for distribution
```
