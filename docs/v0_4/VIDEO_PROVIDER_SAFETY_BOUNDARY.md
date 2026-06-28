# Video Provider Safety Boundary — Aurora Studio v0.4

## Purpose

This document defines the safety boundary for the video provider adapter system in Aurora Studio v0.4.
It governs what is and is not implemented in TASK-000116–120 and the constraints that apply to all future video provider work.

---

## Current Provider Behavior (v0.4)

TASK-000116-120 does not perform real video provider API calls.
TASK-000116-120 does not generate videos.
TASK-000116-120 does not upload files or assets.
TASK-000116-120 does not decode or process local media.
TASK-000116-120 does not execute ffmpeg or external media tools.
TASK-000116-120 does not add provider SDKs.
TASK-000116-120 does not persist real API keys.
TASK-000116-120 does not store or log secrets.
Real video provider execution is blocked until a later task explicitly implements a real adapter.

The only available mode is `mock_video`, which returns a deterministic `mock://video/<id>` URI with no network call.

---

## v0.4 Video Readiness Scope

The v0.4 pack covers:
- Video provider request/response contracts (frozen dataclasses)
- Mock video adapter (deterministic, local, no network)
- Video prompt export bridge (prompt → mock result)
- UISession/CLI mock and readiness commands
- Safety QA docs and source-scan tests

---

## Non-Goals

The following are explicitly out of scope for v0.4:
- Real video generation via any external API
- Video file creation or storage
- Video upload or reference video ingestion
- Frame extraction or thumbnail generation
- ffmpeg/ffprobe/mediainfo execution
- Audio processing
- Image-to-video workflows
- Video playback or preview

---

## Real Video Execution Prerequisites

Real video execution requires ALL of the following before it may proceed in a future version:
1. Provider registered and enabled in provider registry
2. Real video execution explicitly requested by user
3. `real_video_execution_allowed = True` in gate config
4. Secret reference available (not the value)
5. Secret storage approved for this provider
6. Prompt-only request (no reference video upload)
7. No reference video uploaded
8. No reference image, mask, or asset uploaded
9. Log redaction enabled for this provider
10. Logging sanitized (secrets and prompt data scrubbed)
11. Network access allowed for this provider
12. User has explicitly confirmed real video execution
13. User has confirmed no PII in prompt text
14. Video safety review completed and approved

Until all prerequisites are met, `VideoProviderExecutionGate.evaluate_real_video()` returns `allowed=False`.

---

## Video Data Exposure Boundary

- Prompt text is local only in v0.4
- No video bytes may be included in `VideoProviderRequest`
- No base64-encoded video, image, or audio may be included in parameters
- `FORBIDDEN_PARAMETER_KEYS` enforces this at validation time

---

## Asset Upload Boundary

- No file upload of any kind is implemented in v0.4
- No `upload_file`, `file_path`, or `asset_binary` field exists in contracts

---

## Secret Handling Boundary

- No API key is stored in v0.4
- No secret is passed through the mock adapter
- Ephemeral call-time secret model applies if real execution is ever enabled
- `sanitize_error()` redacts sensitive patterns from error strings

---

## Logging/Redaction Boundary

- Run history stores only sanitized metadata: prompt preview, mock URI, job ID, status
- No secret appears in logs, run history, autosave, or export artifacts

---

## Network Boundary

- `execute_mock()` sets `network_call=False` in response
- No network call is made in any automated test
- `VideoProviderExecutionGate` performs no network calls

---

## Provider Adapter Boundary

- `VideoProviderAdapter.execute_real_video()` returns `status="blocked"` in base class
- `MockVideoProviderAdapter` never calls the network
- No provider SDK is imported

---

## Desktop UI Boundary

- Desktop shell imports safely with no video SDK
- UI surfaces mock-only mode with required wording: "Mock only. No video is generated."

---

## CLI Boundary

- `video-provider-mock` and `video-provider-readiness` commands output JSON
- No network call, no SDK, no secret, no video file

---

## Packaging Boundary

- No video file, no media binary, no SDK is included in the portable ZIP

---

## Testing Boundary

- No test file triggers a network call
- No test file creates a video file
- Source scan in QA pack confirms no forbidden imports in `src/aurora_studio/**/*.py`

---

## Future Implementation Tasks

Real video execution requires a dedicated future task covering:
- Provider SDK selection and security review
- Video safety classifier integration
- Secure ephemeral key entry flow
- Rate limiting and cost budget controls
- Video binary handling sandbox

---

## Acceptance Criteria

- [ ] `VideoProviderExecutionGate.evaluate_real_video()` returns `allowed=False`
- [ ] `MockVideoProviderAdapter.execute_mock()` returns `status="mock"`, `network_call=False`
- [ ] `video_uri` always uses `mock://video/<id>` scheme
- [ ] No forbidden imports in `src/aurora_studio/**/*.py`
- [ ] All automated tests pass without network calls
- [ ] No video file created during tests

---

*Aurora Studio v0.4 — TASK-000116*
