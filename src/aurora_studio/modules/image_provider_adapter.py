"""Image provider adapter base class and validation helpers for Aurora Studio v0.4.

No provider SDK. No network calls. No image generation. No image files.
Standard library only. Real execution blocked by default.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.image_provider import (
    FORBIDDEN_PARAMETER_KEYS,
    IMAGE_PROVIDER_MODES,
    MAX_IMAGE_PROMPT_LENGTH,
    ImageProviderRequest,
    ImageProviderResponse,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_image_provider_request(request: ImageProviderRequest) -> list[str]:
    """Validate an ImageProviderRequest. Returns list of error codes."""
    errors: list[str] = []

    if not request.provider_id or not request.provider_id.strip():
        errors.append("provider_id_missing")

    if not request.prompt_text or not request.prompt_text.strip():
        errors.append("prompt_empty")
    elif len(request.prompt_text) > MAX_IMAGE_PROMPT_LENGTH:
        errors.append("prompt_too_long")

    if request.mode not in IMAGE_PROVIDER_MODES:
        errors.append("mode_invalid")

    # Check parameters for forbidden keys and JSON-serializability
    params = request.parameters_as_dict()
    param_errors = validate_image_provider_parameters(params)
    errors.extend(param_errors)

    return errors


def validate_image_provider_parameters(parameters: dict[str, Any]) -> list[str]:
    """Validate image provider parameters. Returns list of error codes."""
    errors: list[str] = []

    if not isinstance(parameters, dict):
        errors.append("parameters_not_serializable")
        return errors

    for key in parameters:
        if key.lower() in FORBIDDEN_PARAMETER_KEYS:
            errors.append("parameters_contain_forbidden_key")
            break

    try:
        json.dumps(parameters)
    except (TypeError, ValueError):
        errors.append("parameters_not_serializable")

    return errors


def _sanitize_response_preview(preview: str, max_len: int = 200) -> str:
    """Truncate and sanitize a raw provider response preview."""
    if not preview:
        return ""
    sanitized = preview[:max_len]
    if len(preview) > max_len:
        sanitized += "...[truncated]"
    return sanitized


# ---------------------------------------------------------------------------
# ImageProviderAdapter base class
# ---------------------------------------------------------------------------

class ImageProviderAdapter:
    """Abstract-style base class for image provider adapters.

    Subclasses must implement execute_mock() and optionally execute_real_image().
    Base class always blocks real execution.
    No network calls. No image generation. No image files.
    """

    provider_id: str = ""
    provider_name: str = ""
    supports_real_image: bool = False

    def supports(self, provider_id: str) -> bool:
        return bool(provider_id and provider_id.strip())

    def build_request(
        self,
        prompt_text: str,
        provider_id: str,
        mode: str = "mock_image",
        **kwargs: Any,
    ) -> ImageProviderRequest:
        """Build an ImageProviderRequest from prompt text and kwargs."""
        params_raw = kwargs.pop("parameters", {})
        if isinstance(params_raw, dict):
            parameters = tuple(params_raw.items())
        else:
            parameters = tuple(params_raw)

        return ImageProviderRequest(
            request_id=str(uuid.uuid4()),
            provider_id=provider_id,
            mode=mode,
            prompt_text=prompt_text,
            negative_prompt_text=kwargs.get("negative_prompt_text", ""),
            model=kwargs.get("model", ""),
            parameters=parameters,
            source_type=kwargs.get("source_type", ""),
            source_id=kwargs.get("source_id", ""),
            profile_id=kwargs.get("profile_id", ""),
            template_id=kwargs.get("template_id", ""),
            output_artifact_type=kwargs.get("output_artifact_type", "mock_image_result"),
        )

    def execute(
        self,
        request: ImageProviderRequest,
        secret_value: str = "",
    ) -> ImageProviderResponse:
        """Route execution by mode."""
        mode = request.mode

        if mode == "mock_image":
            return self.execute_mock(request)

        if mode == "real_image":
            return ImageProviderResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                provider_id=request.provider_id,
                mode="real_image",
                status="blocked",
                error_message="Real image execution is blocked by the provider gate in v0.4.",
                network_call=False,
                created_at=_utc_now(),
            )

        # blocked_real_image or unknown
        return ImageProviderResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode=mode,
            status="blocked",
            error_message=f"Image execution mode '{mode}' is blocked or unsupported.",
            network_call=False,
            created_at=_utc_now(),
        )

    def execute_mock(self, request: ImageProviderRequest) -> ImageProviderResponse:
        """Mock execution. Subclasses should override for provider-specific behavior."""
        errors = validate_image_provider_request(request)
        if errors:
            return ImageProviderResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                provider_id=request.provider_id,
                mode=request.mode,
                status="invalid_request",
                error_message="; ".join(errors),
                mock_response=True,
                network_call=False,
                created_at=_utc_now(),
            )
        return ImageProviderResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode="mock_image",
            status="mock",
            image_uri=f"mock://image/{request.request_id}",
            mock_response=True,
            network_call=False,
            created_at=_utc_now(),
        )

    def execute_real_image(
        self,
        request: ImageProviderRequest,
        secret_value: str,
    ) -> ImageProviderResponse:
        """Real image execution. Base class always returns blocked.

        Subclasses must override this. Real execution requires gate approval.
        secret_value used call-time only — never stored.
        """
        return ImageProviderResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode="real_image",
            status="blocked",
            error_message=(
                "Real image execution is not implemented in the base adapter. "
                "Subclass and implement execute_real_image()."
            ),
            network_call=False,
            created_at=_utc_now(),
        )

    def sanitize_response_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Sanitize a raw response payload: remove secrets, truncate preview."""
        safe: dict[str, Any] = {}
        for k, v in payload.items():
            if k.lower() in {"api_key", "secret", "token", "authorization", "password"}:
                safe[k] = "<redacted>"
            elif k == "raw_response_preview" and isinstance(v, str):
                safe[k] = _sanitize_response_preview(v)
            elif k in {"image_bytes", "image_base64", "mask_base64", "reference_image_base64"}:
                safe[k] = "<image data removed>"
            else:
                safe[k] = v
        return safe
