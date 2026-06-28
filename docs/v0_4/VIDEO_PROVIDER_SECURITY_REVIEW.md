# Video Provider Security Review — Aurora Studio v0.4

> Threat model and security review for the v0.4 video provider adapter pack.

---

## Threat Model

### T1 — Accidental Real Video Execution
**Risk**: Mock video adapter accidentally triggers a real network call or video generation.
**Mitigations**:
- `VideoProviderExecutionGate.evaluate_real_video()` always returns `allowed=False`.
- `VideoProviderAdapter.execute_real_video()` returns `status="blocked"` in base class.
- `MockVideoProviderAdapter.execute()` routes any non-mock mode to the blocked response.
- Test: `test_execute_real_video_blocked` in `test_mock_video_provider_adapter.py`.

### T2 — Secret Exfiltration via Response Payload
**Risk**: A leaked API key or token appears in response JSON.
**Mitigations**:
- `VideoProviderResponse` contains no secret-holding fields.
- `sanitize_response_payload()` strips forbidden keys.
- `sanitize_error()` redacts sensitive patterns from error strings.
- `to_dict()` verified to exclude `api_key`, `secret`, `token`, `password`.
- Test: `test_response_no_secret_fields` in `test_mock_video_provider_adapter.py`.

### T3 — Binary Payload Injection (video/audio bytes)
**Risk**: A caller passes `video_bytes`, `audio_bytes`, or base64 in parameters.
**Mitigations**:
- `FORBIDDEN_PARAMETER_KEYS` blocks all binary/upload keys.
- `validate_video_provider_request()` rejects requests with forbidden keys.
- `VideoProviderRequest` has no binary-holding fields in its schema.

### T4 — Video File Creation
**Risk**: Adapter creates video files on disk.
**Mitigations**:
- `execute_mock()` builds only an in-memory `VideoProviderResponse`.
- `video_uri` is always `mock://video/<request_id>` — never a file URI.
- No `open()`, `write()`, PIL, cv2, moviepy, or ffmpeg imported in source.
- Test: `test_no_video_file_created` in adapter and bridge test files.

### T5 — Forbidden Library or Tool Import
**Risk**: A future diff adds PIL, cv2, moviepy, ffmpeg, subprocess, or httpx.
**Mitigations**:
- Source scan in QA test: `test_video_provider_no_forbidden_imports_in_source`.
- CI should fail immediately if any forbidden import appears in `src/aurora_studio/**/*.py`.

### T6 — Prompt Injection via Export Artifact
**Risk**: Export artifact ID contains shell metacharacters or injection vectors.
**Mitigations**:
- `build_video_prompt_from_export()` wraps artifact ID in a plain text template string.
- No shell exec, no file read, no subprocess. Pure string composition.
- Prompt preview truncated to 120 characters in run result.

### T7 — Run History Secrets Leak
**Risk**: Provider run history persists secrets between sessions.
**Mitigations**:
- Run history is a plain Python list on `VideoPromptExportBridge` — ephemeral, cleared on restart.
- No run history is written to disk, JSON files, autosave files, logs, or backups.
- `_build_result()` explicitly excludes secrets from the result dict.

### T8 — External Media Tool Execution
**Risk**: ffmpeg, ffprobe, mediainfo, or ImageMagick is called on user prompt or artifact input.
**Mitigations**:
- No subprocess call for media in any video provider module.
- No `os.system` call in any video provider module.
- Source scan verifies absence of forbidden tool invocations.

---

## Prompt Data Exposure

In v0.4: prompt text stays local. No prompt text is transmitted to any external service.
In a future real-execution version: prompt text will be transmitted to the video provider API. The user warning doc (`REAL_VIDEO_PROVIDER_USER_WARNING.md`) discloses this.

## Reference Image/Video Exposure

Not implemented in v0.4. If reference media is supported in a future version, the user warning doc must be updated and reference asset transmission must be gated by explicit user consent.

## Secret Exposure

No secret is stored, logged, or transmitted in v0.4. Ephemeral model applies if real execution is ever enabled.

## Local Storage Risks

Run history is in-memory only. No video data is written to disk.

## Log/Redaction Risks

Provider logs contain sanitized metadata only. `sanitize_error()` and `sanitize_response_payload()` are applied before any string reaches logs.

## CLI Risks

CLI stdout contains only JSON with no secrets. `api_key`, `sk-*` patterns are verified absent by tests.

## Desktop UI Risks

Desktop shell imports safely. No video SDK import. Mock-only mode displayed with required warning text.

## Network Risks

No network call in v0.4. All execution is local. `network_call=False` enforced in responses.

## Provider Response Risks

`raw_response_preview` is truncated to 200 characters and redacted. No full provider response is stored.

## Generated Media Risks

No media is generated in v0.4. `video_uri` is always `mock://video/<id>` — not a real URL.

## External Media Tool Risks

No ffmpeg, ffprobe, mediainfo, or ImageMagick invocation in v0.4.

## Packaging Risks

Portable ZIP includes no video files, media binaries, or provider SDKs.

## Rollback Strategy

If any real execution path is accidentally enabled, the change must be reverted immediately. Gate is hardcoded to block real execution.

## Future Hardening Tasks

- Video safety classifier integration (before any real video is displayed)
- Secure ephemeral key entry flow
- Rate limiting and cost budget controls
- Video binary handling sandbox (memory-limited)
- Full security review before `evaluate_real_video()` can return `allowed=True`

---

*Aurora Studio v0.4 — TASK-000120*
