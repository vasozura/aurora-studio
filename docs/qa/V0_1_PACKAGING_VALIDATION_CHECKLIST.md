# v0.1 Packaging Validation Checklist

Document ID: V0_1_PACKAGING_VALIDATION_CHECKLIST
Version: 0.1.0
Status: QA checklist — fill in during QA review
Task: TASK-000049

Instructions: Tick each checkbox as PASS during QA review.
Mark any failure as FAIL and open a blocker.

---

## Build Prerequisites

- [ ] Python 3.11+ is installed on the build machine (64-bit CPython).
- [ ] `python --version` confirms 3.11 or later.
- [ ] `pip install -r build\requirements-build.txt` succeeds.
- [ ] `python -m PyInstaller --version` confirms PyInstaller is available.
- [ ] tkinter is available: `python -c "import tkinter"` exits 0.

---

## One-Folder Build

- [ ] `scripts\build_windows_onefolder.bat` exits 0.
- [ ] `dist\AuroraStudio\` exists after build.
- [ ] `dist\AuroraStudio\AuroraStudio.exe` exists.
- [ ] `dist\AuroraStudio\_internal\` exists (PyInstaller runtime).
- [ ] Build does not print unexpected errors.
- [ ] Build does not install packages other than those in `requirements-build.txt`.

---

## Built App Smoke

- [ ] `dist\AuroraStudio\AuroraStudio.exe --headless-smoke` exits 0.
- [ ] Output is valid JSON.
- [ ] JSON contains `"ok": true`.
- [ ] `scripts\smoke_built_app.bat` exits 0.
- [ ] No provider API key appears in output.
- [ ] No plugin code is executed during smoke.

---

## Portable Folder Staging

- [ ] `scripts\stage_windows_portable.bat` exits 0.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\` is created.
- [ ] Staging cleans previous output before re-creating.
- [ ] Staging does not create a ZIP file.
- [ ] Staging does not install packages.
- [ ] Staging does not require admin rights.

---

## Portable Folder Contents

- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\app\AuroraStudio\AuroraStudio.exe` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\app\AuroraStudio\_internal\` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\run_desktop.bat` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\smoke_desktop.bat` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\README.txt` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\NOTICE.txt` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\data\` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\logs\` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\samples\` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\tmp\` exists.

---

## Portable Folder Smoke

- [ ] `scripts\smoke_portable_folder.bat` exits 0.
- [ ] `smoke_desktop.bat` inside portable folder exits 0.
- [ ] No window opens during portable folder smoke.
- [ ] No provider API is called.
- [ ] No plugin code is executed.

---

## Release Candidate ZIP

- [ ] `scripts\create_portable_zip.bat` exits 0.
- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip` exists.
- [ ] ZIP file size is reasonable (note actual size in report).
- [ ] ZIP filename matches naming convention: `AuroraStudio-v{VERSION}-{RC_TAG}-windows-portable.zip`.
- [ ] ZIP creation does not create an installer.
- [ ] ZIP creation does not create MSIX.
- [ ] No installer is created.
- [ ] No MSIX is created.
- [ ] No code signing is attempted.
- [ ] No provider integration is enabled.
- [ ] No plugin execution is enabled.

---

## Checksum

- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256` exists.
- [ ] SHA-256 file contains exactly one line: `<hash>  AuroraStudio-v0.1.0-rc1-windows-portable.zip`.
- [ ] Checksum is computed after ZIP creation (not before).
- [ ] Checksum verification command succeeds:
  ```powershell
  $h = (Get-FileHash "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip" -Algorithm SHA256).Hash.ToLower()
  $s = (Get-Content "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256").Split(" ")[0]
  $h -eq $s
  ```
  Expected: `True`

---

## ZIP Extraction Smoke

- [ ] `scripts\smoke_portable_zip.bat` exits 0.
- [ ] ZIP extracts without errors.
- [ ] Extracted top-level folder is `AuroraStudio-v0.1.0-windows-portable`.
- [ ] All required items exist in extracted folder:
  - [ ] `app\`
  - [ ] `run_desktop.bat`
  - [ ] `smoke_desktop.bat`
  - [ ] `README.txt`
  - [ ] `NOTICE.txt`
  - [ ] `data\`
  - [ ] `logs\`
  - [ ] `samples\`
  - [ ] `tmp\`
- [ ] `smoke_desktop.bat` inside extracted folder exits 0.
- [ ] Smoke extraction folder is cleaned up after smoke.

---

## Artifact Naming

- [ ] ZIP name is exactly `AuroraStudio-v0.1.0-rc1-windows-portable.zip`.
- [ ] SHA-256 name is exactly `AuroraStudio-v0.1.0-rc1-windows-portable.sha256`.
- [ ] Top-level folder inside ZIP is exactly `AuroraStudio-v0.1.0-windows-portable`.
- [ ] EXE inside portable folder is `AuroraStudio.exe`.

---

## Artifact Exclusions

The ZIP must NOT contain any of the following:

- [ ] No `.git\` directory.
- [ ] No `tests\` directory.
- [ ] No `src\` directory (Python source).
- [ ] No `release-candidates\` directory nested inside ZIP.
- [ ] No `build\` directory (build cache).
- [ ] No `dist-portable\` directory nested inside ZIP.
- [ ] No `pyproject.toml`.
- [ ] No `*.py` Python source files.
- [ ] No `build\pyinstaller_work\` contents.

---

## Security-Sensitive Exclusions

The ZIP must NOT contain:

- [ ] No OpenAI API key or credential of any kind.
- [ ] No Anthropic API key or credential.
- [ ] No RunwayML API key or credential.
- [ ] No ElevenLabs API key or credential.
- [ ] No `.env` file.
- [ ] No file matching `*_key*`, `*secret*`, `*.pem`, `*.p12`.
- [ ] No user project folder data (except intentional empty `samples/`).
- [ ] No database file (SQLite, Postgres dump, etc.).

---

## Known Limitations

- [ ] Reviewer confirms: no installer is included or created.
- [ ] Reviewer confirms: no MSIX is included or created.
- [ ] Reviewer confirms: no code signing is applied.
- [ ] Reviewer confirms: SmartScreen warning is expected on first launch.
- [ ] Reviewer confirms: antivirus false positives are possible and documented.
- [ ] Reviewer confirms: tkinter must be present in the build Python (not embeddable zip).
- [ ] Reviewer confirms: no provider API keys are bundled.
- [ ] Reviewer confirms: no plugin code is executed at runtime.
- [ ] Reviewer confirms: this is a smoke build, not a production release.
