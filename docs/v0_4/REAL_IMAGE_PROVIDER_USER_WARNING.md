# Real Image Provider — User Warning

> **Status in Aurora Studio v0.4: BLOCKED**
> Real image generation through any external provider is not available in this version.

---

## What This Means

Aurora Studio v0.4 includes a **mock-only** image provider workflow:

- Prompt text is accepted and validated.
- A deterministic `mock://image/<id>` URI is returned — no actual image is generated.
- No network call is made to any image provider API.
- No API key or secret is required or accepted.

This allows you to test the prompt → image provider pipeline end-to-end without incurring API costs or transmitting data to any external service.

---

## Why Real Execution Is Blocked

Real image provider execution is blocked in v0.4 for the following reasons:

1. **No provider SDK is bundled** — Aurora Studio v0.4 uses standard library only.
2. **No image safety review pipeline** — Generated images from real providers require content review before display.
3. **No persistent key storage** — v0.4 does not store API keys securely between sessions.
4. **No rate limiting or cost controls** — Real API calls incur costs that the v0.4 budget model does not account for.
5. **No image file handling** — v0.4 does not decode, display, or store binary image data.

---

## What Will Change in a Future Version

A future release (post-v0.4) may introduce real image execution subject to:

- [ ] User explicitly enables real image execution in Settings
- [ ] Provider SDK reviewed and approved by Aurora Labs
- [ ] Image safety classifier integrated (content moderation before display)
- [ ] Secure ephemeral key entry flow (no persistent storage)
- [ ] Rate limiting and cost budget controls implemented
- [ ] Image binary handling sandboxed and memory-limited
- [ ] Full security review completed and documented

Until all prerequisites are met, the execution gate will remain closed.

---

## What Happens If You Try

If you call an image provider with `mode="real_image"`:
- The execution gate returns `allowed=False`.
- The adapter returns `status="blocked"`.
- No network call is made.
- No key is consumed or transmitted.
- The UI surfaces: *"Real image execution is blocked in v0.4."*

---

## Safe Use in v0.4

Use the mock image workflow freely:

```
aurora image-provider-mock --provider mock-image --prompt "A vibrant sunset"
```

This is safe, free, deterministic, and requires no credentials.

---

*Aurora Studio v0.4 — TASK-000115*
