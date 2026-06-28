# v0.2 Release Candidate Plan — Aurora Studio

## Purpose

This document describes the plan for producing and validating the Aurora Studio v0.2.0-rc1 release candidate.
This is planning only. No final release is created by TASK-000070.

## Release Candidate Target

Version: 0.2.0-rc1
Type: Internal release candidate
State: Planning

## Scope Included

The following features are included in v0.2:

- Scene detail editor
- Shot detail editor
- Scene/Shot inspector
- Timeline editor
- Timeline duration summary
- Asset browser
- Asset linking
- Character detail editor
- Character reference workflow
- Expanded AFL validation
- Prompt template system
- Prompt export preview
- Export profiles
- Project search and filters
- JSON import/export hardening
- Autosave planning
- Undo/redo planning
- Provider adapter planning
- Plugin sandbox planning

## Scope Excluded

The following are explicitly excluded from v0.2:

- No provider integration
- No plugin execution
- No database
- No autosave implementation
- No undo/redo implementation
- No installer
- No MSIX
- No code signing
- No production readiness claim

## Prerequisites

- All TASK-000051 through TASK-000070 completed.
- All tests pass with zero failures.
- Headless smoke passes.
- CLI smoke passes.
- No open blockers.

## Required Automated Tests

```bash
python -m unittest
```

Expected: all tests pass, zero failures.

## Required Headless Smoke

```bash
python -m aurora_studio.ui.desktop_shell --headless-smoke
```

Expected: ok: true

## Required Desktop Manual QA

- Open application.
- Create a new project.
- Create a scene and edit detail.
- Create a shot and edit detail.
- Add a timeline item.
- Import an asset.
- Link an asset.
- Create a character.
- Add a character reference.
- Run AFL validation.
- Create a prompt template.
- Render a prompt preview.
- Save as export artifact.
- Create an export profile.
- Render with profile.
- Search scenes, shots, assets, characters.
- Save project.
- Close and reopen project.
- Verify all data persists.

## Required Packaging Validation

- Portable ZIP packaging script is inspectable.
- ZIP contains required source files.
- ZIP does not contain API keys.
- ZIP does not contain provider SDK.

## Known Limitations

- No provider integration.
- No plugin execution.
- No autosave.
- No undo/redo.
- No installer.
- Desktop UI is minimal (tkinter).
- No thumbnail or media preview.
- No drag-and-drop.
- No real AI generation.

## Go/No-Go Process

See: docs/qa/V0_2_GO_NO_GO_TEMPLATE.md

1. Complete all prerequisites.
2. Run all required automated tests.
3. Complete manual QA checklist.
4. Complete packaging validation.
5. Review open blockers.
6. Fill in go/no-go template.
7. Reviewer signs off.

## Evidence Collection

- Save test output to a file: `python -m unittest 2>&1 | tee test-results.txt`
- Screenshot headless smoke output.
- Screenshot manual QA steps.
- Record packaging validation output.

## Future Final Release Process

- Increment version to 0.2.0.
- Tag git commit with v0.2.0.
- Produce final ZIP artifact.
- Publish release notes.
- Archive release candidate artifacts.
