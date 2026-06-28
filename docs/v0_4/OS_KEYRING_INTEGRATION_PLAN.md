# OS Keyring Integration Plan — Aurora Studio v0.4

## Purpose

This document plans the future integration of OS keyring backends for secure provider
secret storage. No integration is implemented in v0.4.

TASK-000103 does not implement OS keyring integration.
TASK-000103 does not add keyring dependency.
TASK-000103 does not store real API keys.

## Supported Future Platforms

- Windows: Windows Credential Manager (via `keyring` package, WinCred backend)
- macOS: macOS Keychain (via `keyring` package, Keychain backend)
- Linux: Secret Service API / libsecret (via `keyring` package, SecretService backend)

## Windows Credential Manager Future

- Service name: `AuroraStudio/<provider_id>`
- Username: `aurora_studio_user`
- Secret stored as a Windows Credential entry.
- Revocation: delete credential via Windows Credential Manager or Aurora Studio UI.
- Prerequisites: `keyring` package installed, Windows 10/11.

## macOS Keychain Future

- Service name: `AuroraStudio/<provider_id>`
- Account name: `aurora_studio_user`
- Secret stored as a Keychain item.
- Revocation: delete keychain item via Keychain Access or Aurora Studio UI.
- Prerequisites: `keyring` package installed, macOS 12+.

## Linux Secret Service Future

- Service name: `AuroraStudio/<provider_id>`
- Secret stored via D-Bus Secret Service API (libsecret).
- Revocation: delete secret via GNOME Seahorse or Aurora Studio UI.
- Prerequisites: `keyring` package installed, `libsecret` or compatible provider.

## Fallback Behavior

If OS keyring is unavailable:
- Aurora Studio falls back to session-only mode.
- The user is informed that secrets will not persist between sessions.
- No secret is written to disk in fallback mode.

## No-Keyring Mode

If the user explicitly disables keyring integration:
- Secrets are held in memory for the current session only.
- The provider config UI shows status: `not_configured`.
- Re-entry is required on each application launch.

## Portable Mode

In portable ZIP mode:
- OS keyring is not available (different user account, different machine).
- Secrets must be re-entered after unzipping.
- The portable ZIP is verified to contain no secret values.

## Migration Strategy

When upgrading from session-only to keyring:
1. User opens provider config UI.
2. User clicks "Save API Key to Keyring".
3. Consent dialog is shown.
4. On confirmation, key is written to OS keyring.
5. Session-only state is cleared from memory.
6. Provider config UI updates to show `configured_without_secret` (key in keyring, not in bundle).

## Revocation

User may revoke keyring entry at any time:
1. User opens provider config UI.
2. User clicks "Remove Saved Key".
3. Aurora Studio deletes the keyring entry.
4. Provider returns to `not_configured` state.

## Testing Requirements

- Unit tests for keyring read/write must use a mocked keyring backend.
- No test may write to the real OS keyring.
- Integration tests must verify that fallback mode works without a keyring.
- Tests must verify that revocation clears the entry.

## Security Review Requirements

Before keyring integration ships:
- Security review must confirm that the service name namespace prevents cross-app collisions.
- Security review must confirm that revocation is complete (no residual data).
- Security review must confirm that the fallback does not accidentally persist secrets.

## Implementation Prerequisites

The following must be complete before keyring integration begins:
1. This plan has been reviewed and approved.
2. The `keyring` package is added to `pyproject.toml` (requires explicit user instruction).
3. A dedicated task (TASK-000106+) authorizes the implementation.
4. The provider execution gate has a mechanism to open it for specific providers.
5. User consent UI flow is designed and approved.
