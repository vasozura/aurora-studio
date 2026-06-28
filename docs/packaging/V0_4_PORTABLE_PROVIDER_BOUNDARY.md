# v0.4 Portable Provider Boundary

**Version**: 0.4.0
**Status**: Documented

---

## Purpose

Define which provider workflows are included and excluded from v0.4 portable artifacts,
and what secret handling, logging, and offline behavior applies.

---

## Provider Workflows Included

The following workflows are included in v0.4 portable artifacts:

- Text provider mock workflow (dry_run mode)
- Text provider readiness check (all prerequisites reported as unsatisfied)
- Image provider mock workflow (mock_image mode)
- Image provider readiness check (all prerequisites reported as unsatisfied)
- Video provider mock workflow (mock_video mode)
- Video provider readiness check (all prerequisites reported as unsatisfied)
- Source and packaging safety scans
- Redacted provider logs and prompt run history

---

## Provider Workflows Excluded

The following workflows are explicitly excluded:

- Provider SDKs (OpenAI, Anthropic, Google, Runway, Kling, Pika, Luma, Replicate, Stability)
- Bundled API keys
- Real image provider execution
- Real video provider execution
- Real text provider execution (network)
- Media upload to providers
- Database for provider state
- Plugin execution
- Media decoding (ffmpeg, PIL, cv2, moviepy)
- OS keyring integration
- Background workers

---

## Text Provider Boundary

In v0.4 portable artifacts:
- Text provider dry_run mode is enabled (no network)
- Real text execution via network is blocked by default
- All real-text prerequisites are unsatisfied
- No provider SDK is bundled
- `urllib.request` is allowed for future gated use but blocked by gate

---

## Image Provider Boundary

In v0.4 portable artifacts:
- Image provider mock mode is enabled (`mock://image/<id>` URIs returned)
- Real image execution is blocked by default
- All real-image prerequisites are unsatisfied
- No image generation occurs
- No image files are written
- No PIL/cv2/moviepy imports

---

## Video Provider Boundary

In v0.4 portable artifacts:
- Video provider mock mode is enabled (`mock://video/<id>` URIs returned)
- Real video execution is blocked by default
- All real-video prerequisites are unsatisfied
- No video generation occurs
- No video files are written
- No ffmpeg/subprocess/PIL/cv2/moviepy imports

---

## Secret Handling

- API keys are not stored in any artifact
- Secrets are call-time only (passed at invocation, not persisted)
- Redaction utilities are bundled and active
- Secret-like fields are redacted in logs and run history

---

## Logs/History

- Provider logs and prompt run history are in-memory only
- No log files are written to disk by default in v0.4
- Redaction is applied before any log content is displayed
- No secrets appear in log output

---

## Offline Behavior

- All mock workflows function offline (no network required)
- Readiness checks function offline (all prerequisites reported as unsatisfied)
- Safety scan functions offline
- Real provider execution is blocked regardless of network availability

---

## Known Limitations

- Real execution requires future implementation of secret storage and gate unlocking
- Portable artifact creation (ZIP) is not scripted in v0.4 — manual packaging only
- Log persistence to disk is not implemented in v0.4

---

*Aurora Studio v0.4 — TASK-000124*
