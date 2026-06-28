# Aurora Studio v0.3 QA Plan

## Purpose

Define the QA scope, test areas, and go/no-go process for Aurora Studio v0.3.

---

## Scope

- Editor foundation (v0.2 preserved)
- Provider foundation (dry-run only)
- Prompt execution workflow (local only)
- Plugin sandbox foundation (metadata only, execution disabled)
- Project backup/recovery
- Explicit autosave
- Minimal undo/redo command stack
- Packaging (portable ZIP RC)

---

## Out of Scope

- Real provider API tests
- Plugin execution tests
- Database tests
- Media preview tests
- Installer/code signing tests
- Production load tests
- Multi-user conflict tests
- Cloud sync tests

---

## Required Environment

- Python 3.11+
- Standard library only (no test dependencies beyond unittest)
- Windows 10/11 x64 for packaging smoke
- PYTHONPATH=src

---

## Automated Test Suite

```
PYTHONPATH=src python -m unittest
```

Expected: All tests PASS.

---

## Desktop Smoke

```
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke
```

---

## CLI Smoke

```
PYTHONPATH=src python -m aurora_studio.cli smoke
PYTHONPATH=src python -m aurora_studio.cli provider-smoke
PYTHONPATH=src python -m aurora_studio.cli plugin-smoke
```

---

## Project Persistence Tests

```
PYTHONPATH=src python -m aurora_studio.cli create-demo --path ./tmp
PYTHONPATH=src python -m aurora_studio.cli validate-bundle --path ./tmp
PYTHONPATH=src python -m aurora_studio.cli rehydrate-bundle --path ./tmp
```

---

## Provider Dry-Run Tests

Covered by tests/test_provider_dry_run_adapter.py and tests/test_provider_adapter_qa_pack.py.

---

## Prompt Execution Tests

Covered by tests/test_prompt_execution_queue.py, tests/test_batch_prompt_export.py, tests/test_prompt_run_history.py.

---

## Plugin Sandbox Tests

Covered by tests/test_plugin_manifest_validation.py, tests/test_plugin_permission_model.py, tests/test_plugin_sandbox_boundary.py, tests/test_plugin_runtime_stub.py, tests/test_plugin_qa_security_checklist.py.

---

## Backup/Recovery Tests

Covered by tests/test_project_backup_recovery.py.

---

## Autosave Tests

Covered by tests/test_autosave_implementation.py.

---

## Undo/Redo Tests

Covered by tests/test_undo_redo_minimal_command_stack.py.

---

## Packaging Tests

Covered by tests/test_v0_3_packaging_update.py and tests/test_v0_3_portable_zip_rc_pack.py.

---

## Manual QA

- Launch desktop via run_desktop.bat (Windows only)
- Create project, add scene, shot, asset, character
- Save and reload bundle
- Run provider dry-run from Providers tab
- Validate manifest from Plugins tab
- Check plugin runtime is blocked
- Create backup via UI
- Enable autosave and write autosave
- Undo/redo an edit

---

## Evidence Requirements

- Automated test run output (tests PASS)
- Desktop smoke output (ok=true)
- CLI smoke outputs (ok=true)
- Plugin smoke output (sandbox_allowed=false, stub_status=blocked)
- Packaging doc review

---

## Known Limitations

- No real provider API testing.
- Plugin execution always blocked.
- Media preview not implemented.
- Windows-only packaging.
- Autosave writes placeholder bundle data only.
- Undo/redo covers 4 action types only.

---

## Go/No-Go Process

See V0_3_GO_NO_GO_TEMPLATE.md.
