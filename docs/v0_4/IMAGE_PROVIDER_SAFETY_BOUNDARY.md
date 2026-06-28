# Image Provider Safety Boundary — v0.4

## Purpose

This document defines the safety boundary for image provider integration in Aurora Studio v0.4.
It describes what is permitted, what is explicitly forbidden, and how the execution gate enforces these boundaries.

## Current Provider Behavior

In v0.4, all image provider execution paths are in planning/bridge mode only:

- Mock image execution is available locally with no network call.
- Real image provider execution is blocked by default.
- No image files are generated.
- No assets are uploaded.

## v0.4 Image Readiness Scope

TASK-000111-115 introduces:

- Image provider contracts (request/response shapes)
- Local mock image adapter (deterministic, no network)
- Image prompt export bridge (connects prompt export to mock adapter)
- Image provider execution gate
- Safety QA docs and tests

## Non-Goals

TASK-000111-115 does **not** implement:

- Real image provider API calls
- Image generation
- Image editing
- Image upload
- Reference image upload
- Mask upload
- Thumbnail generation
- Media decoding
- Provider model discovery
- Cost estimation
- Rate limit management
- Persistent secret storage

## Explicit Safety Statements

```
TASK-000111-115 does not perform real image provider API calls.
TASK-000111-115 does not generate images.
TASK-000111-115 does not upload files or assets.
TASK-000111-115 does not decode or process local media.
TASK-000111-115 does not add provider SDKs.
TASK-000111-115 does not persist real API keys.
TASK-000111-115 does not store secrets in project JSON.
TASK-000111-115 does not log secrets.
TASK-000111-115 does not bundle secrets.
Real image provider execution is blocked until a later task explicitly implements a real image provider adapter.
```

## Real Image Execution Prerequisites

Before any real image provider execution may proceed, ALL of the following must be satisfied:

1. provider_registered — Provider must be registered in the provider registry
2. provider_enabled — Provider must be enabled in provider config
3. real_image_execution_requested — Real execution explicitly requested by the caller
4. real_image_execution_allowed — Gate config must allow real image execution
5. secret_reference_available — A secret reference must be available (not the actual value)
6. secret_storage_approved — Secret storage approach approved for this provider
7. prompt_only_request — Request must be prompt-only (no reference image upload)
8. no_reference_image_upload — No reference image, mask, or asset may be uploaded
9. redaction_enabled — Log redaction must be enabled
10. logging_sanitized — Logging must sanitize secrets and prompt data
11. network_allowed_for_provider — Network access allowed for this provider
12. user_confirmed — User must have explicitly confirmed real image execution
13. no_pii_in_prompt_confirmed — User must confirm no PII in prompt text

In v0.4, the gate always returns blocked for real image execution.

## Image Data Exposure Boundary

- No image bytes may be stored in contracts, run history, logs, or export artifacts.
- No base64-encoded image data may appear in any JSON payload.
- Mock image URIs use the safe `mock://image/<id>` scheme.
- No real image URL from an external provider may be stored persistently.

## Asset Upload Boundary

No upload of any kind is permitted in v0.4:

- No reference image upload
- No mask upload
- No style transfer image upload
- No control image upload
- No face image upload
- No asset binary transfer

## Secret Handling Boundary

- Secrets are never stored on adapter instances.
- Secrets are never written to project JSON, autosave files, backup files, logs, run history, export artifacts, release artifacts, or portable bundles.
- Ephemeral call-time secret model only (for future real image execution).
- Secrets must be redacted from all error messages and log entries.

## Logging / Redaction Boundary

- Prompt text logged only as a sanitized/truncated preview.
- No full prompt text in logs.
- No secret values in logs.
- Mock image URIs are safe to log.

## Network Boundary

- No network calls in mock execution paths.
- No network calls in automated tests.
- Real HTTP only possible via `urllib.request` (stdlib) after gate approval (blocked in v0.4).

## Provider Adapter Boundary

- No provider SDK imports (`openai`, `anthropic`, `stability`, `replicate`, `runway`, etc.)
- No `requests`, `httpx`, or `aiohttp`
- No `PIL`, `cv2`, or `moviepy`
- Real execution base class always returns blocked

## Desktop UI Boundary

- No real image execution button in UI
- UI may display mock image URI and execution mode
- UI must display "Mock only — no image is generated"

## CLI Boundary

- `image-provider-mock` command: no network, no image file created
- `image-provider-readiness` command: reports prerequisites only, never executes
- No `--secret` or `--api-key` CLI argument (shell history risk)

## Packaging Boundary

- No image files in release artifacts
- No provider secrets in portable bundles
- No SDK dependencies added to `pyproject.toml`

## Testing Boundary

- All automated tests use mock mode only
- No real network calls in test suite
- No image files created in test suite
- Source scan verifies no forbidden imports

## Future Implementation Tasks

Real image provider execution will require a dedicated future task that must:

1. Implement a specific provider adapter (not in TASK-000111-115)
2. Pass an explicit gate (new task)
3. Pass a new security review
4. Add new real-execution tests with monkeypatched HTTP

## Acceptance Criteria

- Safety boundary doc exists and states all required safety commitments
- Escalation rules doc exists
- Gate blocks real image execution by default
- Gate allows mock image execution
- UISession exposes gate evaluation and prerequisite listing
- All tests pass

---

*Last updated: v0.4 — TASK-000111*
