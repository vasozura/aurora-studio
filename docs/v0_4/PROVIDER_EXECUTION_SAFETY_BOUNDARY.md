# Provider Execution Safety Boundary — Aurora Studio v0.4

## Purpose

This document defines the execution safety boundary for all provider-related work in v0.4.
It governs what may and may not occur during TASK-000101 through TASK-000105.

## Current Provider Behavior

Aurora Studio v0.3 provides:
- A provider registry with in-memory ProviderDefinition records.
- A dry-run provider ("dry-run-local") that returns synthetic responses without network access.
- Provider log, error handling, and prompt run history — all in-memory, standard library only.
- No provider SDK. No network call. No real API key storage.

## v0.4 Readiness Scope

TASK-000101 through TASK-000105 extend the provider layer with:
- A provider execution gate that blocks real execution by default.
- A user API key entry boundary with redaction utilities.
- Secret storage strategy documentation (planning only).
- Provider config UI hardening (metadata only, no secret storage).
- Provider test connection — dry/mock only, no network.

## Non-Goals

TASK-000101-105 does NOT:
- Implement any real provider adapter.
- Add any provider SDK (OpenAI, Anthropic, Google, or other).
- Make any network call.
- Persist any real API key.
- Store any secret in project JSON, autosave files, backup files, or portable ZIP.
- Log any secret value.
- Enable real provider execution.
- Add a database, background worker, or media generation pipeline.

## Real Execution Prerequisites

Before any future real provider adapter may be implemented, the following must be true:
1. OS keyring integration is implemented and tested (deferred to TASK-000106+).
2. User has explicitly opted in to real execution via a dedicated UI action.
3. A provider adapter for the target provider exists and has passed adapter tests.
4. A real API key is available via OS keyring — never from project JSON.
5. The provider execution gate has been opened for the specific provider by a future explicit gate-open mechanism.
6. Redaction is applied to all logs and output before persistence.
7. A consent/confirmation flow has been shown to the user.

## Execution Gate Model

A `ProviderExecutionGate` module is implemented in v0.4 with the following contract:

- `is_real_execution_allowed(provider_id)` returns `False` for all providers in v0.4.
- `evaluate_execution(provider_id, requested_action, config=None)` returns a `ProviderExecutionGateDecision`.
- `block_real_execution(provider_id, requested_action, reason="")` returns a blocked decision.
- The gate may not be opened from within TASK-000101-105.

## User Consent Boundary

- No UI in v0.4 may display a button that triggers real provider execution.
- No UI in v0.4 may imply that real execution is available.
- Future real execution must be preceded by an explicit user opt-in dialog.
- The consent state must be tracked separately from provider config metadata.

## Secret Handling Boundary

- No real API key may be written to any file in v0.4.
- API key entry UI (if any) must display only redacted previews.
- `ProviderKeyEntryState.to_dict()` must never include the real key value.
- `sanitize_provider_config_payload()` must strip all key-like fields from any dict before persistence.

## Logging / Redaction Boundary

- Provider logs must never contain raw API key values.
- `redact_secret()` and `sanitize_text_for_secrets()` utilities are provided in v0.4.
- Log entries must pass through redaction before being stored in run history.
- Prompt text must never be sent to an external service in v0.4.

## Network Boundary

- TASK-000101-105 does not perform real provider API calls.
- No `socket`, `urllib`, `http.client`, `requests`, `httpx`, or `aiohttp` usage.
- Test connection in v0.4 is dry/mock only.

## Provider Adapter Boundary

- No real provider adapter exists in v0.4.
- `provider_registry.py` registers the dry-run provider only.
- Future adapters (OpenAI, Anthropic, etc.) are deferred to TASK-000106+.

## Desktop UI Boundary

- Provider tab may show: execution gate status (Blocked), dry-run status, config metadata.
- Provider tab must NOT show: a real "Connect" or "Execute" button.
- API key entry UI (if shown) must display only placeholder/redacted state.

## CLI Boundary

- `cli smoke` and `cli provider-smoke` continue to pass in v0.4.
- `cli provider-test` (new in v0.4) operates in dry/mock mode only.
- No CLI command in v0.4 accepts or uses a real API key.

## Packaging Boundary

- Portable ZIP produced by packaging scripts must not bundle any secret.
- Release notes must not contain any API key.
- Packaging scripts from v0.3 remain unchanged unless test inspection compatibility requires it.

## Testing Boundary

- All tests in TASK-000101-105 use standard library only.
- No test makes a network call.
- No test stores a real secret.
- Mock/dry-run test connection uses local deterministic logic only.

## Future Implementation Tasks

The following are deferred to TASK-000106 or later:
- Real OpenAI provider adapter
- Real Anthropic provider adapter
- Real image/video provider adapter
- OS keyring integration
- Actual secret persistence
- Real test connection with network
- Rate limiting and cost estimation
- Production provider runtime

## Acceptance Criteria

- `is_real_execution_allowed(provider_id)` returns `False` for all providers.
- No provider SDK import exists anywhere in `src/`.
- No network call occurs during `python -m unittest`.
- No secret is written to any file.
- All TASK-000101-105 tests pass.
- Headless smoke and CLI smoke pass.

---

Explicit boundary statement:

TASK-000101-105 does not perform real provider API calls.
TASK-000101-105 does not add provider SDKs.
TASK-000101-105 does not persist real API keys.
TASK-000101-105 does not store secrets in project JSON.
TASK-000101-105 does not log secrets.
TASK-000101-105 does not bundle secrets.
Real provider execution is blocked until a later task explicitly implements a provider adapter.
