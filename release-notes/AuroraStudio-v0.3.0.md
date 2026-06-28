# Aurora Studio v0.3.0

## Release Type

DRAFT. Not for distribution.
Decision status: **PENDING**

This document is a draft release note.
It will be finalized only after an explicit GO decision with complete QA evidence.
This document does not claim production readiness.

---

## Based On

Aurora Studio v0.2 editor foundation + v0.3 AI/workflow/safety foundation.

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
- Autosave writes placeholder bundle data only.
- Undo/redo covers 4 safe action types only.
- backup-project and recovery-report not available as CLI commands yet.
- Windows packaging scripts only.

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

```bash
python -m unittest
```

Expected: All tests PASS.

---

## Decision Status

**PENDING**

This release note will be updated to reflect the final GO decision when:
1. All QA evidence is complete.
2. V0_3_FINAL_RELEASE_DECISION_REPORT.md is signed off.
3. User explicitly instructs to change decision to GO.
