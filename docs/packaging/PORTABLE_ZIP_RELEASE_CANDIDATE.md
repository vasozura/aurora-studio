# Portable ZIP Release Candidate

Document ID: PORTABLE_ZIP_RELEASE_CANDIDATE
Version: 0.1.0
Status: Release candidate process — not a final release
Task: TASK-000048

---

## Purpose

Document the controlled process for creating and validating a portable ZIP
release candidate for Aurora Studio.

This is a release candidate packaging process. It creates a ZIP artifact that
can be inspected and validated before a final release decision.

This does not create a final release.
This does not create an installer.
This does not create MSIX.
This does not code-sign binaries.
This does not enable provider integration.
This does not enable plugin execution.
ZIP output is disposable and can be regenerated at any time.

---

## Prerequisites

1. Python 3.11+ and PyInstaller installed on the build machine:

```bash
python -m pip install -r build\requirements-build.txt
```

2. One-folder app built:

```bat
scripts\build_windows_onefolder.bat
```

3. Portable folder staged:

```bat
scripts\stage_windows_portable.bat
```

4. Portable folder smoke verified (recommended before creating ZIP):

```bat
scripts\smoke_portable_folder.bat
```

---

## Build One-Folder App

```bat
scripts\build_windows_onefolder.bat
```

PowerShell:

```powershell
.\scripts\build_windows_onefolder.ps1
```

Output: `dist\AuroraStudio\AuroraStudio.exe`

---

## Stage Portable Folder

```bat
scripts\stage_windows_portable.bat
```

PowerShell:

```powershell
.\scripts\stage_windows_portable.ps1
```

Output: `dist-portable\AuroraStudio-v0.1.0-windows-portable\`

---

## Smoke Portable Folder

```bat
scripts\smoke_portable_folder.bat
```

PowerShell:

```powershell
.\scripts\smoke_portable_folder.ps1
```

Expected: exits 0. No window opens.

---

## Create Release Candidate ZIP

```bat
scripts\create_portable_zip.bat
```

PowerShell:

```powershell
.\scripts\create_portable_zip.ps1
```

Output:

```text
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

The ZIP contains the staged portable folder as its top-level directory:

```text
AuroraStudio-v0.1.0-windows-portable/
```

---

## Verify Checksum

The SHA-256 checksum file is created alongside the ZIP:

```text
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

Contents:

```text
<sha256hash>  AuroraStudio-v0.1.0-rc1-windows-portable.zip
```

The smoke script verifies the checksum before extraction. To verify manually:

```powershell
$hash = (Get-FileHash "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip" -Algorithm SHA256).Hash.ToLower()
$stored = (Get-Content "release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256").Split(" ")[0]
$hash -eq $stored
```

---

## Smoke ZIP Extraction

```bat
scripts\smoke_portable_zip.bat
```

PowerShell:

```powershell
.\scripts\smoke_portable_zip.ps1
```

The smoke script:

1. Verifies ZIP exists.
2. Verifies checksum file exists.
3. Verifies checksum matches ZIP.
4. Extracts ZIP to `release-candidates\_smoke\`.
5. Verifies extracted top-level folder is `AuroraStudio-v0.1.0-windows-portable`.
6. Verifies `app/`, `run_desktop.bat`, `smoke_desktop.bat`, `README.txt`, `NOTICE.txt`, `data/`, `logs/`, `samples/`, `tmp/` exist.
7. Runs `smoke_desktop.bat` from extracted folder (`--headless-smoke`).
8. Cleans up the smoke extraction folder.
9. Exits 0 on success.

No window opens during ZIP smoke.

---

## Expected Artifacts

```text
release-candidates/
  AuroraStudio-v0.1.0-rc1-windows-portable.zip
  AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

The `release-candidates/` directory is listed in `.gitignore` and must not be
committed to the repository.

---

## What Is Included

- PyInstaller one-folder app bundle (`app/AuroraStudio/`)
- Desktop shell launcher (`run_desktop.bat`)
- Headless smoke script (`smoke_desktop.bat`)
- User instructions (`README.txt`)
- Build notices (`NOTICE.txt`)
- Empty writable directories (`data/`, `logs/`, `samples/`, `tmp/`)

---

## What Is Not Included

- No installer (NSIS, WiX, MSIX)
- No code signing
- No provider API keys
- No plugin code or plugin execution
- No database engine
- No repository source files
- No `.git` directory
- No build cache
- No test files
- No auto-update mechanism

---

## Cleanup Behavior

The ZIP creation script removes only:

```text
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip
release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256
```

The smoke script removes its temporary extraction folder:

```text
release-candidates\_smoke\
```

To fully clean all release candidate output:

```bat
rmdir /s /q release-candidates
```

PowerShell:

```powershell
Remove-Item -Recurse -Force release-candidates
```

---

## Troubleshooting

**Staged folder not found:**

```text
ERROR: Staged portable folder not found
```

→ Run: `scripts\stage_windows_portable.bat`

**ZIP creation fails:**

→ Ensure PowerShell is available and the staged folder is not locked.
→ Close any running `AuroraStudio.exe` instances before creating ZIP.

**Checksum mismatch:**

→ ZIP may have been modified or corrupted after creation.
→ Re-run `scripts\create_portable_zip.bat` to regenerate ZIP and checksum.

**Extracted folder layout check fails:**

→ Re-run `scripts\stage_windows_portable.bat` to rebuild the staged folder.
→ Re-run `scripts\create_portable_zip.bat` to rebuild the ZIP.

**ZIP headless smoke exits non-zero:**

→ Check `scripts\smoke_portable_folder.bat` first (staged folder smoke).
→ If staged smoke also fails, rebuild from `scripts\build_windows_onefolder.bat`.

---

## Future Final Release Task

This task creates a release candidate ZIP only.

A later task will:

1. Run final validation on the RC ZIP.
2. Apply code signing if approved.
3. Rename to final release artifact.
4. Create GitHub release or equivalent distribution channel.
5. Publish release notes.

No final release is created by TASK-000048.
