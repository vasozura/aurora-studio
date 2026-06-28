"""Video provider adapter base class for Aurora Studio v0.4.

No network calls. No video generation. No video files. No provider SDKs.
No PIL/cv2/moviepy. Standard library only.

TASK-000117
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.video_provider import (
    FORBIDDEN_PARAMETER_KEYS,
    VIDEO_PROVIDER_MODES,
    VideoProviderRequest,
    VideoProviderResponse,
)
from aurora_studio.modules.provider_secret_redaction import redact_secret


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


_REAL_BLOCKED_REASON = (
    "Real video provider execution is blocked in Aurora Studio v0.4. "
    "No video generation is implemented. Use mock_video mode."
)

_MAX_PREVIEW_LEN = 200


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_video_provider_request(request: VideoProviderRequest) -> list[str]:
    """Return list of validation error codes. Empty list = valid."""
    errors: list[str] = []
    if not getattr(request, "prompt_text", "").strip():
        errors.append("prompt_empty")
    if len(getattr(request, "prompt_text", "")) > 32_000:
        errors.append("prompt_too_long")
    if not getattr(request, "provider_id", "").strip():
        errors.append("provider_id_missing")
    mode = getattr(request, "mode", "")
    if mode not in VIDEO_PROVIDER_MODES:
        errors.append("execution_mode_invalid")
    # Check parameters for forbidden keys
    params = dict(getattr(request, "parameters", ()))
    forbidden_found = FORBIDDEN_PARAMETER_KEYS & set(params.keys())
    if forbidden_found:
        errors.append("forbidden_parameter_keys")
    return errors


def validate_video_provider_parameters(parameters: dict[str, Any]) -> list[str]:
    """Validate parameters dict. Returns list of error codes."""
    errors: list[str] = []
    if not isinstance(parameters, dict):
        errors.append("parameters_not_dict")
        return errors
    forbidden_found = FORBIDDEN_PARAMETER_KEYS & set(parameters.keys())
    if forbidden_found:
        errors.append("forbidden_parameter_keys")
    # All values must be JSON-serializable
    try:
        json.dumps(parameters)
    except (TypeError, ValueError):
        errors.append("parameters_not_serializable")
    return errors


def _sanitize_response_preview(preview: str, max_len: int = _MAX_PREVIEW_LEN) -> str:
    """Truncate preview and redact obvious secrets."""
    preview = redact_secret(str(preview))
    return preview[:max_len]


# ---------------------------------------------------------------------------
# Base adapter
# ---------------------------------------------------------------------------

class VideoProviderAdapter:
    """Base video provider adapter.

    All real execution is blocked. Subclasses implement execute_mock().
    No network calls. No video files. No provider SDKs. No secrets stored.
    """

    def supports(self, provider_id: str) -> bool:
        return False

    def build_request(
        self,
        prompt_text: str,
        provider_id: str,
        mode: str = "mock_video",
        *,
        negative_prompt_text: str = "",
        model: str = "",
        parameters: dict[str, Any] | None = None,
        source_type: str = "",
        source_id: str = "",
        profile_id: str = "",
        template_id: str = "",
    ) -> VideoProviderRequest:
        params_raw = parameters or {}
        params_tuple = tuple(params_raw.items())
        return VideoProviderRequest(
            request_id=_make_id(),
            provider_id=provider_id,
            mode=mode,
            prompt_text=prompt_text,
            negative_prompt_text=negative_prompt_text,
            model=model,
            parameters=params_tuple,
            source_type=source_type,
            source_id=source_id,
            profile_id=profile_id,
            template_id=template_id,
        )

    def execute(
        self,
        request: VideoProviderRequest,
        secret_value: str = "",
    ) -> VideoProviderResponse:
        mode = getattr(request, "mode", "mock_video")
        if mode == "mock_video":
            return self.execute_mock(request)
        # real_video and blocked_real_video are always blocked
        return self._block(request)

    def execute_mock(self, request: VideoProviderRequest) -> VideoProviderResponse:
        """Override in subclass. Base returns a minimal mock response."""
        errors = validate_video_provider_request(request)
        if errors:
            return VideoProviderResponse(
                response_id=_make_id(),
                request_id=getattr(request, "request_id", ""),
                provider_id=getattr(request, "provider_id", ""),
                mode=getattr(request, "mode", "mock_video"),
                status="invalid_request",
                error_message=f"Validation errors: {errors}",
            )
        return VideoProviderResponse(
            response_id=_make_id(),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode="mock_video",
            status="mock",
            video_uri=f"mock://video/{request.request_id}",
            job_id=f"mock-job-{request.request_id}",
            mock_response=True,
            network_call=False,
        )

    def execute_real_video(
        self,
        request: VideoProviderRequest,
        secret_value: str,
    ) -> VideoProviderResponse:
        """Always blocked in base class."""
        return self._block(request)

    def _block(self, request: VideoProviderRequest) -> VideoProviderResponse:
        return VideoProviderResponse(
            response_id=_make_id(),
            request_id=getattr(request, "request_id", ""),
            provider_id=getattr(request, "provider_id", ""),
            mode=getattr(request, "mode", "blocked_real_video"),
            status="blocked",
            error_message=_REAL_BLOCKED_REASON,
            network_call=False,
        )

    def sanitize_response_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return a safe copy — no secrets, no binary, truncated preview."""
        safe: dict[str, Any] = {}
        for k, v in payload.items():
            if k in FORBIDDEN_PARAMETER_KEYS:
                continue
            if k == "raw_response_preview":
                safe[k] = _sanitize_response_preview(str(v))
            else:
                safe[k] = redact_secret(str(v)) if isinstance(v, str) else v
        return safe
