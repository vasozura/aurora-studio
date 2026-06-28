# v0.4 Release Candidate QA Plan

**Version**: 0.4.0-rc1
**Status**: Active

---

## Purpose

Define QA requirements for the v0.4.0 release candidate. This plan gates promotion of rc1
to final release. No release may be approved without evidence satisfying each section.

---

## Release Candidate Target

- Package: Aurora Studio v0.4.0-rc1
- Scope: provider execution mock/readiness, secret redaction, safety scan, packaging safety

---

## Included Scope

- Real-provider readiness boundary (all prerequisites unsatisfied, blocked by default)
- First gated text provider path (dry_run mode)
- Text provider mock/readiness workflow
- Image provider mock bridge
- Video provider mock bridge
- Secret redaction utilities
- Provider logs/history (in-memory, sanitized)
- Provider workflow QA
- Packaging secret safety

---

## Excluded Scope

- Provider SDKs (OpenAI, Anthropic, Google, etc.)
- Real image provider execution
- Real video provider execution
- Persistent API key storage
- OS keyring implementation
- Plugin execution
- Database
- Media decoding
- Installer/MSIX/code signing
- Production readiness claim

---

## Prerequisites

- All TASK-000101 through TASK-000124 completed and marked DONE
- `python -m unittest` passes with 0 failures
- Health audit report exists (`docs/qa/V0_4_PROVIDER_EXECUTION_HEALTH_AUDIT_REPORT.md`)
- Safety scan passes (`safety-scan --root .` returns PASS)
- Packaging safety docs exist

---

## Required Automated Tests

```bash
PYTHONPYCACHEPREFIX=/tmp/pycache PYTHONPATH=src python -m unittest
```

Expected: 0 failures, 0 errors.

---

## Required Provider Workflow Smoke

```bash
PYTHONPATH=src python -m aurora_studio.cli provider-smoke
PYTHONPATH=src python -m aurora_studio.cli provider-test --provider dry-run --mode dry_run
PYTHONPATH=src python -m aurora_studio.cli text-provider-mock --provider openai-compatible --prompt "hello"
PYTHONPATH=src python -m aurora_studio.cli text-provider-readiness --provider openai-compatible
PYTHONPATH=src python -m aurora_studio.cli image-provider-mock --provider mock-image --prompt "test"
PYTHONPATH=src python -m aurora_studio.cli image-provider-readiness --provider mock-image
PYTHONPATH=src python -m aurora_studio.cli video-provider-mock --provider mock-video --prompt "test"
PYTHONPATH=src python -m aurora_studio.cli video-provider-readiness --provider mock-video
```

All must exit 0 with expected output.

---

## Required Safety Scan

```bash
PYTHONPATH=src python -m aurora_studio.cli safety-scan --root .
```

Expected: `{"overall_status": "PASS"}`

---

## Required Packaging Secret Safety Smoke

Run: `scripts/smoke_v0_4_portable_secret_safety.ps1` or `.bat` against the release folder.

Expected: RESULT: PASS

---

## Required Desktop Manual QA

See: `docs/qa/V0_4_PROVIDER_WORKFLOW_MANUAL_QA_CHECKLIST.md`

All checkboxes must be marked PASS.

---

## Required CLI QA

All CLI commands in the regression plan must be executed and produce expected output.

See: `docs/qa/V0_4_PROVIDER_WORKFLOW_REGRESSION_PLAN.md`

---

## Known Limitations

- Real provider execution is not included in this RC scope.
- Portable ZIP creation is not scripted.
- OS keyring is not implemented.
- Desktop GUI is headless-only in this QA run.

---

## Go/No-Go Process

1. Complete all required automated tests.
2. Complete all required CLI smoke commands.
3. Complete desktop manual QA checklist.
4. Run safety scan.
5. Run packaging secret safety smoke.
6. Fill in `docs/qa/V0_4_GO_NO_GO_TEMPLATE.md`.
7. Fill in `docs/qa/V0_4_FINAL_RELEASE_DECISION_REPORT.md` with decision.
8. If decision is GO or GO WITH KNOWN LIMITATIONS, run promotion script.

---

## Evidence Collection

All evidence must be recorded in `docs/qa/V0_4_PROVIDER_WORKFLOW_EVIDENCE_TEMPLATE.md`
before a GO decision may be made.

---

*Aurora Studio v0.4 — TASK-000125*
