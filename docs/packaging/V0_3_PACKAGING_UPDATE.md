# Aurora Studio v0.3 Packaging Update

## Purpose

Document the v0.3 packaging target and flow for Aurora Studio.
This document updates prior packaging conventions for the v0.3.0 release candidate.

---

## Current Packaging Flow

1. Build one-folder distribution with PyInstaller:
   `.\scripts\build_windows_onefolder.ps1`

2. Stage portable folder:
   `.\scripts\stage_windows_portable.ps1`

3. Smoke test staged folder:
   `.\scripts\smoke_portable_folder.ps1`

4. Create portable ZIP RC:
   `.\scripts\create_v0_3_portable_zip_rc.ps1`

5. Smoke RC ZIP:
   `.\scripts\smoke_v0_3_portable_zip_rc.ps1`

---

## v0.3 Packaging Target

Artifact: `AuroraStudio-v0.3.0-rc1-windows-portable.zip`
Platform: Windows 10/11 x64

---

## Included App Components

- Aurora Studio v0.3 desktop application (Python + tkinter)
- Provider foundation (dry-run only — no SDK bundled)
- Prompt execution workflow (local only)
- Plugin sandbox foundation (metadata only, execution disabled)
- Project backup/recovery
- Explicit autosave
- Minimal undo/redo command stack
- run_desktop.bat
- smoke_desktop.bat
- README.txt
- NOTICE.txt

---

## Explicitly Excluded Components

- No provider SDKs (OpenAI, Anthropic, etc.)
- No API keys or tokens
- No bundled secrets or credentials
- No plugin execution runtime
- No database (SQLite, Postgres, etc.)
- No media preview engine (ffmpeg, Pillow, etc.)
- No background autosave worker
- No installer or MSIX
- No code signing

---

## Build Prerequisites

- Windows 10/11 x64
- Python 3.11+
- PyInstaller (project dependency)
- PowerShell 5.1+

---

## One-Folder Build Command

```powershell
.\scripts\build_windows_onefolder.ps1
```

---

## Portable Staging Command

```powershell
.\scripts\stage_windows_portable.ps1
```

---

## Portable ZIP Command

```powershell
.\scripts\create_v0_3_portable_zip_rc.ps1
```

---

## Smoke Commands

```powershell
.\scripts\smoke_portable_folder.ps1
.\scripts\smoke_v0_3_portable_zip_rc.ps1
```

---

## Known Limitations

- Windows-only packaging scripts.
- PyInstaller one-folder does not include provider SDKs — by design.
- No automated CI/CD pipeline — build must be triggered manually.
- Media preview not included — planning only in v0.3.

---

## Safety Confirmation

No provider SDKs are bundled.
No API keys are included.
No secrets are bundled.
No plugin execution runtime is included.
No database is bundled.
No media preview engine is included.
No background autosave worker is bundled.
