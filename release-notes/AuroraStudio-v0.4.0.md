# Aurora Studio v0.4.0 Release Notes

**Release type**: DRAFT — do not distribute
**Status**: PENDING — awaiting go/no-go decision
**Date**: _____________

---

## This document is a draft. It must not claim production readiness.
## It must remain PENDING until an explicit GO decision is recorded.

---

## Included

- Provider execution gate (text / image / video)
- Text provider dry_run and mock workflow
- Text provider readiness check
- Image provider mock bridge
- Image provider readiness check
- Video provider mock bridge
- Video provider readiness check
- Secret redaction utilities
- Provider config safe snapshots
- Provider logs and prompt run history
- Source and packaging safety scan
- Health audit report
- Provider workflow regression QA docs
- Packaging secret safety docs and scripts

---

## Not Included

- Provider SDKs
- Real image/video/text provider execution
- Persistent API key storage
- OS keyring
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
```

---

## How to Smoke Test

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache PYTHONPATH=src python -m unittest
PYTHONPATH=src python -m aurora_studio.cli safety-scan --root .
```

---

## Known Limitations

- Real provider execution not implemented.
- Not production-ready.
- OS keyring not implemented.
- Portable ZIP creation not scripted.

---

## Validation

See `docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md`.

---

## Decision Status

PENDING — this document must not be used to approve a release until
`docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md` records an explicit GO decision.

---

*Aurora Studio v0.4.0 — DRAFT. Not production-ready.*
