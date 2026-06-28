# Text Provider Adapter QA Checklist — v0.4

## Purpose

This checklist must be completed before any text provider adapter is considered
ready for production use in Aurora Studio. It covers security, safety, and
correctness requirements.

---

## 1. Execution Mode Coverage

- [ ] Dry-run mode implemented — validates request, no text generated, no network call
- [ ] Mock mode implemented — deterministic local response, no network call
- [ ] Real text mode present but blocked by default via gate
- [ ] blocked_real mode returns blocked status immediately

## 2. Secret Handling

- [ ] No secret stored on adapter instance (no `self.secret`, `self.api_key`, `self.token`)
- [ ] Ephemeral secret accepted only at call time (`execute_real_text(request, ephemeral_secret)`)
- [ ] Ephemeral secret NOT returned in any response payload or `to_dict()` output
- [ ] Ephemeral secret redacted from error messages before returning response
- [ ] Secret never written to logs, run history, export artifacts, or project JSON
- [ ] `to_safe_dict()` / `to_json()` on request contract redacts `ephemeral_secret_ref`

## 3. Network Safety

- [ ] `network_call=False` on all dry_run responses
- [ ] `network_call=False` on all mock responses
- [ ] `network_call=False` on all blocked responses
- [ ] `network_call=True` only on successful real HTTP responses
- [ ] No real network calls in automated test suite (monkeypatched or not reached)
- [ ] Real HTTP uses only `urllib.request` from stdlib — no openai/anthropic/requests/httpx/aiohttp

## 4. Gate Enforcement

- [ ] `execute()` checks `is_real_execution_allowed()` before calling `execute_real_text()`
- [ ] Gate returns False by default in v0.4
- [ ] `execute_real_text()` called only when gate returns True AND ephemeral_secret provided
- [ ] UISession `execute_text_provider_real_with_ephemeral_secret()` requires `confirm=True`

## 5. Forbidden SDK Imports

- [ ] No `import openai` in any `src/aurora_studio/**/*.py` file
- [ ] No `from openai` in any `src/aurora_studio/**/*.py` file
- [ ] No `import anthropic` in any `src/aurora_studio/**/*.py` file
- [ ] No `from anthropic` in any `src/aurora_studio/**/*.py` file
- [ ] No `import requests` in any `src/aurora_studio/**/*.py` file
- [ ] No `import httpx` in any `src/aurora_studio/**/*.py` file
- [ ] No `import aiohttp` in any `src/aurora_studio/**/*.py` file

## 6. Contract Correctness

- [ ] `TextProviderRequest` is a `frozen=True` dataclass
- [ ] `TextProviderResponse` is a `frozen=True` dataclass
- [ ] All `to_dict()` / `to_json()` outputs are JSON-serializable
- [ ] `from_dict()` roundtrip produces equivalent contract
- [ ] Validation errors returned as list of string codes, not exceptions

## 7. CLI Safety

- [ ] `text-provider-mock` — no network, no secret field in output
- [ ] `text-provider-readiness` — reports all prerequisites, never executes
- [ ] Real CLI (if implemented) reads secret from env var, NOT command-line argument
  (shell history may retain command-line arguments — see REAL_PROVIDER_USER_WARNING.md)

## 8. Documentation

- [ ] `TEXT_PROVIDER_ADAPTER_QA_CHECKLIST.md` present
- [ ] `TEXT_PROVIDER_SECURITY_REVIEW.md` present
- [ ] `REAL_PROVIDER_USER_WARNING.md` present

---

*Last updated: v0.4 — TASK-000110*
