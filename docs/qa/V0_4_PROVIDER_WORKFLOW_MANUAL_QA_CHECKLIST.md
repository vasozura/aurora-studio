# v0.4 Provider Workflow Manual QA Checklist

**Version**: 0.4.0
**Reviewer**: _____________
**Date**: _____________
**Environment**: _____________

---

## Instructions

Check each item. Mark PASS, FAIL, or N/A. Record evidence in the Evidence Template.

---

## Desktop Launch

- [ ] Desktop launches without error (`python -m aurora_studio.ui.desktop_shell --headless-smoke` returns ok=true)
- [ ] No import errors on startup
- [ ] No secrets in startup output

---

## Provider Tab Visible

- [ ] Provider tab is accessible in UI session
- [ ] Provider registry lists expected providers (dry-run-local, mock-image, mock-video)

---

## Text Provider Mock Path

- [ ] `text-provider-mock --provider openai-compatible --prompt "hello"` exits zero
- [ ] Response contains `ok: true`
- [ ] No secret values in stdout
- [ ] No network call in response (`network_call: false` or equivalent)

---

## Text Provider Readiness Path

- [ ] `text-provider-readiness --provider openai-compatible` exits zero
- [ ] Returns all prerequisites as unsatisfied
- [ ] No secret values in stdout

---

## Image Provider Mock Path

- [ ] `image-provider-mock --provider mock-image --prompt "test"` exits zero
- [ ] Response contains `status: mock`
- [ ] Image URI starts with `mock://`
- [ ] No secret values in stdout
- [ ] No image file created

---

## Image Provider Readiness Path

- [ ] `image-provider-readiness --provider mock-image` exits zero
- [ ] Returns `real_image_execution_ready: false`
- [ ] Lists 13 or more prerequisites, all unsatisfied

---

## Video Provider Mock Path

- [ ] `video-provider-mock --provider mock-video --prompt "test"` exits zero
- [ ] Response contains `status: mock`
- [ ] Video URI starts with `mock://`
- [ ] No secret values in stdout
- [ ] No video file created

---

## Video Provider Readiness Path

- [ ] `video-provider-readiness --provider mock-video` exits zero
- [ ] Returns `real_video_execution_ready: false`
- [ ] Lists 15 or more prerequisites, all unsatisfied

---

## Logs/History Visible and Sanitized

- [ ] Provider logs available via UISession
- [ ] Prompt run history available via UISession
- [ ] No API keys or secrets in log output
- [ ] Redaction utilities active

---

## No Secret Persistence

- [ ] No secrets written to project JSON
- [ ] No secrets written to autosave files
- [ ] No secrets written to backup files
- [ ] No secrets in run history export
- [ ] `safety-scan --root .` returns `overall_status: PASS`

---

## Project Save/Load After Provider Actions

- [ ] `create-demo` succeeds
- [ ] `validate-bundle` succeeds after demo creation
- [ ] `rehydrate-bundle` succeeds after validate

---

## Plugin Execution Remains Blocked

- [ ] `PluginRuntimeStub.is_runtime_enabled()` returns False
- [ ] Plugin execution via UISession returns disabled status
- [ ] No plugin packages executed

---

## Autosave/Backup Unaffected

- [ ] Autosave does not write provider secrets
- [ ] Backup does not write provider secrets
- [ ] Undo/redo stack does not expose secrets

---

## Packaging Smoke

- [ ] `safety-scan --root .` returns PASS
- [ ] Packaging smoke scripts present (`.ps1`, `.bat`)
- [ ] Scripts check for exclusion of `.env`, secrets

---

## Sign-off

Reviewer: _____________
Date: _____________
Decision: PASS / FAIL / PENDING

---

*Aurora Studio v0.4 — TASK-000123*
