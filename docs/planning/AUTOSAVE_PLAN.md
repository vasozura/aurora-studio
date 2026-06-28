# Autosave Plan — Aurora Studio

## Purpose

This document describes the planned autosave behavior for Aurora Studio.
Autosave is not implemented in TASK-000066.
This document is planning only.

## Current Save Behavior

The user invokes save explicitly via the desktop Save button or the UISession save_bundle() method.
Save writes a JSON bundle to the project directory.
Before overwriting, a timestamped backup is written to `.backups/`.

## Non-goals

- No autosave is implemented in TASK-000066.
- No background timer is added.
- No thread is added.
- No background worker or daemon is created.
- No OS-level file watcher is used.

## Autosave Trigger Policy (Future)

When implemented, autosave should trigger:

- After a configurable idle debounce interval (e.g. 30 seconds) following a change.
- Only when the project has unsaved (dirty) changes.
- Never during a manual save operation.
- Never during bundle export or import.

## Manual Save Priority

Manual save remains the source of truth.
Manual save clears autosave recovery state.
If autosave and manual save conflict, the manual save wins unconditionally.
Autosave must never silently destroy user data.

## Backup Location (Future)

Autosave should write to a recovery file, not overwrite the main bundle.

Recommended recovery file path:

```
<project_dir>/.autosave/aurora_bundle.autosave.json
```

Backups before overwrite remain in `.backups/` as today.

## Recovery Flow (Future)

1. On startup, check for `.autosave/aurora_bundle.autosave.json`.
2. If found and newer than main bundle, prompt user to recover.
3. User chooses: Recover, Discard, or Ignore.
4. If Recover: copy autosave to main bundle, then load.
5. If Discard: delete autosave file.
6. If Ignore: leave autosave file, load main bundle.

## Conflict Behavior

If autosave file exists but main bundle is newer:

- Do not overwrite main bundle with autosave.
- Prompt user with timestamps for both files.
- Let user decide.

## Corruption Protection

- Autosave must write to a temp file first, then rename.
- Never write partial JSON to the main autosave path.
- If autosave write fails, log warning and continue — do not crash.
- If autosave file is corrupt on startup, discard and log.
- Autosave must use backups or recovery files, never direct overwrite.

## UI Indicators (Future)

- Show a dirty indicator (e.g. asterisk in title bar) when unsaved changes exist.
- Show "Autosaving..." briefly when autosave fires.
- Show "Saved" or timestamp after successful save.

## Failure Handling

- If autosave fails, show a non-blocking warning.
- Do not block the user from working.
- Log the error to the application log.
- Do not crash the application.

## Testing Strategy

Unit tests should cover:

- Dirty state tracking (future).
- Autosave trigger conditions (future).
- Recovery prompt logic (future).
- Corruption detection (future).
- Existing backup-before-overwrite behavior (tested in test_project_json_hardening.py).

## Future Implementation Tasks

- TASK-AUTOSAVE-001: Add dirty state tracking to managers.
- TASK-AUTOSAVE-002: Add debounce timer to desktop shell.
- TASK-AUTOSAVE-003: Implement recovery file write with temp-rename.
- TASK-AUTOSAVE-004: Implement startup recovery prompt.
- TASK-AUTOSAVE-005: Add backup retention policy.
- TASK-AUTOSAVE-006: Implement corrupt autosave detection.

Autosave implementation requires a later task.

## Risks

- Autosave with threading requires careful locking.
- Frequent autosave can cause performance issues on large bundles.
- Recovery prompt adds startup complexity.
- Corrupt autosave could confuse users.

## Acceptance Criteria (Future)

- Autosave fires after idle debounce.
- Autosave never overwrites main bundle directly.
- Startup recovery prompt appears when autosave file is newer.
- Manual save always wins over autosave.
- Corrupt autosave is detected and discarded with a warning.
- All autosave behavior is covered by unit tests.
