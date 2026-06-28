# v0.4 Provider Workflow Regression Plan

**Version**: 0.4.0
**Status**: Active

---

## Purpose

Define the regression test scope, environment, and pass/fail criteria for the v0.4 provider
workflow release. This plan covers all provider mock/readiness workflows, secret safety,
plugin boundary, and packaging verification.

---

## Scope

- Provider execution gate (text / image / video)
- Text provider dry_run and mock workflow
- Text provider readiness check (always blocked)
- Image provider mock workflow
- Image provider readiness check (always blocked)
- Video provider mock workflow
- Video provider readiness check (always blocked)
- Provider logs and prompt run history
- Secret redaction utilities
- Provider config safe snapshots
- Packaging secret safety
- Plugin boundary regression
- Desktop import / headless safety
- CLI provider commands
- Project persistence after provider actions

---

## Out of Scope

- Real image provider API calls
- Real video provider API calls
- Provider SDK tests
- Real API key storage tests
- Media decoding tests
- Plugin execution tests
- Database tests
- Load/performance tests
- OS keyring tests
- Installer / MSIX / code signing tests

---

## Required Environment

- Python 3.10+
- `PYTHONPATH=src`
- Standard library only
- No network access required
- No provider API keys required
- No external tools required (no ffmpeg, imagemagick, etc.)

---

## Automated Tests

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache PYTHONPATH=src python -m unittest
```

Expected: all tests pass, 0 failures.

---

## Desktop Smoke

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke
```

Expected: `{"ok": true}`

---

## CLI Smoke

```bash
PYTHONPATH=src python -m aurora_studio.cli smoke
```

Expected: `{"ok": true}`

---

## Project Persistence

```bash
PYTHONPATH=src python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"
PYTHONPATH=src python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project
PYTHONPATH=src python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project
```

Expected: all return `{"ok": true}`

---

## Provider Readiness

```bash
PYTHONPATH=src python -m aurora_studio.cli provider-smoke
PYTHONPATH=src python -m aurora_studio.cli provider-test --provider dry-run --mode dry_run
```

Expected: both return `{"ok": true}`

---

## Text Provider Mock/Readiness Workflow

```bash
PYTHONPATH=src python -m aurora_studio.cli text-provider-mock --provider openai-compatible --prompt "hello"
PYTHONPATH=src python -m aurora_studio.cli text-provider-readiness --provider openai-compatible
```

Expected: mock returns `{"ok": true}`, readiness returns prerequisites all unsatisfied.

---

## Image Provider Mock/Readiness Workflow

```bash
PYTHONPATH=src python -m aurora_studio.cli image-provider-mock --provider mock-image --prompt "test image"
PYTHONPATH=src python -m aurora_studio.cli image-provider-readiness --provider mock-image
```

Expected: mock returns `{"status": "mock"}`, readiness returns `real_image_execution_ready: false`.

---

## Video Provider Mock/Readiness Workflow

```bash
PYTHONPATH=src python -m aurora_studio.cli video-provider-mock --provider mock-video --prompt "test video"
PYTHONPATH=src python -m aurora_studio.cli video-provider-readiness --provider mock-video
```

Expected: mock returns `{"status": "mock"}`, readiness returns `real_video_execution_ready: false`.

---

## Provider Logs/History

UISession methods `list_provider_logs()`, `list_prompt_run_history()` must return sanitized
results with no secret values.

---

## Secret Redaction

`redact_secret()` must mask all but last 4 chars. Sanitize functions must strip forbidden
parameter keys from payloads. No secrets appear in CLI output.

---

## Packaging Secret Safety

```bash
PYTHONPATH=src python -m aurora_studio.cli safety-scan --root .
```

Expected: `{"overall_status": "PASS"}`

---

## Plugin Boundary Regression

`PluginRuntimeStub.is_runtime_enabled()` must return `False`. Plugin execution must not proceed.

---

## Known Limitations

- Run history is in-memory and ephemeral between sessions.
- Real provider execution requires future work (all gates blocked in v0.4).
- Desktop headless smoke does not test GUI rendering.
- `text-provider-mock` uses openai-compatible stub — no real network.

---

## Evidence Requirements

For each test session, record: environment, Python version, date, reviewer, automated test count,
CLI command outputs, safety scan result.

---

## Pass/Fail Criteria

PASS if:
- All automated tests pass (0 failures, 0 errors)
- All CLI smoke commands return expected output
- Safety scan returns PASS
- No secrets in CLI output
- Plugin runtime remains disabled

FAIL if:
- Any automated test fails
- Any CLI smoke command exits non-zero unexpectedly
- Safety scan returns FAIL
- Any secret value appears in CLI output
- Plugin execution is enabled

---

*Aurora Studio v0.4 — TASK-000123*
