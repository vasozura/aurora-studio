# v0.3 Architecture Boundary — Aurora Studio

## Purpose

This document defines the architecture boundary for Aurora Studio v0.3.
It specifies what v0.3 may and may not implement.
It is the authoritative boundary reference for all TASK-000076-080 work.

## v0.3 Scope

v0.3 may include:

- Provider registry (local metadata only)
- Provider metadata and capabilities (strings, not SDK objects)
- Local dry-run provider adapter (no network, no SDK)
- Provider request/response object model (dataclasses only)
- Sanitized provider request/response logs (no secrets)
- Provider UI metadata (list, status, type display)
- Provider config status tracking (non-secret metadata only)
- Provider QA checks (dry-run, validation, boundary tests)

## v0.3 Non-goals

v0.3 does not include:

- Real provider API calls
- Provider SDKs
- Real API key storage
- Cloud sync
- Database
- Plugin execution
- Arbitrary code execution
- Background jobs
- Web server
- Production readiness claim

## Provider Foundation Boundary

The provider foundation layer in v0.3 is:

- A local registry mapping provider IDs to metadata.
- A dry-run adapter that echoes sanitized prompt summaries.
- A log manager that records request/response metadata without secrets.
- No import of provider SDKs is allowed.
- No network call is permitted.
- No file or media generation is performed.

## Prompt Execution Boundary

In v0.3:

- Prompt rendering is local string substitution (unchanged from v0.2).
- Dry-run execution echoes the prompt without sending it anywhere.
- Real prompt execution to external providers is reserved for a later task.
- No execution queue, retry, or scheduling is implemented.

## Plugin Sandbox Boundary

In v0.3:

- Plugin metadata remains metadata-only (unchanged from v0.2).
- No plugin code is loaded or executed.
- Plugin capabilities are not extended in this pack.
- Plugin sandbox implementation is reserved for a later task.

## Secret Handling Boundary

In v0.3:

- No real API keys are stored.
- No secret values appear in source code.
- No secret values appear in JSON bundles.
- No secret values appear in logs.
- No secret values appear in portable ZIPs or release artifacts.
- Config status metadata (e.g. "not_configured") is allowed.
- Config status must not contain secret values.

## Logging Boundary

In v0.3:

- Logs record request/response metadata only.
- Prompt previews are truncated and sanitized.
- Output previews are truncated and sanitized.
- Secret-like field names (api_key, token, secret, password) are never stored in logs.
- Logs are transient in-memory by default.

## Desktop UI Boundary

In v0.3:

- A minimal provider tab or section is added.
- Provider list, status, enable/disable controls are allowed.
- Dry-run prompt input and result display are allowed.
- No real Execute Provider button that calls an external API.
- No API key input field in this pack.
- No network action is triggered from the UI.

## Persistence Boundary

In v0.3:

- Provider registry state is transient (in-memory only).
- Provider config status is transient (in-memory only).
- Provider logs are transient (in-memory only).
- No secrets are added to the project bundle.
- Existing bundle save/load must not be broken.

## Packaging Boundary

In v0.3:

- No provider SDK is bundled.
- No API key is bundled.
- No secret is included in any release artifact.
- Packaging scripts are not modified in this pack.

## Testing Boundary

In v0.3:

- All tests use standard library only.
- No live network call occurs in any test.
- No provider SDK import is required.
- Dry-run tests are deterministic.
- No test skips to hide provider execution behavior.

## Future Escalation Rules

The following require a future task before implementation:

- Real provider API call → requires TASK-PROVIDER-REAL-001 or equivalent.
- Real API key storage → requires TASK-APIKEY-001 or equivalent.
- Provider SDK import → requires explicit approval task.
- Plugin execution → requires TASK-PLUGIN-SANDBOX-001 or equivalent.
- Database integration → requires explicit architecture task.
- Background execution queue → requires explicit concurrency task.

No escalation is permitted in TASK-000076-080.
