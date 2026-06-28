# Video Provider Adapter QA Checklist — Aurora Studio v0.4

> Companion to `VIDEO_PROVIDER_SAFETY_BOUNDARY.md`.
> All items must pass before any video provider adapter ships.

---

## Purpose

Verify that the v0.4 video provider adapter pack is safe for mock-only use and that no real video execution, video generation, video upload, media decoding, or external tool execution is possible.

## Scope

- `VideoProviderRequest` / `VideoProviderResponse` contracts
- `VideoProviderAdapter` base class
- `MockVideoProviderAdapter`
- `VideoProviderExecutionGate`
- `VideoPromptExportBridge`
- UISession and CLI surface

## Non-Goals

- Real video generation
- Video file creation
- Media upload or download
- ffmpeg/ffprobe/mediainfo execution
- Frame extraction or thumbnail generation

---

## Default Blocked Behavior

- [x] Real video provider execution is blocked by default.
- [x] No video generation is implemented.
- [x] No video upload is implemented.
- [x] No media decoding is implemented.
- [x] No ffmpeg or external media tool execution is implemented.
- [x] Provider SDKs are not used.
- [x] Secrets are not persisted or logged.
- [x] Project JSON/autosave/backups/run history/export artifacts must not contain secrets.
- [x] Automated tests must not perform real network calls.
- [x] Automated tests must not create video files.

---

## Mock Video Execution Checks

- [ ] `execute_mock()` always returns `status="mock"`.
- [ ] `video_uri` always starts with `mock://video/`.
- [ ] `job_id` always starts with `mock-job-`.
- [ ] `network_call=False` in all mock responses.
- [ ] `mock_response=True` in all mock responses.
- [ ] No video file (.mp4, .mov, .webm, .avi, .mkv) created during mock execution.

## Gate Checks

- [ ] `VideoProviderExecutionGate.evaluate_mock_video()` returns `allowed=True`.
- [ ] `VideoProviderExecutionGate.evaluate_real_video()` returns `allowed=False`.
- [ ] Gate performs no network call.
- [ ] Gate decision is JSON-serializable.
- [ ] All 15 real video prerequisites are unsatisfied in v0.4.

## Secret Handling Checks

- [ ] No adapter stores `secret_value` on `self`.
- [ ] No adapter writes secrets to JSON, logs, or autosave files.
- [ ] `sanitize_error()` redacts sensitive patterns.
- [ ] `sanitize_response_payload()` strips forbidden keys.
- [ ] Response `to_dict()` excludes `api_key`, `token`, `secret`, `password`.

## Prompt Data Exposure Checks

- [ ] Prompt text is local only in v0.4.
- [ ] Prompt preview in run history is truncated to 120 characters.
- [ ] No prompt text is sent to any external service.

## Asset Upload Checks

- [ ] No `upload_file`, `file_path`, or `asset_binary` field in contracts.
- [ ] `FORBIDDEN_PARAMETER_KEYS` includes all binary/upload keys.
- [ ] `validate_video_provider_request()` rejects forbidden parameter keys.

## Media Decoding Checks

- [ ] No PIL import in `src/aurora_studio/**/*.py`.
- [ ] No cv2 import in `src/aurora_studio/**/*.py`.
- [ ] No moviepy import in `src/aurora_studio/**/*.py`.
- [ ] No ffmpeg import in `src/aurora_studio/**/*.py`.

## External Tool Checks

- [ ] No `subprocess` call for media processing in video provider modules.
- [ ] No `os.system` call with media tool in video provider modules.
- [ ] No `ffprobe`, `ffmpeg`, `mediainfo` invocation anywhere in `src/`.

## Redaction Checks

- [ ] `sanitize_error()` in `MockVideoProviderAdapter` redacts secrets.
- [ ] `sanitize_response_payload()` in base adapter redacts and truncates.

## Network Boundary Checks

- [ ] `execute_mock()` sets `network_call=False`.
- [ ] No automated test triggers an HTTP connection.
- [ ] `VideoProviderExecutionGate` makes no network calls.

## UI Checks

- [ ] Desktop shell imports safely with no video SDK.
- [ ] `UISession.execute_video_provider_mock()` returns `ok=True`.
- [ ] `UISession.evaluate_video_provider_real_readiness()` returns `real_video_execution_ready=False`.

## CLI Checks

- [ ] `video-provider-mock` exits 0 and returns JSON `status="mock"`.
- [ ] `video-provider-readiness` exits 0 and returns `real_video_execution_ready=false`.
- [ ] No secret appears in CLI stdout.

## Run History Checks

- [ ] `list_video_provider_runs()` returns sanitized metadata only.
- [ ] No secret in run history payload.
- [ ] Run history is in-memory (ephemeral).

## Provider Log Checks

- [ ] Provider logs contain no raw secrets.
- [ ] Provider logs contain no video bytes.

## Export Artifact Checks

- [ ] Export artifact type is `mock_video_result` (text/JSON only).
- [ ] No video bytes or base64 in export artifacts.

## Packaging Checks

- [ ] No video file in portable ZIP.
- [ ] No media binary in portable ZIP.
- [ ] No provider SDK in portable ZIP.

---

## Known Limitations

- Real video execution is not available in v0.4.
- `video_uri` is a mock URI only; no actual video is accessible.
- Run history is in-memory and cleared on restart.

---

## Evidence Checklist

- [ ] `python -m unittest` passes with all video provider tests.
- [ ] `python -m aurora_studio.cli.main video-provider-mock --provider mock-video --prompt "test"` returns mock status.
- [ ] `python -m aurora_studio.cli.main video-provider-readiness --provider mock-video` returns blocked.
- [ ] Source scan test passes in `test_video_provider_safety_qa_pack.py`.

---

*Aurora Studio v0.4 — TASK-000120*
