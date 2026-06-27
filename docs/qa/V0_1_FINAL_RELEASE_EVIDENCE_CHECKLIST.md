# v0.1 Final Release Evidence Checklist

Document ID: V0_1_FINAL_RELEASE_EVIDENCE_CHECKLIST
Version: 0.1.0
Status: Checklist — fill in during final release review
Task: TASK-000050

Instructions: Work through each group in order.
Tick each checkbox as PASS. Mark failures and open blockers before proceeding.
Do not proceed to final promotion unless the decision report says GO or GO WITH KNOWN LIMITATIONS.

---

## Automated Tests

```bash
python -m unittest
```

- [ ] `python -m unittest` exits 0.
- [ ] All tests pass without display.
- [ ] All tests pass without PyInstaller.
- [ ] No test requires a network connection.
- [ ] No test requires a database.
- [ ] No test calls a provider API.
- [ ] No test executes plugin code.
- [ ] Test count recorded in decision report.

---

## Headless Smoke

```bash
python -m aurora_studio.ui.desktop_shell --headless-smoke
```

- [ ] Exits 0.
- [ ] Output is valid JSON.
- [ ] JSON contains `"ok": true`.
- [ ] JSON contains `"application": "aurora-studio"`.
- [ ] JSON contains `"shortcuts"` dict.
- [ ] JSON contains `"app_state"` with expected collections.
- [ ] Result recorded in decision report.

---

## CLI Smoke

```bash
python -m aurora_studio.cli smoke
python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"
python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project
python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project
```

- [ ] `cli smoke` exits 0 and prints valid JSON.
- [ ] `create-demo` exits 0.
- [ ] `validate-bundle` exits 0.
- [ ] `rehydrate-bundle` exits 0.
- [ ] All results recorded in decision report.

---

## Desktop Manual Smoke

*(Requires display — Windows recommended)*

- [ ] Window opens with title `Aurora Studio`.
- [ ] All 7 tabs visible.
- [ ] Project create works.
- [ ] Save Bundle writes `aurora_bundle.json`.
- [ ] Load Bundle restores state.
- [ ] Scene create works.
- [ ] Shot create works.
- [ ] Plugin panel does not execute plugin code.
- [ ] No crash observed during smoke.
- [ ] Manual smoke result recorded in decision report.

*(Mark NOT EXECUTED if no display was available and record in decision report.)*

---

## Packaging Scripts

```bat
scripts\build_windows_onefolder.bat
scripts\stage_windows_portable.bat
scripts\smoke_portable_folder.bat
scripts\create_portable_zip.bat
scripts\smoke_portable_zip.bat
```

PowerShell equivalents:

```powershell
.\scripts\build_windows_onefolder.ps1
.\scripts\stage_windows_portable.ps1
.\scripts\smoke_portable_folder.ps1
.\scripts\create_portable_zip.ps1
.\scripts\smoke_portable_zip.ps1
```

- [ ] `build_windows_onefolder.bat` exits 0.
- [ ] `dist\AuroraStudio\AuroraStudio.exe` exists after build.
- [ ] `stage_windows_portable.bat` exits 0.
- [ ] Staged folder layout is correct.
- [ ] `smoke_portable_folder.bat` exits 0.
- [ ] All packaging results recorded in decision report.

---

## Portable Folder Smoke

- [ ] `scripts\smoke_portable_folder.bat` exits 0.
- [ ] `smoke_desktop.bat` inside staged folder exits 0.
- [ ] No window opened.
- [ ] No provider API called.
- [ ] No plugin code executed.

---

## RC ZIP Smoke

- [ ] `scripts\create_portable_zip.bat` exits 0.
- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip` exists.
- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256` exists.
- [ ] `scripts\smoke_portable_zip.bat` exits 0.
- [ ] ZIP smoke exits 0.

---

## Checksum Verification

- [ ] SHA-256 checksum of RC ZIP is computed and recorded.
- [ ] SHA-256 file content matches ZIP hash.
- [ ] Checksum verified via script, not manually.

---

## Decision Report Completion

- [ ] `docs/qa/V0_1_FINAL_RELEASE_DECISION_REPORT.md` is filled in.
- [ ] All evidence sections contain actual results (not blanks).
- [ ] Known limitations are explicitly ticked.
- [ ] Open blockers section is complete (empty = no blockers).
- [ ] Decision field is updated from PENDING to GO, NO-GO, or GO WITH KNOWN LIMITATIONS.
- [ ] Reviewer name and date are filled in.

---

## Known Limitations Acceptance

- [ ] Decision report says GO or GO WITH KNOWN LIMITATIONS before final promotion.
- [ ] No open blocker remains.
- [ ] Known limitations are explicitly accepted.
- [ ] No installer limitation is accepted.
- [ ] No code signing limitation is accepted.
- [ ] No database limitation is accepted.
- [ ] No provider integration limitation is accepted.
- [ ] No plugin execution limitation is accepted.

---

## Final Promotion

Only after decision report is GO or GO WITH KNOWN LIMITATIONS:

```bat
scripts\promote_rc_to_final.bat
```

PowerShell equivalent:

```powershell
.\scripts\promote_rc_to_final.ps1
```

- [ ] Promotion script reads decision report first.
- [ ] Promotion script verifies RC checksum before copying.
- [ ] `releases\AuroraStudio-v0.1.0-windows-portable.zip` is created.
- [ ] `releases\AuroraStudio-v0.1.0-windows-portable.sha256` is created.
- [ ] Final ZIP is a copy of RC ZIP (not rebuilt).
- [ ] No installer was created.
- [ ] No code signing was attempted.

---

## Final ZIP Smoke

```bat
scripts\smoke_final_portable_zip.bat
```

PowerShell equivalent:

```powershell
.\scripts\smoke_final_portable_zip.ps1
```

- [ ] Final ZIP exists.
- [ ] Final checksum is verified.
- [ ] Final ZIP extracts correctly.
- [ ] Extracted layout matches expected structure.
- [ ] `smoke_desktop.bat` inside final ZIP exits 0.
- [ ] Smoke folder is cleaned up.
- [ ] Final smoke result recorded in decision report.
