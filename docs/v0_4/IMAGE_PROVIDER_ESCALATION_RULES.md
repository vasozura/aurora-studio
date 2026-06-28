# Image Provider Escalation Rules — v0.4

## Purpose

This document defines the rules that govern when and how Aurora Studio may escalate
from mock image execution to real image provider execution. In v0.4, real image
execution is blocked by default.

## What Counts as Real Image Provider Execution

Real image provider execution includes any of the following:

- Network call to an image provider API endpoint
- Provider SDK invocation (openai, stability, replicate, runway, kling, pika, luma, etc.)
- Sending prompt text outside the local machine for image generation
- Sending image files, reference images, masks, or assets outside the local machine
- Using a real API key to authenticate with an external service
- Receiving a generated image or image URL from an external service
- Streaming image generation output from an external service

## Required User Configuration

Before any real image provider execution:

1. User must explicitly enable real image execution in provider config
2. User must select a specific provider and model
3. User must acknowledge the real image execution warning
4. Provider must be registered and enabled in the provider registry

## Required Secret Storage Decision

1. A secret storage strategy must be selected (OS keyring or call-time ephemeral)
2. The chosen strategy must be approved in provider config
3. Secret must NOT be stored in project JSON, autosave, backup, logs, or exports

## Required Prompt Safety Warning

Before executing a real image prompt, the system must warn:

- "This prompt will be sent to an external provider"
- "Do not include personal, sensitive, or regulated information"
- "Provider costs and terms are your responsibility"
- "Reference images (if supported) will also be sent externally"

## Required Asset Upload Consent

If reference images are supported (future task only):

- User must explicitly consent to uploading each reference image
- System must warn that reference images leave the local machine
- No automatic upload of any asset

## Required Redaction

- Prompt text must be truncated/sanitized in logs
- Secret values must be redacted from all logs, error messages, and payloads
- Generated image URLs must not be stored persistently

## Required Provider Adapter Tests

Before a real image provider adapter ships:

- Unit tests must cover all execution paths using monkeypatched HTTP
- No automated test may perform a real network call
- Gate must be tested with both blocked and allowed configurations
- Error handling for network failures must be tested

## Required Mock Tests

- Mock execution must work without secrets or network
- Mock must return a deterministic `mock://image/<id>` URI
- Mock must not create image files
- Mock must pass all safety boundary checks

## Required Opt-In UI

Real image execution UI must:

- Require explicit opt-in (no default-on button)
- Display current execution mode prominently
- Display "Real image execution may send prompts outside this machine"
- Require confirmation before each real execution

## Required CLI Safeguards

If real image CLI is ever added:

- Read secret from environment variable only (not `--api-key` argument — shell history risk)
- Display warning before executing
- Require `--confirm-real-execution` flag

## Required Packaging Safeguards

- No image provider secrets in release artifacts
- No image bytes in release artifacts
- No provider SDK in release dependencies

## Blocked-By-Default Rule

Real image execution is BLOCKED BY DEFAULT in all v0.4 and earlier releases.

The `ImageProviderExecutionGate` returns `allowed=False` for `real_image` mode
unless ALL prerequisites in `REAL_IMAGE_PREREQUISITES` are satisfied in the
gate config. In v0.4, this cannot be achieved through normal operation.

## Go/No-Go for Real Image Adapter Implementation

A real image provider adapter may only be implemented when:

- [ ] All prerequisites defined in IMAGE_PROVIDER_SAFETY_BOUNDARY.md are implementable
- [ ] A specific provider has been selected and reviewed
- [ ] Secret storage strategy is finalized
- [ ] A security review for the specific provider has been completed
- [ ] User-facing warnings are finalized
- [ ] A new explicit gate has been designed and reviewed
- [ ] Test plan includes monkeypatched HTTP tests for all error cases
- [ ] The implementation is in a dedicated new task (not TASK-000111-115)

---

*Last updated: v0.4 — TASK-000111*
