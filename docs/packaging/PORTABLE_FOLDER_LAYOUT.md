# Portable Folder Layout

Document ID: PORTABLE_FOLDER_LAYOUT
Version: 0.1.0
Status: Planning only — this folder must not be created by TASK-000045
Task: TASK-000045

---

## Purpose

Define the proposed directory layout for the future Windows portable release of
Aurora Studio.

This document is planning only. The layout described here must not be created
by TASK-000045. It is a target for a later build task.

---

## Proposed Layout

```text
AuroraStudio-v0.1.0-windows-portable/
  AuroraStudio.exe              <- GUI entry point (PyInstaller one-folder EXE)
  run_desktop.bat               <- convenience launcher for GUI
  run_tests.bat                 <- test runner using bundled Python
  smoke_desktop.bat             <- headless smoke runner
  README.txt                    <- plain-text user instructions
  NOTICE.txt                    <- license and third-party notices
  _internal/                    <- PyInstaller runtime (Python + stdlib, read-only)
    python3X.dll
    ...
  data/                         <- writable user data (empty at install)
  logs/                         <- writable log output (empty at install)
  samples/                      <- optional bundled sample projects (future)
  tmp/                          <- writable temporary workspace (empty at install)
```

---

## Layout Rules

### Bundled App Files (read-only after install)

```text
AuroraStudio.exe
run_desktop.bat
run_tests.bat
smoke_desktop.bat
README.txt
NOTICE.txt
_internal/
```

These files are part of the application bundle and must not be modified by the
running application.

### Generated User Data (writable)

```text
data/       <- user-created project bundle JSON files (aurora_bundle.json etc.)
logs/       <- application log output
tmp/        <- temporary demo projects and scratch folders
```

These directories are writable and created by the user or by CLI operations.

They are **external to the app bundle** in the sense that:
- Their contents are created at runtime, not bundled at build time.
- Users may back them up or move them independently.
- Deleting them does not break the application.

**User-created project folders are external to the app bundle** unless explicitly
selected or placed by the user inside `data/`. The application must not assume
project paths relative to `_internal/`.

---

## Separation of Concerns

| Path | Created by | Writable at runtime | Bundled at build |
|---|---|---|---|
| `AuroraStudio.exe` | Build | No | Yes |
| `_internal/` | Build (PyInstaller) | No | Yes |
| `README.txt` | Build | No | Yes |
| `NOTICE.txt` | Build | No | Yes |
| `data/` | First run / user | Yes | No |
| `logs/` | Application | Yes | No |
| `tmp/` | Application / CLI | Yes | No |
| User project folders | User | Yes | No |

---

## Security Rules (enforced in future build task)

- **No provider API keys must be bundled** inside `_internal/` or any other
  build artifact. Keys are never committed and never packaged.
- **No plugin code must be executed** at launch or by default operation.
  Plugin metadata only.
- **No database files** must be bundled. All persistence is via user-selected
  bundle JSON files.

---

## Versioning Convention

Portable folder naming:

```text
AuroraStudio-v{MAJOR}.{MINOR}.{PATCH}-windows-portable
```

Example:

```text
AuroraStudio-v0.1.0-windows-portable
```

The version is sourced from `pyproject.toml [tool.poetry.version]` at build time.

Distribution ZIP (future):

```text
AuroraStudio-v0.1.0-windows-portable.zip
```

---

## Notes

- The layout uses PyInstaller one-folder mode (`--onedir`), not one-file mode
  (`--onefile`), to avoid slow startup from temp extraction and to simplify
  antivirus compatibility.
- `samples/` is reserved for future bundled sample projects and is optional in
  the initial release.
- The `_internal/` path name is the PyInstaller default for one-folder mode in
  Python 3.12+. Earlier versions use the `dist/` subfolder directly. Confirm
  at build time.
