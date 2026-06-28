# Local Provider Config Boundary — Aurora Studio v0.3

Status: Planning only
Task: TASK-000078
Version: 0.3.0
Date: 2026-06-28

---

## Purpose

This document defines what provider configuration Aurora Studio v0.3 may and
may not store locally.

---

## What v0.3 May Store Locally

- Provider metadata (name, version, type, capabilities) — in memory only
- Provider enabled/disabled state — in memory only
- Dry-run provider configuration — no secrets required
- Provider display preferences — in memory only

---

## What v0.3 Must Not Store Locally

- Real API keys
- Authentication tokens
- Bearer credentials
- Any secret that could authorize a network request
- Any credential in a project bundle file
- Any credential in a portable ZIP

---

## No Real Credential Storage in TASK-000076-080

No real credential storage is implemented in TASK-000076 through TASK-000080.

The provider config manager, if created, may only store:

- Provider ID
- Provider display name
- Provider enabled/disabled flag
- Provider type

It must not store:

- API keys
- Tokens
- Passwords
- Secrets of any kind

---

## Config File Boundary

If a provider config file is written to disk in a future task, it must:

- Use JSON format only
- Contain no secret fields
- Be stored outside the portable bundle
- Never be included in bundle export
- Never be synced to cloud

---

## Provider Config Manager Scope (Future)

A future ProviderConfigManager may:

- Store display names and enabled/disabled state per provider
- Persist config to a local non-bundle file
- Read config on startup

A future ProviderConfigManager must not:

- Store API keys or tokens
- Accept secret values as parameters
- Include config in bundle serialization

---

## Dry-Run Config

The local dry-run provider requires no configuration.

It is always available.

It requires no API key.

It requires no network access.

---

## Future Escalation

When real provider support is added (a later sprint), a separate task must:

1. Define the OS keychain abstraction
2. Implement per-provider key storage
3. Add UI for key management
4. Add sanitized log output
5. Validate no secrets appear in bundle exports

This work must not begin until explicitly authorized in a sprint task.

---

## Acceptance Criteria

- This document exists
- Document states no real credential storage in TASK-000076-080
- Document defines allowed and disallowed local config fields
- Document defines dry-run config scope
- Document defines future escalation path
