# Provider Adapter Plan — Aurora Studio

## Purpose

This document describes the planned provider adapter system for Aurora Studio.
Provider integration is not implemented in TASK-000068.
This document is planning only.

## Current Local-Only Export Behavior

Aurora Studio renders prompts locally using string substitution.
No external API is called.
No provider SDK is used.
Export artifacts are stored in memory as draft status.
Provider execution requires a later task.

## Non-goals

- Provider integration is not implemented in TASK-000068.
- No provider SDK is added.
- No external API is called.
- No API key is stored.
- No provider key is bundled in portable ZIP.
- Local prompt-only mode remains supported.

## Provider Interface Concept (Future)

A provider adapter interface should define:

```
send(prompt: str, params: dict) -> ProviderResponse
cancel(request_id: str) -> None
status(request_id: str) -> RequestStatus
```

Each provider implements the interface independently.
The application layer never calls provider internals directly.

## Local Prompt-Only Mode

Local prompt-only mode remains the default.
All export artifacts are created as draft locally.
No network call is made in local mode.
Local mode must always be supported regardless of provider availability.

## Image Provider Adapter (Future)

Future image providers (examples, not endorsed):

- Stable Diffusion local
- ComfyUI local
- Provider-agnostic REST adapter

Adapter receives rendered prompt and returns image reference.
Image is stored as an asset, not committed to the bundle directly.

## Video Provider Adapter (Future)

Future video providers (examples, not endorsed):

- Local inference server adapter
- Provider-agnostic REST adapter

Adapter receives scene/shot prompt and video generation parameters.
Result is stored as export artifact with provider reference.

## Text Provider Adapter (Future)

Future text providers (examples, not endorsed):

- Local model adapter
- Provider-agnostic REST adapter

Adapter receives prompt and returns generated text.
Result is stored as export artifact.

## API Key Storage Rules (Future)

- Keys are user-provided.
- Keys are never committed to version control.
- Keys are never bundled in portable ZIP.
- Keys are not written to release artifacts.
- Key storage must be explicit and revocable.
- Logs must not contain secrets.
- Keys should be stored in a user-local config file outside the project bundle.

## No Bundled Keys Rule

No API key is bundled in any release artifact.
No API key appears in source code.
No API key appears in documentation.
Violation of this rule is a blocker for any release.

## Request/Response Logging Policy (Future)

- Log provider request metadata (model, timestamp, status) without logging the full prompt.
- Never log API keys or authentication tokens.
- Log response status and error codes.
- Full prompt logging is opt-in only, with user consent.

## Error Handling (Future)

- Network errors return a friendly error message.
- Provider errors are surfaced to the user without crashing.
- Timed-out requests are cancellable.
- Failed artifacts are marked with status "failed" in the export list.

## Rate Limiting (Future)

- Implement per-provider rate limiting to avoid quota overrun.
- Implement retry with backoff for transient errors.
- Expose rate limit status in the UI.

## Safety Boundaries

- No provider call is made without explicit user action.
- No automatic provider invocation from autosave or background timer.
- No provider sends prompts to unintended endpoints.
- Provider adapter must validate the endpoint before sending.

## Packaging Implications

- Provider adapters are optional modules.
- Base package ships without any provider SDK.
- Provider SDK installation is documented separately.
- No provider-specific binary is included in the portable ZIP.

## Testing Strategy

- Unit tests for prompt rendering remain independent of provider.
- Provider adapter tests use mock/stub responses.
- No live API call in the test suite.
- Local mode must be testable without network access.

## Future Implementation Tasks

- TASK-PROVIDER-001: Define ProviderAdapter interface.
- TASK-PROVIDER-002: Implement local stub adapter for testing.
- TASK-PROVIDER-003: Implement first real provider adapter.
- TASK-PROVIDER-004: Add API key management UI.
- TASK-PROVIDER-005: Add rate limiting and retry logic.
- TASK-PROVIDER-006: Add request/response logging (opt-in).

## Acceptance Criteria (Future)

- Provider adapter interface is defined and documented.
- Local prompt-only mode remains fully functional.
- No API key appears in source, docs, or release artifacts.
- Provider errors are surfaced gracefully.
- Test suite passes with no live API calls.
