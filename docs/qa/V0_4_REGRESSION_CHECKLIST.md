# v0.4 Regression Checklist

**Version**: 0.4.0
**Reviewer**: _____________
**Date**: _____________

---

## Instructions

Check each item before approving release. All items must be checked before a GO decision.

---

## Automated Tests

- [ ] `python -m unittest` passes — 0 failures, 0 errors

---

## Desktop Headless Smoke

- [ ] `python -m aurora_studio.ui.desktop_shell --headless-smoke` returns `{"ok": true}`

---

## CLI Smoke

- [ ] `python -m aurora_studio.cli smoke` returns `{"ok": true}`

---

## Create Demo Project

- [ ] `python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"` exits 0

---

## Validate Bundle

- [ ] `python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project` returns `{"ok": true}`

---

## Rehydrate Bundle

- [ ] `python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project` returns `{"ok": true}`

---

## Provider Smoke

- [ ] `python -m aurora_studio.cli provider-smoke` returns `{"ok": true}`

---

## Provider Test dry_run

- [ ] `python -m aurora_studio.cli provider-test --provider dry-run --mode dry_run` returns `{"ok": true}`

---

## Text Provider Mock (if implemented)

- [ ] `python -m aurora_studio.cli text-provider-mock --provider openai-compatible --prompt "hello"` exits 0

---

## Text Provider Readiness (if implemented)

- [ ] `python -m aurora_studio.cli text-provider-readiness --provider openai-compatible` exits 0 — prerequisites unsatisfied

---

## Image Provider Mock (if implemented)

- [ ] `python -m aurora_studio.cli image-provider-mock --provider mock-image --prompt "test"` exits 0 — status=mock

---

## Image Provider Readiness (if implemented)

- [ ] `python -m aurora_studio.cli image-provider-readiness --provider mock-image` exits 0 — real_image_execution_ready=false

---

## Video Provider Mock (if implemented)

- [ ] `python -m aurora_studio.cli video-provider-mock --provider mock-video --prompt "test"` exits 0 — status=mock

---

## Video Provider Readiness (if implemented)

- [ ] `python -m aurora_studio.cli video-provider-readiness --provider mock-video` exits 0 — real_video_execution_ready=false

---

## Safety Scan (if implemented)

- [ ] `python -m aurora_studio.cli safety-scan --root .` exits 0 — overall_status=PASS

---

## Packaging Secret Safety Smoke

- [ ] `scripts/smoke_v0_4_portable_secret_safety.ps1` or `.bat` returns RESULT: PASS

---

## Plugin Runtime Remains Blocked

- [ ] `PluginRuntimeStub.is_runtime_enabled()` returns False
- [ ] No plugin execution proceeds

---

## No Provider SDKs

- [ ] No `import openai` / `from openai` in source
- [ ] No `import anthropic` / `from anthropic` in source
- [ ] No `import requests` in source
- [ ] Safety scan confirms PASS

---

## No Real API Keys Stored

- [ ] No API key files present
- [ ] No `.env` files present
- [ ] `safety-scan` confirms no secret patterns

---

## No Secrets in Artifacts

- [ ] Project JSON contains no secrets
- [ ] Autosave files contain no secrets
- [ ] Backup files contain no secrets
- [ ] Logs contain no secrets
- [ ] Run history contains no secrets

---

## Sign-off

Reviewer: _____________
Date: _____________
All items checked: YES / NO
Decision: GO / NO-GO / GO WITH KNOWN LIMITATIONS / PENDING

---

*Aurora Studio v0.4 — TASK-000125*
