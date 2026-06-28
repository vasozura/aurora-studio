# Local Secret Storage Strategy — Aurora Studio v0.4

## Purpose

This document defines the strategy for managing provider secrets (API keys, tokens, passwords)
in Aurora Studio. It governs how secrets may and may not be stored, now and in future releases.

## Current State

Aurora Studio v0.4 does not store any real API key or secret. The provider execution gate
blocks real execution. The API key entry boundary redacts all user input. No secret is written
to any file.

## Non-Goals

This document does not implement OS keyring integration.
This document does not add the `keyring` package.
This document does not store real API keys.
Implementation is deferred to TASK-000106+.

## Threat Model

Secrets stored insecurely expose users to:
- API key theft via project file access.
- Secret leakage via log files, backups, or portable ZIPs.
- Unintended secret exposure via screenshot or export.
- Secret inclusion in release artifacts or version control.

Aurora Studio must protect against all of the above.

## Secret Classes

Class A — Provider API keys (OpenAI, Anthropic, Google, etc.)
Class B — OAuth access tokens and refresh tokens
Class C — Custom provider authentication headers
Class D — Future secrets (database credentials, S3 keys, etc.)

All secret classes are subject to the same storage prohibitions.

## Where Secrets Must Not Be Stored

Secrets must never be written to:
- project JSON (aurora_project.json)
- autosave files (.autosave/aurora_project.autosave.json)
- backup files (.backups/aurora_project.*.json)
- export artifacts (any file produced by the export pipeline)
- provider logs (any log entry stored in run history)
- run history (PromptRunHistory records)
- portable ZIP (release packaging artifacts)
- release notes
- screenshots
- console output / stdout / stderr

## Potential Storage Options

Option 1 — OS keyring (recommended for future):
  Store secrets in the platform keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service).
  Pros: OS-managed, not written to disk by the application, user can revoke.
  Cons: Requires keyring dependency, not portable, no-keyring fallback needed.

Option 2 — Encrypted local file (not recommended):
  Store an encrypted blob in a local file, with key derived from user passphrase.
  Pros: Works offline, portable.
  Cons: Key management is hard, passphrase fatigue, not OS-integrated.

Option 3 — Session-only in-memory (current approach):
  Never persist secrets; require re-entry each session.
  Pros: No storage risk.
  Cons: Poor UX for multi-session workflows.

Option 4 — User-managed environment variables:
  User exports secrets as environment variables; Aurora Studio reads from env.
  Pros: No storage by Aurora Studio, familiar to developers.
  Cons: Not user-friendly for non-developers, env leakage risk.

## Recommended Future Approach

Implement OS keyring integration in TASK-000106+ using the Python `keyring` package
or direct platform APIs. Design for:
- Per-provider keyring entries with a namespaced service name.
- Fallback to session-only mode if keyring is unavailable.
- User consent required before first keyring write.
- User revocation available from the provider config UI.

## OS Keyring Future

See `docs/v0_4/OS_KEYRING_INTEGRATION_PLAN.md` for the platform-specific integration plan.

## Portable Mode Implications

In portable ZIP mode:
- No keyring is available (different machine, different OS user account).
- Secrets must be re-entered by the user after unzipping.
- The portable ZIP must be verified to contain no secret values before distribution.

## User Consent and Revocation

Before any secret is written to the OS keyring:
- The user must be shown a consent dialog explaining what will be stored.
- The user must actively confirm.
- A revocation option must be available in the provider config UI.

## Backup / Export Exclusions

Backup manager (`ProjectBackupManager`) must never serialize secret fields.
Export pipeline must pass all output through `sanitize_provider_config_payload()`.
Autosave manager must never include secret fields in autosave JSON.

## Logging Exclusions

Provider log entries must pass through `sanitize_text_for_secrets()` before storage.
`PromptRunHistory` must never include raw secret values.
Run preview text must be truncated and redacted before logging.

## Testing Strategy

- Tests must verify that `to_dict()` on all provider contracts produces no secret fields.
- Tests must verify that `sanitize_provider_config_payload()` strips all key-like fields.
- Tests must verify that project bundle save/load does not persist secret values.
- Integration tests for OS keyring must use mocked keyring backends.

## Future Implementation Tasks

- TASK-000106+: OS keyring integration (Windows, macOS, Linux).
- TASK-000106+: Keyring consent UI flow.
- TASK-000106+: Keyring revocation flow.
- TASK-000106+: Session-only fallback if keyring is unavailable.
- TASK-000106+: Portable mode no-keyring policy.

## Acceptance Criteria

- This document exists and covers all sections listed above.
- No secret is written to any file in v0.4.
- All provider contracts produce no secret fields in `to_dict()`.
- Redaction utilities are tested and pass.
