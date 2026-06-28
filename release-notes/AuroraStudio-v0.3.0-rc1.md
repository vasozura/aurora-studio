# Aurora Studio v0.3.0-rc1

## Release Type

Release Candidate. Not for production use.
This release candidate has not yet received a final GO decision.

---

## Based On

Aurora Studio v0.2 editor foundation + v0.3 AI/workflow foundation.

---

## Included

- v0.2 editor foundation (scenes, shots, timeline, assets, characters, AFL, prompts, export profiles)
- Provider foundation — dry-run only, no real API calls
- Prompt execution local workflow (queue, batch export, run history)
- Plugin sandbox foundation — metadata only, execution disabled
- Project backup/recovery (local .backups/ folder)
- Explicit autosave (.autosave/ folder, no background worker)
- Minimal undo/redo command stack (in-memory, safe actions only)

---

## How to Run

```
run_desktop.bat
```

Or from source:

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell
```

---

## How to Smoke Test

```
smoke_desktop.bat
```

Or:

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke
PYTHONPATH=src python -m aurora_studio.cli smoke
PYTHONPATH=src python -m aurora_studio.cli provider-smoke
PYTHONPATH=src python -m aurora_studio.cli plugin-smoke
```

---

## Known Limitations

- No real provider API calls. Dry-run only.
- Plugin execution disabled. All stub calls return blocked.
- Media preview planning only — no preview implemented.
- Autosave writes placeholder bundle — full project bundle integration is a future task.
- Undo/redo covers 4 safe action types only.
- backup-project and recovery-report not available as CLI commands yet.
- Windows packaging scripts only. No Linux/macOS packaging.

---

## Not Included

- Real provider API calls
- Provider SDKs
- Real API key storage
- Plugin execution
- Database
- Media preview
- Installer/MSIX
- Code signing
- Auto-update
- Production readiness claim

---

## Validation

To validate this RC, run:

```bash
python -m unittest
```

Expected: All tests PASS.

---

## Decision Status

This release is a RELEASE CANDIDATE only.
Final release decision: **PENDING**
