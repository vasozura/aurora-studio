# Aurora Studio v0.2.0-rc1

Release type: Internal release candidate
Status: rc1 — NOT a final release
Based on: TASK-000051 through TASK-000070

This is a release candidate for internal review and validation only.
This is NOT a final release.
This release does NOT claim production readiness.

---

## Included in v0.2.0-rc1

- Scene detail editor with full scene metadata
- Shot detail editor with camera and framing detail
- Scene/Shot inspector UI
- Timeline editor with duration summary
- Asset browser with metadata and tag editing
- Asset linking to scenes, shots, and characters
- Character detail editor with extended fields
- Character reference workflow
- Expanded AFL validation with report tracking
- Prompt template system (local string rendering, no Jinja2)
- Prompt export preview (local render, no provider call)
- Export profiles (6 default profiles, custom profiles)
- Project search and filters (in-memory, case-insensitive)
- JSON import/export hardening (backup, validation, friendly errors)
- Autosave planning documentation
- Undo/redo planning documentation
- Provider adapter planning documentation
- Plugin sandbox planning documentation

---

## How to Run

```bash
cd aurora-studio
python -m aurora_studio.ui.desktop_shell
```

---

## How to Smoke Test

```bash
python -m unittest
python -m aurora_studio.ui.desktop_shell --headless-smoke
python -m aurora_studio.cli smoke
python -m aurora_studio.cli create-demo --path ./tmp-demo --title "Demo"
python -m aurora_studio.cli validate-bundle --path ./tmp-demo
python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo
```

---

## Known Limitations

- No provider integration — prompts render locally only
- No plugin execution — plugins are metadata only
- No autosave — manual save only
- No undo/redo — actions are immediate and irreversible
- No installer — run from source
- No MSIX, no code signing
- Desktop UI is minimal (tkinter)
- No thumbnail, face recognition, or media preview
- No drag-and-drop
- No real AI generation
- No database

---

## Not Included

- Provider integration
- Plugin execution
- Database
- Autosave implementation
- Undo/redo implementation
- Installer
- MSIX packaging
- Code signing
- Production readiness claim

---

## Validation

All 1586+ automated tests must pass before promoting rc1.
Headless smoke must pass.
CLI smoke must pass.
Go/no-go template must be completed and signed off.

See: docs/qa/V0_2_GO_NO_GO_TEMPLATE.md
