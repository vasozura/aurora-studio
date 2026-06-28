# API Key Storage Plan — Aurora Studio

Status: Planning only
Task: TASK-000078
Version: 0.3.0
Date: 2026-06-28

---

## Purpose

This document defines the future rules and design constraints for storing
provider API keys in Aurora Studio.

API key storage is not implemented in TASK-000078.

This is a planning document only.

---

## Current Behavior

Aurora Studio v0.3 uses a local dry-run provider only.
No provider API keys are required.
No provider API keys are stored.
No network calls are made to external providers.

---

## Non-goals

- API key storage is not implemented in TASK-000078.
- No credential manager or keychain integration is added.
- No key rotation logic is added.
- No cloud sync of keys is added.
- No keys are bundled in any portable ZIP or release artifact.
- No API keys are committed to source control.

---

## Future Key Storage Rules

When API key storage is implemented in a later task, the following rules apply:

1. Keys are user-provided at runtime — never pre-bundled.
2. Keys are stored in the OS keychain (e.g. Windows Credential Manager, macOS Keychain).
3. Keys are never written to project bundle files.
4. Keys are never included in portable ZIP exports.
5. Keys are never logged — logs must be sanitized before writing.
6. Key storage must be explicit: the user must actively supply a key.
7. Key storage must be revocable: the user must be able to delete a key at any time.
8. Keys must never appear in error messages or stack traces.
9. Key access must be per-provider and scoped to the local machine.
10. There must be no global or shared key store.

---

## Revocability Rule

Key storage must be revocable.

Every stored key must have a corresponding delete operation.

Revoking a key must prevent further provider execution until a new key is supplied.

---

## No Bundled Keys Rule

No API key is bundled in:

- aurora-studio source code
- pyproject.toml
- aurora-studio portable ZIP
- aurora-studio installer
- any release artifact
- any docker image

---

## Secrets in Logs Rule

Logs must never contain secrets.

All request and response logs must be sanitized before writing.

The sanitizer must redact:

- Authorization headers
- Bearer tokens
- API key query parameters
- Any field named: key, secret, token, password, credential, api_key

---

## Secrets in Portable ZIP Rule

The portable ZIP bundle must never contain secrets.

Bundle export must explicitly exclude:

- Provider API keys
- OS keychain data
- Authentication tokens
- Any file containing credentials

---

## Future Implementation Tasks

The following tasks will implement key storage when the time comes:

- Create OS keychain abstraction layer
- Implement per-provider key write, read, delete operations
- Add key validation (format check only — no real API call during validation)
- Add UI for key entry, display (masked), and deletion
- Add log sanitizer that redacts known secret patterns
- Add integration test: key stored → provider enabled → key revoked → provider blocked
- Add bundle export test: assert no key fields in exported ZIP

---

## Testing Strategy

Planning tests verify:

- This document exists
- Required sections exist
- Document states API key storage is not implemented in TASK-000078
- Document states no keys are bundled
- Document states keys must be revocable
- Document states logs must not contain secrets
- Document states keys must not appear in portable ZIP

---

## Acceptance Criteria

- API_KEY_STORAGE_PLAN.md exists
- All required sections are present
- Document explicitly states no implementation in TASK-000078
- Document defines revocability rule
- Document defines no-bundled-keys rule
- Document defines sanitized-logs rule
- tests/test_api_key_storage_planning.py passes
