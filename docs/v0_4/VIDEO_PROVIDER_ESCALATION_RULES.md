# Video Provider Escalation Rules — Aurora Studio v0.4

## Purpose

Define what constitutes "real video execution" for escalation and blocking purposes.

---

## Definition of Real Video Execution

Real video execution is any of the following:

- A network call to a video provider API endpoint
- Invocation of a video provider SDK (Runway, Pika, Kling, Sora, etc.)
- Sending prompt text outside the local machine for video generation
- Sending image, video, audio, reference assets, or mask data outside the local machine
- Using a real API key or bearer token to authenticate with a provider
- Receiving a generated video, video URL, job ID, or render status from an external service
- Spawning a subprocess to run ffmpeg, ffprobe, mediainfo, or any external media tool
- Uploading any file or binary asset to any endpoint

---

## Escalation Triggers

Any of the following in code or tests constitutes an escalation that MUST be blocked:

| Trigger | Action |
|---|---|
| `import requests` / `import httpx` / `import aiohttp` | Block — forbidden HTTP library |
| `import openai` / `import anthropic` / any provider SDK | Block — forbidden SDK |
| `import PIL` / `import cv2` / `import moviepy` / `import ffmpeg` | Block — forbidden media library |
| `subprocess.run(...)` with ffmpeg/ffprobe/mediainfo | Block — forbidden external tool |
| `os.system(...)` with media tool | Block — forbidden shell call |
| `urllib.request.urlopen(...)` in test code | Block — network call in test |
| `video_bytes`, `video_base64`, `audio_bytes` in request | Block — binary payload |
| `api_key`, `secret`, `token`, `password` in response | Block — secret leakage |
| Writing `.mp4`, `.mov`, `.webm`, `.avi`, `.gif` to disk | Block — video file creation |

---

## Allowed in v0.4

| Action | Allowed |
|---|---|
| `mock_video` mode execution | Yes |
| Returning `mock://video/<id>` URI | Yes |
| `video_uri` in response (mock scheme only) | Yes |
| Returning mock `job_id` string | Yes |
| In-memory run history (ephemeral) | Yes |
| Sanitized prompt preview in logs | Yes |
| CLI `video-provider-mock` command | Yes |
| CLI `video-provider-readiness` command | Yes |

---

## Gate Decision

`VideoProviderExecutionGate.evaluate_real_video()` must always return `allowed=False` in v0.4.
`VideoProviderExecutionGate.evaluate_mock_video()` always returns `allowed=True`.

---

## Rollback Rule

If any real video execution path is accidentally enabled, the change must be reverted immediately.
No partial enablement is permitted.

---

*Aurora Studio v0.4 — TASK-000116*
