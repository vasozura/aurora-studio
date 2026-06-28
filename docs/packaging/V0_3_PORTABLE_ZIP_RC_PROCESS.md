# Aurora Studio v0.3 Portable ZIP RC Process

## Purpose

Document the release candidate ZIP creation process for Aurora Studio v0.3.0.
This task creates release candidate process only.
This task does not approve final release.
This task does not sign code.
This task does not create installer/MSIX.

---

## Prerequisites

- Windows 10/11 x64
- Python 3.11+
- PyInstaller installed
- PowerShell 5.1+
- Staged portable folder at `.\dist\AuroraStudio-portable`

---

## Build One-Folder

```powershell
.\scripts\build_windows_onefolder.ps1
```

---

## Stage Portable Folder

```powershell
.\scripts\stage_windows_portable.ps1
```

---

## Create RC ZIP

```powershell
.\scripts\create_v0_3_portable_zip_rc.ps1
```

Output: `release-candidates\AuroraStudio-v0.3.0-rc1-windows-portable.zip`

---

## Verify SHA256

```powershell
Get-Content release-candidates\AuroraStudio-v0.3.0-rc1-windows-portable.zip.sha256
```

---

## Smoke RC ZIP

```powershell
.\scripts\smoke_v0_3_portable_zip_rc.ps1
```

---

## Expected Artifacts

```
release-candidates/AuroraStudio-v0.3.0-rc1-windows-portable.zip
release-candidates/AuroraStudio-v0.3.0-rc1-windows-portable.zip.sha256
```

Final artifact names (only after GO decision):
```
releases/AuroraStudio-v0.3.0-windows-portable.zip
releases/AuroraStudio-v0.3.0-windows-portable.zip.sha256
```

---

## Excluded Files

- .env files
- Secrets or API key files
- __pycache__ directories
- .pytest_cache directories
- Provider SDK packages

---

## Known Limitations

- Windows-only scripts.
- No automated CI/CD — manual trigger required.
- No installer or code signing in this task.

---

## No-Final-Release Rule

This task creates the release candidate process only.
A final release requires explicit GO decision from TASK-000100.
Default decision is PENDING until evidence and user instruction allow change.
