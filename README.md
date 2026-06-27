# Aurora Studio

Aurora Studio is the implementation repository for the Aurora AI filmmaking Creative Operating System.

The source of truth for requirements is the separate specification repository:

```text
aurora-spec
```

---

## Current Status

This is a functional development build. It is not production-ready.

Current capabilities:

- Desktop shell (tkinter, standard library only)
- Project management (create, open, save/load bundle)
- Scene and Shot management
- Timeline management
- Asset management
- Character management
- AFL structure validation (structural only)
- Prompt export artifact management
- Plugin metadata registration
- CLI for headless operations and smoke testing

Not yet implemented:

- Real AFL semantic validation
- Real prompt generation
- Provider integration
- Plugin loading or execution
- Database persistence
- Media preview or processing
- Character face recognition
- Asset metadata extraction
- Full timeline editor
- Professional UI theme
- Auto-save
- Installer or EXE packaging

---

## Current Limitations

- No external dependencies — standard library only.
- No database — all state is in-memory per session, persisted only via bundle JSON.
- No provider integration — no AI model calls.
- No plugin execution — plugin metadata only.
- Desktop shell uses standard-library `tkinter` only (no PySide, PyQt, etc.).
- This is not a final installer or EXE. Run directly from source.

---

## Python Version

```text
Python 3.11+
```

---

## Local Development

No installation step is required. Run directly from source using `PYTHONPATH`.

### Run Tests

From the repository root:

```bash
python -m unittest
```

Windows batch:

```bat
scripts\run_tests.bat
```

Windows PowerShell:

```powershell
.\scripts\run_tests.ps1
```

---

### Run Desktop Shell

Requires a display (GUI).

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell
```

Windows batch:

```bat
scripts\run_desktop.bat
```

Windows PowerShell:

```powershell
.\scripts\run_desktop.ps1
```

---

### Run Headless Smoke

Safe in CI — no display required.

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke
```

---

### Run CLI Smoke

```bash
PYTHONPATH=src python -m aurora_studio.cli smoke
PYTHONPATH=src python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"
PYTHONPATH=src python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project
PYTHONPATH=src python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project
```

Windows batch (runs all smoke steps):

```bat
scripts\smoke_desktop.bat
```

Windows PowerShell:

```powershell
.\scripts\smoke_desktop.ps1
```

---

## Runtime Dependencies

None. Standard library only.

No `pip install` required.

---

## Specification Authority

Implementation must follow `aurora-spec`.

Do not implement features unless a controlled implementation task explicitly authorizes the work.
