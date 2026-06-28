# Aurora Studio v0.4.0-rc1 Release Notes

**Release type**: Release Candidate (NOT FOR PRODUCTION USE)
**Status**: PENDING — awaiting go/no-go decision
**Date**: 2026-06-28

---

## This release is a draft and must not claim production readiness.

---

## Included

- Provider execution gate (text / image / video)
- Text provider dry_run and mock workflow
- Text provider readiness check
- Image provider mock bridge (`mock://image/<id>`)
- Image provider readiness check
- Video provider mock bridge (`mock://video/<id>`)
- Video provider readiness check
- Secret redaction utilities
- Provider config safe snapshots
- Provider logs and prompt run history (in-memory)
- Source and packaging safety scan (`safety-scan`)
- Health audit report
- Provider workflow regression QA docs
- Packaging secret safety docs and scripts

---

## Not Included

- Provider SDKs (OpenAI, Anthropic, Google, Runway, Kling, Pika, etc.)
- Real image provider execution
- Real video provider execution
- Real text provider execution via network
- Persistent API key storage
- OS keyring implementation
- Plugin execution
- Database
- Media decoding
- Installer / MSIX / code signing
- Production readiness

---

## How to Run

```bash
PYTHONPATH=src python -m aurora_studio.ui.desktop_shell --headless-smoke
PYTHONPATH=src python -m aurora_studio.cli smoke
PYTHONPATH=src python -m aurora_studio.cli provider-smoke
```

---

## How to Smoke Test

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache PYTHONPATH=src python -m unittest
PYTHONPATH=src python -m aurora_studio.cli safety-scan --root .
PYTHONPATH=src python -m aurora_studio.cli image-provider-mock --provider mock-image --prompt "test"
PYTHONPATH=src python -m aurora_studio.cli video-provider-mock --provider mock-video --prompt "test"
```

---

## Known Limitations

- Real provider execution requires future implementation.
- OS keyring not implemented.
- Desktop GUI rendering not tested (headless QA only).
- Portable ZIP creation not scripted.
- Not production-ready.

---

## Validation

See `docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md` for go/no-go evidence.

---

## Decision Status

PENDING — reviewer must complete `docs/qa/V0_4_GO_NO_GO_TEMPLATE.md`
and update `docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md`.

---

*Aurora Studio v0.4.0-rc1 — This is not a production release.*
