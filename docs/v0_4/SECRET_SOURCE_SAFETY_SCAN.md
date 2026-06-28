# v0.4 Secret / Source Safety Scan

**Version**: 0.4.0
**Status**: Documented

---

## Purpose

This document describes the v0.4 source and packaging safety scanner for Aurora Studio.
The scanner verifies that the source tree does not contain forbidden SDK imports, unsafe
network/media calls, or secret-like artifact risks.

---

## Scanner Module

`src/aurora_studio/modules/safety_scan.py`

---

## Scan Functions

| Function | Description |
|---|---|
| `scan_text_for_secret_fields(text, path)` | Detect secret-like field assignments in arbitrary text |
| `scan_source_for_forbidden_imports(root_path)` | Detect forbidden SDK imports in `src/aurora_studio/**/*.py` |
| `scan_source_for_forbidden_network_usage(root_path)` | Detect forbidden network library usage |
| `scan_source_for_forbidden_media_usage(root_path)` | Detect ffmpeg/subprocess in image/video modules |
| `scan_packaging_for_secret_risks(root_path)` | Detect secret keywords in packaging scripts/templates |
| `run_v0_4_safety_scan(root_path)` | Run all scans, return combined JSON result |

---

## Source Scan Scope

All scans target: `src/aurora_studio/**/*.py`

---

## Forbidden Imports

The following imports are forbidden in all source files:

- `import openai` / `from openai`
- `import anthropic` / `from anthropic`
- `import requests`
- `import httpx`
- `import aiohttp`
- `import PIL` / `from PIL`
- `import cv2`
- `import moviepy` / `from moviepy`

Allowed: `urllib`, `urllib.request`, `urllib.error` (for gated text adapter work).

---

## Media / Subprocess Scan

For image and video provider modules, the following are also forbidden:

- `import ffmpeg`
- `import ffprobe`
- `import subprocess`
- `subprocess.run(`
- `subprocess.Popen(`
- `os.system(`

---

## Secret-Like Fields

The following field names are flagged when they appear in text payloads or serialized data:

- `api_key`, `apikey`, `token`, `secret`, `password`
- `authorization`, `auth_header`, `bearer`, `private_key`
- `access_token`, `refresh_token`, `client_secret`

Redaction utility *definitions* (which name these fields) are flagged as WARN, not ERROR.

---

## Packaging Scan

Scripts and templates under `scripts/` are scanned for: `.env`, `*.env`, `api_key`, `secret`, `token`, `password`.

If the keyword appears inside an exclusion check or comment, the result is WARN (not ERROR).

---

## Scan Result Format

All scan functions return JSON-serializable dicts with:
- `status`: `"PASS"` or `"FAIL"`
- `errors`: count of hard errors
- `warnings`: count of advisory warnings
- `findings`: list of finding dicts

---

## Docs Not Scanned for Errors

Documentation files (`.md`, `.txt`) are not scanned as source failures even if they mention
forbidden words as warnings or documentation examples.

---

## CLI

If implemented: `python -m aurora_studio.cli safety-scan`

Output: JSON only (one object on stdout).

---

*Aurora Studio v0.4 — TASK-000122*
