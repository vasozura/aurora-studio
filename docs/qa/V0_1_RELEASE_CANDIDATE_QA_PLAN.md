# v0.1 Release Candidate QA Plan

Document ID: V0_1_RELEASE_CANDIDATE_QA_PLAN
Version: 0.1.0
Status: QA process documentation only — not a final release
Task: TASK-000049

---

## Purpose

Define the repeatable QA process for reviewing Aurora Studio v0.1.0-rc1.

This plan covers source-level regression, CLI smoke, desktop UI smoke,
packaging validation, and the go/no-go decision procedure.

This is QA process documentation only.
This is not a final release.
No installer is included.
No database is included.
No provider integration is included.
No plugin execution is enabled.
No production readiness claim is made.

---

## Release Candidate Under Review

```text
AuroraStudio-v0.1.0-rc1-windows-portable.zip
```

SHA-256 checksum file:

```text
AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

Located in:

```text
release-candidates/
```

---

## QA Scope

1. Source-level unit test regression
2. CLI smoke commands
3. Desktop headless smoke
4. Desktop manual UI smoke (display required)
5. Windows one-folder build
6. Portable folder staging and layout validation
7. Portable ZIP creation and checksum
8. Portable ZIP extraction smoke
9. Known limitations review

---

## Out of Scope

- Final release approval (later task)
- Installer validation (not built)
- MSIX validation (not built)
- Code signing validation (not applied)
- Provider integration testing (not implemented)
- Plugin execution testing (not implemented)
- Real AFL semantic validation (structural only)
- Real prompt generation testing (not implemented)
- Production load or performance testing
- Multi-user or network testing
- Automated UI test framework

---

## Test Environments

**Source regression:**
- Any OS with Python 3.11+
- No display required

**Desktop manual smoke:**
- Windows 10 or 11 (64-bit) with display
- Python 3.11+ installed

**Packaging QA:**
- Windows 10 or 11 (64-bit)
- Python 3.11+ installed
- PyInstaller installed (`pip install -r build\requirements-build.txt`)

---

## Required Commands

### Source regression

```bash
python -m unittest
```

Expected: exits 0. All tests pass.

### Headless smoke

```bash
python -m aurora_studio.ui.desktop_shell --headless-smoke
```

Expected: exits 0. Prints valid JSON with `"ok": true`.

### CLI smoke

```bash
python -m aurora_studio.cli smoke
python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"
python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project
python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project
```

Expected: all exit 0. JSON output where applicable.

---

## Required Windows Packaging Commands

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

Each must exit 0 to pass.

---

## Required Artifacts

After a full packaging QA pass, these must exist:

```text
dist\AuroraStudio\AuroraStudio.exe
dist-portable\AuroraStudio-v0.1.0-windows-portable\
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

None of these may be committed to the repository.

---

## Pass Criteria

All of the following must be true for a GO decision:

1. `python -m unittest` exits 0.
2. `--headless-smoke` exits 0 and prints valid JSON.
3. All CLI smoke commands exit 0.
4. PyInstaller one-folder build succeeds.
5. Portable folder staging produces the correct layout.
6. Portable folder smoke exits 0.
7. Release candidate ZIP is created with correct name.
8. SHA-256 checksum file is created.
9. ZIP checksum is verified.
10. ZIP extraction smoke exits 0.
11. ZIP does not contain `.git`, `tests/`, `release-candidates/`, provider keys, or build cache.
12. All known limitations are reviewed and accepted.
13. No open blocker issues remain.

---

## Fail Criteria (Blockers)

Any of the following causes a NO-GO decision:

- `python -m unittest` exits non-zero (any test failure).
- `--headless-smoke` exits non-zero.
- Any required CLI command exits non-zero.
- PyInstaller build fails.
- Portable folder smoke exits non-zero.
- ZIP checksum does not match.
- ZIP extraction smoke exits non-zero.
- ZIP contains a provider API key or credential.
- ZIP contains `.git/` directory.
- A crash or unhandled exception is observed during any manual smoke step.

---

## Manual QA Procedure

1. Check out or update the repository to the tagged commit.
2. Run `python -m unittest` from repository root.
3. Run `--headless-smoke` and verify JSON output.
4. Run all CLI smoke commands in order.
5. On a machine with display: launch `python -m aurora_studio.ui.desktop_shell` and perform manual UI smoke (see regression checklist).
6. Record results in the go/no-go report.

---

## Regression Procedure

Follow `docs/qa/V0_1_REGRESSION_CHECKLIST.md` in order.
Tick each checkbox as PASS.
Mark any failure as FAIL and open a blocker.

---

## Packaging Validation Procedure

Follow `docs/qa/V0_1_PACKAGING_VALIDATION_CHECKLIST.md` in order.
Run each packaging command.
Inspect each artifact.
Tick each checkbox as PASS or FAIL.

---

## Go/No-Go Procedure

1. Complete regression checklist.
2. Complete packaging validation checklist.
3. Review known limitations list.
4. Fill in `docs/qa/V0_1_GO_NO_GO_REPORT_TEMPLATE.md`.
5. If any blocker is open: decision is NO-GO.
6. If no blockers and all pass criteria are met: decision is GO or GO WITH KNOWN LIMITATIONS.
7. Record decision and sign off.

---

## Known Limitations Review

Before making a GO decision, all items in the known limitations list must be
explicitly reviewed and accepted:

```text
[ ] No installer (portable folder only)
[ ] No code signing (SmartScreen warning expected)
[ ] No database (in-memory state only)
[ ] No provider integration (no AI model calls)
[ ] No plugin execution (metadata only)
[ ] No real AFL semantic validation (structural only)
[ ] No real prompt generation
[ ] Not production ready
```

---

## Evidence Collection

The QA reviewer must collect and record:

```text
- unittest output (pass count, test result)
- headless-smoke JSON output
- CLI smoke outputs
- PyInstaller build output (success/failure, output size)
- portable folder directory listing
- ZIP file size and SHA-256 hash
- ZIP extraction directory listing
- Manual UI smoke notes
- Antivirus scan result if available
- Any observed anomalies
```

Evidence must be retained until a final release decision is made.
