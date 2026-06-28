# Prompt Execution Workflow QA — Aurora Studio v0.3

Status: QA Planning
Task: TASK-000085
Version: 0.3.0
Date: 2026-06-28

---

## Purpose

This document describes the manual and automated QA workflow for the v0.3
prompt execution system.

---

## Manual Dry-Run Workflow

1. Open Aurora Studio desktop.
2. Navigate to the Providers tab.
3. Click "Refresh Providers" — verify dry-run-local appears as available.
4. Enter a prompt in the Dry Run section.
5. Click "Execute Dry Run".
6. Verify output_text appears and contains [DRY-RUN].
7. Verify no network requests were made.
8. Navigate to Provider Logs — verify a log entry was created.
9. Navigate to Run History — verify a dry_run entry exists.

---

## Manual Batch Export Workflow

1. Open Aurora Studio desktop.
2. Navigate to the Providers tab.
3. In the Batch Prompt Export section, enter:
   - Source Type: scene
   - Source IDs: s1,s2,s3
   - Template ID: default-scene-basic
4. Click "Create Batch Export".
5. Verify batch result shows total_count=3, success_count=3.
6. Navigate to Exports — verify export artifacts were created.
7. Verify no provider was invoked.

---

## Manual Run History Workflow

1. Execute at least one dry-run.
2. Navigate to Run History.
3. Click "Refresh History".
4. Verify the dry_run entry appears.
5. Check prompt_preview is truncated and sanitized.
6. Click "Clear History".
7. Verify history is empty.

---

## Manual Error Handling Workflow

1. Enter an empty prompt in the Dry Run section.
2. Click "Execute Dry Run".
3. Verify ok=False and a compact error message appears.
4. Disable the dry-run provider via "Disable Provider".
5. Click "Execute Dry Run".
6. Verify ok=False with message "Provider... is disabled".
7. Re-enable provider via "Enable Provider".

---

## Expected Safe Failures

The following must fail gracefully (ok=False, compact message, no traceback):

- Empty prompt text → validation_error
- Unknown provider_id → provider_not_configured
- Disabled provider → provider_disabled
- Empty source_type for queue enqueue → validation_error
- Empty source_ids for batch export → validation_error
- No template or profile for batch export → validation_error

---

## Regression Commands

Run after any change to provider or prompt execution code:

```bash
python -m unittest
python -m aurora_studio.ui.desktop_shell --headless-smoke
python -m aurora_studio.cli smoke
python -m aurora_studio.cli provider-smoke
```

Expected: all pass, no provider SDK imported, no network calls made.

---

## Evidence Checklist

Before marking v0.3 provider foundation as QA-ready:

- [ ] python -m unittest passes (all tests, no failures)
- [ ] python -m aurora_studio.ui.desktop_shell --headless-smoke outputs ok:true
- [ ] python -m aurora_studio.cli smoke passes
- [ ] python -m aurora_studio.cli provider-smoke outputs JSON
- [ ] No openai/anthropic module present in sys.modules after test run
- [ ] No secrets appear in log output
- [ ] docs/v0_3/PROVIDER_FOUNDATION_QA_CHECKLIST.md exists
- [ ] docs/v0_3/PROMPT_EXECUTION_WORKFLOW_QA.md exists
- [ ] docs/pipeline/V0_3_PIPELINE_PROGRESS.md lists TASK-000085 DONE

---

## Go/No-Go for Future Real Provider Implementation

A later task may implement real provider calls. Before that task begins:

- [ ] OS keychain abstraction is designed
- [ ] Per-provider API key write/read/delete is implemented
- [ ] Key validation does not require a real API call
- [ ] Log sanitizer covers all known secret patterns
- [ ] Bundle export test asserts no key fields
- [ ] Security boundary document is updated
- [ ] Architecture boundary document is updated

No real provider call may be added without explicit sprint authorization.
