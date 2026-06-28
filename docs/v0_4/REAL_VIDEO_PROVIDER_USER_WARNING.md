# Real Video Provider — User Warning

> **Status in Aurora Studio v0.4: BLOCKED**
> Real video generation through any external provider is not available in this version.

---

## What This Means

Aurora Studio v0.4 includes a **mock-only** video provider workflow:

- Prompt text is accepted and validated locally.
- A deterministic `mock://video/<id>` URI is returned — no actual video is generated.
- No network call is made to any video provider API.
- No API key or secret is required or accepted.

---

## Future Warning — Read Before Enabling Real Execution

If real video provider execution is enabled in a future version, the following applies:

**Real video provider execution may send prompt text outside this machine.**

If reference media is supported in a future version, those files may also be sent outside this machine.

Do not send confidential, sensitive, personal, regulated, or unauthorized media.

API keys are not saved by Aurora Studio in this mode unless a future secure storage feature is explicitly enabled.

Provider costs, queue times, and terms of service are the user's responsibility. Aurora Studio does not control or monitor external provider usage, billing, content policies, or data retention.

---

## What Will Change in a Future Version

A future release (post-v0.4) may introduce real video execution subject to:

- [ ] User explicitly enables real video execution in Settings
- [ ] Provider SDK reviewed and approved by Aurora Labs
- [ ] Video safety classifier integrated (content moderation before display)
- [ ] Secure ephemeral key entry flow (no persistent storage)
- [ ] Rate limiting and cost budget controls implemented
- [ ] Video binary handling sandboxed and memory-limited
- [ ] Reference media upload gated by explicit user consent
- [ ] Full security review completed and documented
- [ ] All 15 gate prerequisites satisfied

Until all prerequisites are met, the execution gate will remain closed.

---

## What Happens If You Try

If you call a video provider with `mode="real_video"`:
- The execution gate returns `allowed=False`.
- The adapter returns `status="blocked"`.
- No network call is made.
- No key is consumed or transmitted.
- The UI surfaces: *"Real video execution is blocked in v0.4."*

---

## Safe Use in v0.4

Use the mock video workflow freely:

```
aurora video-provider-mock --provider mock-video --prompt "A sweeping aerial view"
```

This is safe, free, deterministic, and requires no credentials.

---

*Aurora Studio v0.4 — TASK-000120*
