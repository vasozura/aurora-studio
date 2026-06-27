# Aurora Studio v0.1.0

**VALIDITY GUARD:** This final release note is valid only after
`docs/qa/V0_1_FINAL_RELEASE_DECISION_REPORT.md` records
GO or GO WITH KNOWN LIMITATIONS.

While the decision report says PENDING or NO-GO, this document
is a draft and must not be used to represent a completed release.

---

## Release Type

Final release — Windows portable folder (one-folder PyInstaller build)

Based on:

```text
AuroraStudio-v0.1.0-rc1-windows-portable.zip
```

Final artifact:

```text
releases/AuroraStudio-v0.1.0-windows-portable.zip
releases/AuroraStudio-v0.1.0-windows-portable.sha256
```

---

## Based On

Release candidate: AuroraStudio-v0.1.0-rc1
Tasks: TASK-000045 through TASK-000050

---

## Included

Aurora Studio v0.1.0 includes:

- Local desktop shell (tkinter, no external GUI framework)
- Project create/open
- Scene and Shot basics
- Timeline, Asset and Character smoke panels
- AFL, Export and Plugin metadata smoke panels
- Local JSON bundle save/load (aurora_bundle.json)
- Bundle rehydration
- CLI smoke commands (smoke, create-demo, validate-bundle, rehydrate-bundle)
- Windows portable folder layout
- Portable ZIP release candidate process

---

## How to Run

Extract the ZIP to a folder of your choice:

```text
AuroraStudio-v0.1.0-windows-portable.zip
```

Inside the extracted folder:

```bat
run_desktop.bat
```

---

## How to Smoke Test

```bat
smoke_desktop.bat
```

Expected: exits 0, prints `"ok": true` JSON.

---

## Known Limitations

- No installer — portable folder only.
- No code signing — SmartScreen warning expected on first launch.
- No database — all state is in-memory, persisted only via JSON bundle.
- No provider integration — no AI model calls.
- No plugin execution — plugin panel shows metadata only.
- No real AFL semantic validation — structural checks only.
- No real prompt generation — not implemented.
- Not production ready.

---

## Not Included

- No installer
- No MSIX
- No code signing
- No database
- No provider integration
- No plugin execution
- No real AFL semantic validation
- No real prompt generation
- No production readiness claim

---

## Validation

This release was validated using:

- `docs/qa/V0_1_RELEASE_CANDIDATE_QA_PLAN.md`
- `docs/qa/V0_1_REGRESSION_CHECKLIST.md`
- `docs/qa/V0_1_PACKAGING_VALIDATION_CHECKLIST.md`
- `docs/qa/V0_1_GO_NO_GO_REPORT_TEMPLATE.md`
- `docs/qa/V0_1_FINAL_RELEASE_DECISION_PROCESS.md`
- `docs/qa/V0_1_FINAL_RELEASE_DECISION_REPORT.md`
- `docs/qa/V0_1_FINAL_RELEASE_EVIDENCE_CHECKLIST.md`

Decision report must show GO or GO WITH KNOWN LIMITATIONS before
this document is considered valid.

---

## Final Artifact

```text
releases/AuroraStudio-v0.1.0-windows-portable.zip
releases/AuroraStudio-v0.1.0-windows-portable.sha256
```

SHA-256: (recorded in decision report after promotion)
