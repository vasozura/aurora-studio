# v0.4 Provider Workflow Evidence Template

**Version**: 0.4.0

---

## Reviewer

Name: _____________

---

## Date

Date: _____________

---

## Environment

OS: _____________
Python version: _____________
Shell: _____________
Working directory: _____________

---

## Build/Source Revision

Source revision / commit: _____________
Branch: _____________

---

## Automated Test Evidence

Command run:

```
PYTHONPYCACHEPREFIX=/tmp/pycache PYTHONPATH=src python -m unittest
```

Result:
- Tests run: _____
- Failures: _____
- Errors: _____
- Skipped: _____
- Outcome: PASS / FAIL

---

## CLI Smoke Evidence

| Command | Exit Code | Result |
|---|---|---|
| `python -m aurora_studio.cli smoke` | | |
| `python -m aurora_studio.cli provider-smoke` | | |
| `python -m aurora_studio.cli provider-test --provider dry-run --mode dry_run` | | |

---

## Desktop Manual QA Evidence

| Check | Result | Notes |
|---|---|---|
| Headless smoke | | |
| No import errors | | |
| No secrets in startup | | |

---

## Provider Workflow Evidence

| Workflow | Command | Status | Output excerpt |
|---|---|---|---|
| text-provider-mock | `text-provider-mock --provider openai-compatible --prompt "hello"` | | |
| text-provider-readiness | `text-provider-readiness --provider openai-compatible` | | |
| image-provider-mock | `image-provider-mock --provider mock-image --prompt "test"` | | |
| image-provider-readiness | `image-provider-readiness --provider mock-image` | | |
| video-provider-mock | `video-provider-mock --provider mock-video --prompt "test"` | | |
| video-provider-readiness | `video-provider-readiness --provider mock-video` | | |

---

## Safety Scan Evidence

Command: `python -m aurora_studio.cli safety-scan --root .`

Result:
- overall_status: _____________
- forbidden_imports errors: _____
- forbidden_network_usage errors: _____
- forbidden_media_usage errors: _____
- packaging warnings: _____

---

## Packaging Evidence

| Check | Result |
|---|---|
| No .env files in portable folder | |
| No api_key/token/secret files | |
| README/NOTICE present | |
| Smoke scripts present | |

---

## Known Limitations

_List any known limitations accepted for this release:_

---

## Open Blockers

_List any open blockers (if any, decision must be NO-GO):_

---

## Decision Recommendation

Decision: PASS / FAIL / PENDING

Notes: _____________

---

*Aurora Studio v0.4 — TASK-000123*
