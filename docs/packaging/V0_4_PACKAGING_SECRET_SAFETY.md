# v0.4 Packaging Secret Safety

**Version**: 0.4.0
**Status**: Documented

---

## Purpose

Ensure that v0.4 portable artifacts explicitly exclude secrets, provider keys, caches, SDKs,
and unsafe development artifacts. This document describes the safety boundary and exclusion
policy for all packaging and distribution artifacts.

---

## Scope

All v0.4 portable bundles, ZIP exports, and distribution packages.

---

## Portable Artifact Boundary

A v0.4 portable artifact contains:
- Source code (`src/aurora_studio/`)
- Documentation (`docs/`)
- Tests (`tests/`)
- Scripts (`scripts/`)
- Configuration (`pyproject.toml`, `README.md`, `NOTICE`)
- Demo project data (no secrets)

---

## Excluded Files

The following must never appear in a portable artifact:

- `.env` files (`*.env`, `.env`, `.env.local`, `.env.production`)
- Provider API key files
- OS keyring exports
- Provider SDK packages (`openai/`, `anthropic/`, `requests/`, etc.)
- `__pycache__/` directories
- `.pytest_cache/` directories
- User private project data with secrets
- Backup files containing secrets

---

## Excluded Secret Patterns

The following secret patterns must not appear in release artifacts:

- `api_key = <value>` (non-empty value)
- `token = <value>` (non-empty value)
- `secret = <value>` (non-empty value)
- `password = <value>` (non-empty value)
- Bearer tokens
- Authorization headers with values
- Private keys

---

## Provider Key Policy

No API keys are bundled.
No .env files are bundled.
No provider secrets are bundled.
No user secrets are bundled.
No plugin packages are bundled for execution.
Provider real execution remains opt-in and secret-safe.

API keys are call-time only — passed by the user at execution time, not stored.

---

## Environment File Policy

`.env` files are excluded from all portable artifacts. If a `.env` file is found during
packaging, the packaging process must fail clearly.

---

## Cache Policy

`__pycache__/` and `.pytest_cache/` directories must be excluded from all portable artifacts.
These directories may contain compiled bytecode that reveals source paths.

---

## Logs Policy

Log files that may contain provider request/response data must be excluded from portable
artifacts unless explicitly reviewed and confirmed secret-free. In v0.4, logs are in-memory
and do not persist to disk by default.

---

## User Project Data Policy

User project JSON files (`aurora_project.json`, `aurora_bundle.json`) do not contain secrets
in v0.4 because secret storage is not implemented. If user project data is included in a
portable bundle for demo purposes, it must be reviewed to confirm no secrets are present.

---

## Smoke Validation

Before distributing any portable artifact, run:

```powershell
.\scripts\smoke_v0_4_portable_secret_safety.ps1 -PortablePath <path>
```

or:

```cmd
scripts\smoke_v0_4_portable_secret_safety.bat <path>
```

Both scripts check for excluded patterns and fail clearly if violations are found.

---

## Known Limitations

- Real execution secret handling is not yet implemented (no OS keyring, no encrypted storage).
- Smoke scripts check for presence of excluded files but do not scan file contents for all possible secret patterns.
- Portable ZIP creation scripts are out of scope for v0.4 — only safety validation scripts are provided.

---

*Aurora Studio v0.4 — TASK-000124*
