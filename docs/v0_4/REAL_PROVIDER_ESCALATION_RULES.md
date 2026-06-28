# Real Provider Escalation Rules — Aurora Studio v0.4

## Purpose

This document defines the rules that must be satisfied before any real provider adapter
may be implemented, enabled, or executed in Aurora Studio.

## What Counts as Real Provider Execution

Real provider execution is defined as any of the following:
- A network call to a provider endpoint (OpenAI, Anthropic, Google, or other).
- A provider SDK invocation (openai, anthropic, google-generativeai, or similar).
- Sending prompt text outside the local machine.
- Sending image, video, or audio data outside the local machine.
- Using a real API key to authenticate with an external service.
- Receiving a provider response from an external service.

Any of the above constitutes real provider execution and is blocked in v0.4.

## Required User Configuration

Before real execution may be enabled for a provider:
1. The user must have explicitly configured the provider via the provider config UI.
2. The user must have entered an API key via the OS keyring flow (not project JSON).
3. The user must have confirmed understanding that real calls will be made.
4. The provider must be in state `available` (not `not_configured` or `disabled`).

## Required Secret Storage Decision

Before real execution may be enabled:
1. OS keyring integration must be implemented and tested.
2. The keyring backend for the user's OS must be verified (Windows Credential Manager / macOS Keychain / Linux Secret Service).
3. A no-keyring fallback policy must be documented and implemented.
4. The user must have consented to secret storage via the OS keyring.

## Required Redaction

All logging of provider interactions must pass through redaction:
- `redact_secret()` must be applied to any value that looks like an API key.
- `sanitize_provider_config_payload()` must strip key-like fields from all persisted dicts.
- `sanitize_text_for_secrets()` must be applied to any log text that may contain secrets.
- No secret may appear in run history, provider logs, project bundle, autosave, or backup files.

## Required Provider Adapter Tests

Each real provider adapter must have:
- Unit tests with mocked network responses (no real network in CI).
- An adapter contract test verifying that the adapter returns a `ProviderResponse`.
- A test verifying that the adapter never logs raw API key values.
- A test verifying that the adapter fails gracefully if the API key is missing.

## Required Mock Tests

Before a real adapter is accepted:
- A mock test connection must pass deterministically without network.
- The mock must be distinct from the dry-run provider.
- The mock must verify that the adapter interface is correct.

## Required Opt-In UI

Before real execution may be triggered from the UI:
- A dedicated "Enable Real Execution" flow must be implemented.
- The flow must display a warning dialog explaining that real API calls will be made.
- The user must actively confirm the action.
- The UI must not display a real execute button unless the gate is explicitly open.

## Required CLI Safeguards

Before real execution may be triggered from the CLI:
- A `--confirm-real-execution` flag or equivalent must be required.
- The CLI must not proceed without explicit confirmation.
- The CLI must log a warning that a real API call is about to be made.

## Required Packaging Safeguards

Before a release with real provider support:
- The portable ZIP must be verified to contain no secrets.
- The release notes must not reference any API key.
- Packaging scripts must include a secret-scan step.

## Blocked-by-Default Rule

Until all conditions above are satisfied, the provider execution gate returns:

```
allowed = False
reason = "Real provider execution is blocked in v0.4. Prerequisites not met."
```

This is enforced by `ProviderExecutionGate.is_real_execution_allowed(provider_id)` returning False.

## Go/No-Go for Real Adapter Implementation

A real provider adapter may be implemented only when:
1. This escalation rules document has been reviewed.
2. OS keyring integration is complete and tested.
3. User opt-in UI is implemented.
4. Redaction utilities are in place and tested.
5. The provider execution gate has a documented mechanism to open it for specific providers.
6. All existing tests continue to pass.
7. A dedicated task (TASK-000106+) explicitly authorizes the implementation.
