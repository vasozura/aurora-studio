# Provider Foundation QA Checklist — Aurora Studio v0.3

Status: QA Planning
Task: TASK-000085
Version: 0.3.0
Date: 2026-06-28

---

## Purpose

This document is the QA checklist for the v0.3 provider foundation and prompt
execution workflow implemented in TASK-000076 through TASK-000085.

---

## Scope

Covered by this checklist:

- Provider registry (TASK-000077)
- Local provider config boundary (TASK-000078)
- Dry-run adapter (TASK-000079)
- Provider request/response log (TASK-000080)
- Prompt execution queue (TASK-000081)
- Batch prompt export (TASK-000082)
- Prompt run history (TASK-000083)
- Provider error handling (TASK-000084)
- Architecture boundary docs (TASK-000076)
- Security boundary docs (TASK-000076)

---

## Non-goals

This checklist does not cover:

- Real provider API calls
- Provider SDK integration
- API key storage implementation
- Network execution
- Background worker testing
- Database queue persistence
- Plugin execution
- Image/video/audio generation

---

## Provider Registry Checks

- [ ] ProviderRegistry imports without errors
- [ ] Built-in dry-run provider is always present
- [ ] list_providers() returns at least one entry
- [ ] register_provider() accepts valid types only
- [ ] enable_provider() sets state to "available"
- [ ] disable_provider() sets state to "disabled"
- [ ] mark_provider_error() sets state to "error"
- [ ] get_provider() returns ValidationError for unknown IDs

---

## Provider Config Boundary Checks

- [ ] No real API keys in provider config
- [ ] No secrets stored by ProviderRegistry
- [ ] Provider state is in-memory only
- [ ] Config does not appear in bundle export
- [ ] LOCAL_PROVIDER_CONFIG_BOUNDARY.md exists and is accurate

---

## Dry-Run Adapter Checks

- [ ] ProviderDryRunAdapter imports without SDK
- [ ] execute() returns status="dry_run"
- [ ] execute() with empty prompt raises ValidationError
- [ ] output_text is non-empty
- [ ] output_text contains [DRY-RUN] label
- [ ] No network module imported during execution
- [ ] No openai/anthropic/requests module imported

---

## Prompt Execution Queue Checks

- [ ] PromptExecutionQueue imports without errors
- [ ] enqueue_request() creates item with status="queued"
- [ ] mark_running/completed/failed/blocked/cancelled all work
- [ ] clear_completed() removes only completed items
- [ ] execute_next_with_dry_run() processes one item
- [ ] No background thread created during queue operation

---

## Batch Export Checks

- [ ] BatchPromptExportManager imports without errors
- [ ] render_batch() returns rendered text for each source
- [ ] create_export_artifacts_for_batch() creates artifacts
- [ ] Partial failure returns status="partial"
- [ ] Empty source_ids returns status="failed"
- [ ] No provider execution during batch export
- [ ] Result is JSON-serializable

---

## Run History Checks

- [ ] PromptRunHistory imports without errors
- [ ] record_dry_run() stores sanitized preview
- [ ] record_batch_result() stores one entry per source
- [ ] record_manual_export() creates entry
- [ ] sanitize_preview() redacts secret patterns
- [ ] sanitize_preview() truncates long text
- [ ] clear_history() empties all records

---

## Provider Log Checks

- [ ] ProviderLog imports without errors
- [ ] record() creates log entry from request+response
- [ ] Secret patterns are redacted from prompt_preview
- [ ] list_entries() returns most recent first
- [ ] clear() returns count and empties log

---

## Error Handling Checks

- [ ] normalize_error() infers validation_error from "must not be empty"
- [ ] normalize_error() infers provider_disabled from "disabled"
- [ ] is_retryable() returns True for network_error, timeout, rate_limited
- [ ] is_retryable() returns False for validation_error, blocked
- [ ] to_user_message() contains no Traceback text
- [ ] to_log_payload() is JSON-serializable
- [ ] Secret patterns are sanitized from error messages

---

## Secret Handling Checks

- [ ] No real API keys exist in codebase
- [ ] No secrets exist in provider registry
- [ ] No secrets exist in log entries
- [ ] No secrets exist in run history
- [ ] No secrets exist in error messages
- [ ] No secrets would appear in bundle export

---

## No Real Provider API Calls

No real provider API calls are included in TASK-000076-085.

All execution is local dry-run only.

No provider SDKs are installed or imported.

No API keys are stored.

---

## No Provider SDKs Included

No provider SDKs are included in TASK-000076-085.

The following must not be importable in this codebase:

- openai
- anthropic
- cohere
- huggingface_hub
- boto3 (provider-related usage)
- google-generativeai

---

## No Real API Keys Stored

No real API keys are stored in TASK-000076-085.

Key storage planning is documented in API_KEY_STORAGE_PLAN.md.

Implementation requires a later task.

---

## No Secrets Logged

All logs must sanitize secret-like content before storing.

Sanitized patterns include: api_key, token, bearer, secret, password, credential, authorization.

---

## Dry-Run Provider Is Local Only

The dry-run provider executes locally.

It does not make network calls.

It does not require an API key.

It always returns status="dry_run".

---

## Plugin Execution Remains Disabled

No plugin code is loaded in TASK-000076-085.

Plugin execution requires a later sandbox task.

---

## Desktop UI Checks

- [ ] Providers tab exists in TABS list
- [ ] refresh_providers() works headless
- [ ] list_providers() returns JSON-serializable payload
- [ ] Dry-run section accepts prompt and returns output

---

## CLI Checks

- [ ] python -m aurora_studio.cli smoke passes
- [ ] python -m aurora_studio.cli provider-smoke outputs JSON (if implemented)
- [ ] python -m aurora_studio.ui.desktop_shell --headless-smoke passes

---

## Packaging Checks

- [ ] No provider SDK appears in pyproject.toml dependencies
- [ ] Bundle export does not include provider state

---

## Known Limitations

- Queue is in-memory only (no persistence)
- Run history is in-memory only (no persistence)
- Provider logs are in-memory only (no persistence)
- Batch export does not invoke dry-run (local render only)
- Error type inference is pattern-based, not exhaustive
- No real provider execution in any component
