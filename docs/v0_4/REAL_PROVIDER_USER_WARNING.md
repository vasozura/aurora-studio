# Real Provider Execution — User Warning

> **IMPORTANT: Real provider execution may send prompt text outside this machine.**

## What This Means

When Aurora Studio executes a prompt in **real text** mode, the content of your
prompt — including any characters, scene descriptions, or creative materials
included in the prompt — is transmitted over the internet to a third-party AI
provider (such as OpenAI's API servers).

This data transmission is subject to the privacy policy and terms of service of
the provider you have configured.

**Aurora Studio does not control, monitor, or guarantee the handling of your
data by third-party providers.**

---

## Before Enabling Real Provider Execution

1. **Read your provider's privacy policy** — understand how your prompt data
   is stored, used, and retained.

2. **Do not include sensitive personal information** in prompts sent to
   third-party providers unless you have verified the provider's data handling
   policies permit this.

3. **Do not include confidential business information** in prompts unless
   your agreement with the provider covers confidential use.

4. **API key security** — your API key authorizes charges to your account.
   Keep it secure. Aurora Studio stores no API keys persistently.

---

## Secret Handling Warning

**Do not pass API keys as command-line arguments because shell history may
retain them.**

If using a CLI or script to invoke Aurora Studio with a real provider secret,
pass the secret through an environment variable (e.g. `AURORA_PROVIDER_SECRET`),
not as a `--api-key` or `--secret` flag. Shell history files (`.bash_history`,
`.zsh_history`, and similar) may persist for months and can be read by anyone
with access to your user account or filesystem.

---

## How Real Execution Is Gated

Aurora Studio requires **all** of the following before a real provider call
can proceed:

1. Provider registered and enabled in configuration
2. Real execution explicitly requested by the caller
3. Real execution allowed in the gate configuration
4. A secret reference is available (not the actual secret — just a reference)
5. Secret storage approach approved for this provider
6. Request is text-only (no image, video, or audio)
7. Log redaction is enabled
8. Logging is verified to sanitize secrets and prompts
9. Network access is allowed for this provider
10. User has explicitly confirmed real execution
11. Secret is provided ephemerally at call time (never stored)

In Aurora Studio v0.4, real execution remains **blocked by default**. All
prerequisites must be satisfied and execution must be explicitly confirmed.

---

*Last updated: v0.4 — TASK-000110*
