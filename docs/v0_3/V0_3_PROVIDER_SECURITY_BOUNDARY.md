# v0.3 Provider Security Boundary — Aurora Studio

## Purpose

This document defines the security boundary for all provider-related work in
Aurora Studio v0.3 (TASK-000076-080).

Violation of any rule in this document is a blocker for all tasks in this pack.

---

## No Bundled Secrets

No API key, token, password, or secret of any kind is bundled in:

- Source code
- JSON bundle files
- Release artifacts
- Portable ZIP files
- Documentation examples
- Test fixtures

If a test requires a provider key value, it must use a clearly fake placeholder such as "test-placeholder-not-a-real-key".

---

## No Real API Calls in TASK-000076-080

No real external API call is made in any code path implemented in TASK-000076-080.

This includes:

- No HTTP GET or POST to any provider endpoint
- No WebSocket connections to providers
- No gRPC calls to providers
- No SDK-mediated API calls
- No subprocess calls that invoke provider tools

All provider "execution" in this pack is dry-run only.

---

## No Provider SDKs in TASK-000076-080

No provider SDK is imported or installed in this pack.

Prohibited imports include (not exhaustive):

- openai
- anthropic
- google.generativeai
- stability_sdk
- replicate
- boto3 (for AI services)
- requests (for provider endpoints)
- httpx
- aiohttp

Standard library only. No new third-party dependencies.

---

## No Secrets in Logs

Provider log entries must not contain:

- API key values
- Token values
- Secret values
- Password values
- Bearer token values
- Any value that could authenticate a real provider request

Log entries may contain:

- Provider ID (a local identifier)
- Event type (a controlled string)
- Status (a controlled string)
- Prompt preview (truncated and sanitized)
- Output preview (truncated and sanitized)
- Error message (sanitized, no stack traces with secrets)

---

## No Secrets in Portable ZIP

When a project is packaged or exported:

- No provider credentials are included.
- No API key is written to the bundle or ZIP.
- The bundle schema does not include fields for secrets.
- Existing bundle save/load must not be modified to add secret fields.

---

## No Network Execution

The dry-run provider must not:

- Open a network socket
- Resolve a DNS name for a provider
- Load a local model from a network path
- Import a library that performs auto-network operations on import

The dry-run adapter must be fully offline and deterministic.

---

## Dry-Run Only Until Explicitly Enabled by Later Task

All provider "execution" in v0.3 is dry-run only.

The dry-run adapter:

- Accepts a prompt and provider ID.
- Returns a synthetic response clearly labeled as dry-run.
- Does not contact any external system.
- Does not require configuration to function.

Real provider execution is gated behind a future explicit task.
No mechanism to bypass dry-run is included in this pack.

---

## Future API Key Storage Must Be Explicit, Revocable and User-Controlled

When real API key storage is implemented (future task):

- The user must explicitly enter keys — no defaults, no auto-discovery.
- Keys must be stored in a location controlled and accessible by the user.
- Keys must be revocable at any time without data loss.
- Keys must never be logged.
- Keys must never be committed to version control.
- Keys must never be bundled in release artifacts.
- Key storage implementation requires a dedicated security review task.

This rule is documented here for future implementers.
It does not authorize key storage in TASK-000076-080.
