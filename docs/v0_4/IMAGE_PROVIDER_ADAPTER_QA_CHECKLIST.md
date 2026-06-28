# Image Provider Adapter QA Checklist — Aurora Studio v0.4

> Companion to `IMAGE_PROVIDER_SAFETY_BOUNDARY.md`.
> All items must pass before any image provider adapter ships in v0.4.

---

## 1. Execution Mode Gate

- [ ] `execute_mock()` always returns `status="mock"` regardless of input.
- [ ] `execute_real_image()` always returns `status="blocked"` in v0.4 base class.
- [ ] `MockImageProviderAdapter.execute(mode="real_image", ...)` returns `status="blocked"`.
- [ ] `MockImageProviderAdapter.execute(mode="blocked_real_image", ...)` returns `status="blocked"`.
- [ ] `ImageProviderExecutionGate.evaluate_real_image()` never returns `allowed=True` in v0.4.
- [ ] `is_real_execution_allowed()` is hardcoded to `False` in gate.

## 2. No Network in Automated Tests

- [ ] All test files import no `requests`, `httpx`, `aiohttp`, `urllib.request` at module level.
- [ ] All `execute_mock()` calls set `network_call=False` in the response.
- [ ] No test file triggers an outbound HTTP connection.

## 3. No Image Files Created

- [ ] `execute_mock()` creates no `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, or `.tiff` files.
- [ ] No image bytes are written to disk, temp, or `/tmp`.
- [ ] `image_uri` is always `mock://image/<request_id>` scheme — never a file URI.

## 4. No Binary Payload in Request or Response

- [ ] `ImageProviderRequest` has no fields for `image_bytes`, `image_base64`, `mask_base64`, `reference_image_base64`.
- [ ] `FORBIDDEN_PARAMETER_KEYS` blocks binary/secret keys from `parameters` tuple.
- [ ] `validate_image_provider_request()` rejects requests containing forbidden parameter keys.
- [ ] `ImageProviderResponse` has no field for raw image bytes.
- [ ] `raw_response_preview` is truncated to 200 characters max.

## 5. No Secrets Stored or Logged

- [ ] No adapter stores `secret_value` on `self`.
- [ ] No adapter writes secrets to JSON, logs, or autosave files.
- [ ] `sanitize_error()` redacts secrets from error messages.
- [ ] `sanitize_response_payload()` strips forbidden keys from dicts.
- [ ] Response `to_dict()` excludes `api_key`, `token`, `secret`, `password` keys.

## 6. Contract Integrity

- [ ] `ImageProviderRequest` is `@dataclass(frozen=True)`.
- [ ] `ImageProviderResponse` is `@dataclass(frozen=True)`.
- [ ] Both `to_dict()` and `to_json()` are JSON-serializable.
- [ ] All new fields use default values for backward compatibility.

## 7. Forbidden Imports in Source

- [ ] `src/aurora_studio/**/*.py` contains no `import PIL`.
- [ ] `src/aurora_studio/**/*.py` contains no `import cv2`.
- [ ] `src/aurora_studio/**/*.py` contains no `import moviepy`.
- [ ] `src/aurora_studio/**/*.py` contains no `import requests`.
- [ ] `src/aurora_studio/**/*.py` contains no `import httpx`.
- [ ] `src/aurora_studio/**/*.py` contains no `import aiohttp`.

## 8. Provider Registry

- [ ] `mock-image` provider is registered at startup with `provider_type="image"`.
- [ ] `mock-image` provider has `requires_api_key=False`.
- [ ] `dry-run-local` provider is still registered.

## 9. CLI / UI Surface

- [ ] `image-provider-mock` CLI command exits 0 and returns JSON with `status="mock"`.
- [ ] `image-provider-readiness` CLI command exits 0 and returns `real_image_execution_ready=false`.
- [ ] `UISession.run_mock_image_from_prompt()` returns `ok=True`.
- [ ] `UISession.evaluate_image_provider_real_readiness()` returns `real_image_execution_ready=False`.

---

*QA sign-off required before v0.4 image provider goes into integration.*
