# Aurora Studio v0.3 Portable Folder Layout

## Intended Layout

```
AuroraStudio-v0.3.0-windows-portable/
  app/                  ← PyInstaller one-folder distribution
  data/                 ← User project data (by user choice)
  logs/                 ← Application log files
  samples/              ← Sample project bundles
  tmp/                  ← Temporary working files
  run_desktop.bat       ← Launch Aurora Studio desktop app
  smoke_desktop.bat     ← Run headless smoke test
  README.txt            ← User-facing README
  NOTICE.txt            ← License and third-party notices
```

---

## Notes

No secrets are included.
No provider API keys are included.
No plugin packages are bundled.
User project data is external or stored under data/ by user choice only.
The app/ directory contains only the Python runtime and Aurora Studio modules.
No database files are included.
No media preview engine is bundled.
No background worker processes are included.

---

## Layout Rules

- app/ must contain only PyInstaller output and Aurora Studio source.
- data/ is empty on first run; user creates projects here by choice.
- logs/ is created on first launch.
- tmp/ is cleared on each launch.
- run_desktop.bat sets PYTHONPATH and launches desktop_shell.
- smoke_desktop.bat runs --headless-smoke and exits 0 on success.
- README.txt must not contain API keys or secrets.
- NOTICE.txt must list all bundled third-party licenses.
