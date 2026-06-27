# Aurora Studio v0.1.0-rc1

Release type: Release candidate — local Windows portable build
Date: 2026-06-27
Status: Smoke validated — not a final release

---

## Release Type

This is a release candidate for local development and smoke testing.

It is not a production release.
It is not a final release.
It is not an installer release.
No production readiness is claimed.

---

## Included

This release candidate includes:

**Local desktop shell**
- tkinter-based desktop application
- Project path and title management
- Tabbed layout: Scenes & Shots, Timeline, Assets, Characters, AFL, Exports, Plugins
- Keyboard shortcuts: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+R, Ctrl+L, F5, Escape
- Status and log panel
- Workspace summary panel

**Project management**
- Project create and open
- Local JSON bundle save (aurora_bundle.json)
- Local JSON bundle load and rehydration

**Scene and Shot basics**
- Create scene, list scenes
- Create shot within scene, list shots

**Timeline, Asset, and Character smoke panels**
- Create timeline, add/remove/move timeline items
- Import/register asset, mark missing, archive
- Create character, add/remove reference assets, archive

**AFL, Export, and Plugin metadata smoke panels**
- Structural AFL validation (structural only — no semantic validation)
- Create export artifact, mark ready, mark failed
- Register, enable, and disable plugins (metadata only — no execution)

**Bundle rehydration**
- Full rehydration from bundle JSON via CLI and desktop shell

**CLI smoke commands**
- `python -m aurora_studio.cli smoke`
- `python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"`
- `python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project`
- `python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project`

**Headless smoke**
- `python -m aurora_studio.ui.desktop_shell --headless-smoke`

**Windows portable folder layout**
- `AuroraStudio-v0.1.0-windows-portable/`
- `app/AuroraStudio/AuroraStudio.exe` (PyInstaller one-folder)
- `run_desktop.bat`, `smoke_desktop.bat`
- `data/`, `logs/`, `samples/`, `tmp/`
- `README.txt`, `NOTICE.txt`

---

## How to Run

From the extracted portable folder:

```bat
run_desktop.bat
```

Requires a display.

---

## How to Smoke Test

From the extracted portable folder (no display required):

```bat
smoke_desktop.bat
```

Expected: exits 0. No window opens.

---

## Known Limitations

- No database is included. All state is in-memory per session.
- No provider integration is included. No AI model calls are made.
- No plugin execution is enabled. Plugin metadata only.
- No real AFL semantic validation is implemented. Structural only.
- No real prompt generation is implemented.
- No installer is included. Portable folder only.
- No code signing applied. SmartScreen warning expected on first launch.
- No auto-update implemented.
- No production readiness claim is made.

---

## Not Included

- No installer (NSIS, WiX, MSIX)
- No code signing (Authenticode / EV certificate)
- No database (SQLite, Postgres, ORM)
- No provider integration (OpenAI, Anthropic, RunwayML, etc.)
- No plugin execution
- No real AFL semantic validation
- No real prompt generation
- No media preview or processing
- No character face recognition
- No asset metadata extraction
- No full timeline editor
- No professional UI theme
- No auto-save
- No auto-update
- No production release approval

---

## Validation Checklist

```text
[ ] python -m unittest passes (source)
[ ] python -m aurora_studio.ui.desktop_shell --headless-smoke exits 0
[ ] python -m aurora_studio.cli smoke exits 0
[ ] scripts\build_windows_onefolder.bat succeeds
[ ] scripts\stage_windows_portable.bat succeeds
[ ] scripts\smoke_portable_folder.bat exits 0
[ ] scripts\create_portable_zip.bat creates ZIP and SHA-256
[ ] scripts\smoke_portable_zip.bat exits 0
[ ] ZIP top-level folder is AuroraStudio-v0.1.0-windows-portable
[ ] run_desktop.bat present in ZIP
[ ] smoke_desktop.bat present in ZIP
[ ] README.txt present in ZIP
[ ] NOTICE.txt present in ZIP
[ ] data/, logs/, samples/, tmp/ present in ZIP
[ ] No provider keys in ZIP
[ ] No plugin code executed
[ ] No installer created
[ ] No final release approved
```

---

## QA and Validation

QA documentation for this release candidate:

- `docs/qa/V0_1_RELEASE_CANDIDATE_QA_PLAN.md` — full QA plan and procedure
- `docs/qa/V0_1_REGRESSION_CHECKLIST.md` — regression checklist
- `docs/qa/V0_1_PACKAGING_VALIDATION_CHECKLIST.md` — packaging validation checklist
- `docs/qa/V0_1_GO_NO_GO_REPORT_TEMPLATE.md` — go/no-go report template

To complete QA review, follow the procedures in the QA plan.
Fill in the go/no-go template with actual results.

This release candidate has not received final release approval.
No production readiness claim is made.
