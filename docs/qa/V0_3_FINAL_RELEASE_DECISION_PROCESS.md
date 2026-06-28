# Aurora Studio v0.3 Final Release Decision Process

## Purpose

Define the final release decision process for Aurora Studio v0.3.

Final release cannot be approved automatically.
Default decision is PENDING.
If blockers exist, decision must be NO-GO.
GO requires passing automated tests, manual QA and packaging validation evidence.

---

## Prerequisites

- TASK-000091 through TASK-000099 completed.
- V0_3_GO_NO_GO_TEMPLATE.md filled by authorized reviewer.
- V0_3_FINAL_RELEASE_EVIDENCE_CHECKLIST.md all items checked.
- RC ZIP exists and SHA256 verified.
- Zero open blockers.

---

## Required Evidence

- Automated test output: all tests PASS.
- Headless smoke: ok=true.
- CLI smoke: ok=true.
- provider-smoke: ok=true.
- plugin-smoke: ok=true, sandbox_allowed=false, stub_status=blocked.
- Portable ZIP RC created.
- SHA256 verified.
- Manual desktop QA completed.
- No secrets bundled (confirmed).
- No provider SDKs bundled (confirmed).

---

## Decision Roles

- Reviewer: authorized team member who ran QA.
- Approver: may be same as reviewer for internal RC.

---

## Allowed Decisions

- GO
- NO-GO
- GO WITH KNOWN LIMITATIONS
- PENDING (default)

---

## Promotion Process

If decision is GO or GO WITH KNOWN LIMITATIONS:

```powershell
.\scripts\promote_v0_3_rc_to_final.ps1
```

Script checks decision status in report before promoting.
Script fails if decision is PENDING or NO-GO.

---

## Final Artifact Naming

```
releases/AuroraStudio-v0.3.0-windows-portable.zip
releases/AuroraStudio-v0.3.0-windows-portable.zip.sha256
```

---

## Smoke Final Artifact

```powershell
.\scripts\smoke_v0_3_final_portable_zip.ps1
```

---

## Rollback Rule

If final smoke fails after promotion, roll back by:
- Removing final artifact from releases/.
- Returning decision to NO-GO in decision report.
- Blocking any distribution of the failed artifact.

---

## Known Limitations

- No installer/MSIX. Portable ZIP only.
- No code signing.
- No auto-update.
- Media preview not included.
- Plugin execution disabled.

---

## No Automatic Approval Rule

Final release cannot be approved automatically.
Default decision is PENDING.
If blockers exist, decision must be NO-GO.
GO requires explicit human sign-off with complete evidence.
