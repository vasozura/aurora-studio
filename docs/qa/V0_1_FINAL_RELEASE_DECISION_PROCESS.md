# v0.1 Final Release Decision Process

Document ID: V0_1_FINAL_RELEASE_DECISION_PROCESS
Version: 0.1.0
Status: Process documentation
Task: TASK-000050

---

## Purpose

Define the formal process for making the v0.1.0 final release decision,
based on evidence collected during the v0.1.0-rc1 QA review.

This process determines whether the release candidate is promoted to a
final artifact, deferred, or rejected.

This task does not create an installer.
This task does not create MSIX.
This task does not code-sign binaries.
This task does not add database, provider integration, or plugin execution.

---

## Inputs

All of the following must exist and be reviewed before making a decision:

```text
docs/qa/V0_1_RELEASE_CANDIDATE_QA_PLAN.md
docs/qa/V0_1_REGRESSION_CHECKLIST.md
docs/qa/V0_1_PACKAGING_VALIDATION_CHECKLIST.md
docs/qa/V0_1_GO_NO_GO_REPORT_TEMPLATE.md
docs/qa/V0_1_FINAL_RELEASE_EVIDENCE_CHECKLIST.md
release-notes/AuroraStudio-v0.1.0-rc1.md
release-candidates/AuroraStudio-v0.1.0-rc1-windows-portable.zip
release-candidates/AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

---

## Required Evidence

Before a final decision can be made, the following evidence must be collected:

1. `python -m unittest` run and result recorded.
2. `--headless-smoke` run and JSON output captured.
3. All CLI smoke commands run and results recorded.
4. Desktop manual smoke completed (if a display was available).
5. Windows packaging commands run in full sequence:
   ```bat
   scripts\build_windows_onefolder.bat
   scripts\stage_windows_portable.bat
   scripts\smoke_portable_folder.bat
   scripts\create_portable_zip.bat
   scripts\smoke_portable_zip.bat
   ```
6. RC ZIP checksum verified.
7. RC ZIP contents inspected for exclusion violations.
8. Known limitations reviewed and explicitly accepted or rejected.
9. `docs/qa/V0_1_FINAL_RELEASE_DECISION_REPORT.md` filled in.

---

## Decision Options

The final decision must be one of:

**GO** — All pass criteria met, no open blockers, known limitations accepted.
Promotion to final artifact is allowed.

**NO-GO** — One or more blockers remain open, or pass criteria not met.
Promotion to final artifact is forbidden.

**GO WITH KNOWN LIMITATIONS** — No blockers. Pass criteria met.
Known limitations have been reviewed and explicitly accepted.
Promotion to final artifact is allowed with documented caveats.

**PENDING** — Review not yet complete. Default state.
Promotion is forbidden while decision is PENDING.

---

## Blocker Rules

**STOP RULE: If any blocker remains open, the final decision MUST be NO-GO.**

A blocker is any of:

- `python -m unittest` exits non-zero.
- `--headless-smoke` exits non-zero.
- Any CLI smoke command exits non-zero.
- Portable folder smoke exits non-zero.
- RC ZIP smoke exits non-zero.
- RC ZIP checksum does not match.
- RC ZIP contains a provider API key or credential.
- RC ZIP contains `.git/`.
- A crash or unhandled exception during any manual smoke step.

---

## Known Limitations Acceptance

All items in the known limitations list must be explicitly reviewed.
If any limitation is not accepted, it must be filed as an open blocker.

Required acceptance items:

```text
[ ] No installer (portable folder only)
[ ] No MSIX
[ ] No code signing (SmartScreen warning expected)
[ ] No database (in-memory state only)
[ ] No provider integration (no AI model calls)
[ ] No plugin execution (metadata only)
[ ] No real AFL semantic validation (structural only)
[ ] No real prompt generation
[ ] Not production ready
```

---

## Promotion Rules

Final artifact promotion is allowed only after Decision is GO or GO WITH KNOWN LIMITATIONS.

If decision is PENDING: promotion is forbidden.
If decision is NO-GO: promotion is forbidden.
If decision is GO: promotion is allowed.
If decision is GO WITH KNOWN LIMITATIONS: promotion is allowed with accepted caveats.

Promotion script (`scripts\promote_rc_to_final.bat`) will read the decision
report and refuse to run if the decision is PENDING or NO-GO.

---

## Final Artifact Naming

Release candidate:

```text
release-candidates/AuroraStudio-v0.1.0-rc1-windows-portable.zip
release-candidates/AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

Final artifacts:

```text
releases/AuroraStudio-v0.1.0-windows-portable.zip
releases/AuroraStudio-v0.1.0-windows-portable.sha256
```

Promotion copies the RC ZIP to the final name. It does not rebuild.
It does not re-stage. It does not mutate ZIP contents.

---

## Final Smoke Rules

After promotion, run:

```bat
scripts\smoke_final_portable_zip.bat
```

Expected: exits 0. ZIP extraction smoke passes.
If final smoke fails, the promotion is invalid.

---

## Rollback Rules

If final smoke fails after promotion:

1. Delete `releases/AuroraStudio-v0.1.0-windows-portable.zip`.
2. Delete `releases/AuroraStudio-v0.1.0-windows-portable.sha256`.
3. Update decision report to NO-GO.
4. Investigate failure before re-attempting promotion.

The RC ZIP in `release-candidates/` must never be deleted during rollback —
it is the source of truth.

---

## Non-Goals

This task does not implement:

- Automatic QA execution
- Automatic GO decision
- Installer
- MSIX
- Code signing
- Auto-update
- GitHub release automation
- Binary dependency audit
- Provider execution
- Plugin execution
- Database persistence
