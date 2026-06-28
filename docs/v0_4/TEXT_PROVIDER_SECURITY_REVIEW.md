# Text Provider Security Review — v0.4

## Scope

This document reviews the security posture of Aurora Studio's v0.4 text provider
adapter system covering: secret handling, execution gate, transport security,
and audit surface.

---

## 1. Secret Handling

### 1.1 Ephemeral Call-Time Secret Model

Aurora Studio v0.4 uses an ephemeral call-time secret model:

- API secrets are **never stored** on adapter instances, in project JSON,
  autosave files, backup files, export artifacts, logs, run history, or
  portable bundles.
- The secret is accepted as a parameter at the point of execution
  (`execute_real_text(request, ephemeral_secret)`) and is used only for that
  single HTTP request.
- After the call returns, the reference is not retained anywhere in the system.

### 1.2 CLI Secret Handling

**WARNING: Do not pass API keys as command-line arguments because shell history
may retain them.**

If a real-execution CLI command is ever added, it must read the secret from an
environment variable (e.g. `AURORA_PROVIDER_SECRET`) rather than from a
`--secret` or `--api-key` argument. Shell history files (`.bash_history`,
`.zsh_history`, etc.) persist command-line arguments and can expose secrets
to other users or processes with filesystem access.

### 1.3 Error Message Redaction

The adapter explicitly replaces the ephemeral secret with `<redacted>` in any
exception message before returning it in the error response payload. This
prevents accidental leakage through error logging.

---

## 2. Execution Gate

### 2.1 Gate Design

- `ProviderExecutionGate.is_real_execution_allowed()` returns `False` by default
  in v0.4 for all providers.
- `evaluate_real_text_execution()` checks 11 prerequisites; all must be satisfied
  before `allowed=True` is returned.
- In the `execute()` routing method, real text is only dispatched to
  `execute_real_text()` after gate approval AND a non-empty ephemeral secret.

### 2.2 UISession Confirmation Gate

`execute_text_provider_real_with_ephemeral_secret()` requires `confirm=True`
as an explicit parameter. Without it, the method immediately returns an error.
This is an application-layer gate independent of the execution gate.

---

## 3. Forbidden Dependencies

The following packages must never appear in `src/aurora_studio/**/*.py`:

| Package | Reason |
|---------|--------|
| `openai` | Provider SDK — adds unpinned network dependency |
| `anthropic` | Provider SDK — adds unpinned network dependency |
| `requests` | Third-party HTTP — use stdlib `urllib.request` |
| `httpx` | Third-party HTTP — use stdlib `urllib.request` |
| `aiohttp` | Third-party async HTTP — use stdlib `urllib.request` |

Real HTTP is performed using `urllib.request` (Python standard library only),
gated behind the execution gate.

---

## 4. Transport Security

- All real HTTP calls use HTTPS (enforced by the base URL default:
  `https://api.openai.com/v1`).
- Custom `base_url` values should be validated by the operator to use HTTPS
  for production endpoints.
- The `Authorization: Bearer <secret>` header is constructed at call time and
  not cached or logged.

---

## 5. Audit Surface

| Component | Stores Secret? | Network Call? | Notes |
|-----------|---------------|---------------|-------|
| `TextProviderRequest` | No | No | `ephemeral_secret_ref` is a label only |
| `TextProviderResponse` | No | Reflects actual | `network_call=True` only on real HTTP |
| `OpenAICompatibleTextAdapter` | No | Only in `execute_real_text()` | Secret passed, never stored |
| `UISession` run history | No | No | Secret fields stripped before storage |
| CLI output | No | No | Secret never in stdout |

---

## 6. Known Limitations (v0.4)

- Real execution gate always returns `False` — no production provider calls can
  be made through the gate in this release.
- OS keyring integration deferred to a future release.
- Secret rotation and revocation are out of scope for v0.4.

---

*Last updated: v0.4 — TASK-000110*
