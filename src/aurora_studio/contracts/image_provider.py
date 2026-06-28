"""Image provider request/response contracts for Aurora Studio v0.4.

No provider SDK imports. No network calls. No image bytes. Standard library only.
Real image execution blocked by default.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_PROVIDER_MODES: frozenset[str] = frozenset({
    "mock_image",
    "real_image",
    "blocked_real_image",
})

IMAGE_PROVIDER_STATUSES: frozenset[str] = frozenset({
    "mock",
    "success",
    "failed",
    "blocked",
    "invalid_request",
})

# Maximum prompt length
MAX_IMAGE_PROMPT_LENGTH: int = 4000

# Forbidden parameter keys — must never appear in image provider requests
FORBIDDEN_PARAMETER_KEYS: frozenset[str] = frozenset({
    "image_bytes",
    "image_base64",
    "mask_base64",
    "reference_image_base64",
    "upload_file",
    "file_path",
    "asset_binary",
    "api_key",
    "token",
    "secret",
    "password",
})

IMAGE_VALIDATION_ERRORS: frozenset[str] = frozenset({
    "prompt_empty",
    "prompt_too_long",
    "provider_id_missing",
    "mode_invalid",
    "parameters_not_serializable",
    "parameters_contain_forbidden_key",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# ImageProviderRequest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ImageProviderRequest:
    """A request to an image provider adapter.

    No image bytes. No base64. No file upload paths. No secrets.
    """

    request_id: str
    provider_id: str
    mode: str
    prompt_text: str
    negative_prompt_text: str = ""
    model: str = ""
    parameters: tuple[tuple[str, Any], ...] = ()  # key-value pairs, JSON-serializable
    source_type: str = ""
    source_id: str = ""
    profile_id: str = ""
    template_id: str = ""
    output_artifact_type: str = "mock_image_result"
    created_at: str = field(default_factory=_utc_now)

    def parameters_as_dict(self) -> dict[str, Any]:
        return dict(self.parameters)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "mode": self.mode,
            "prompt_text": self.prompt_text,
            "negative_prompt_text": self.negative_prompt_text,
            "model": self.model,
            "parameters": self.parameters_as_dict(),
            "source_type": self.source_type,
            "source_id": self.source_id,
            "profile_id": self.profile_id,
            "template_id": self.template_id,
            "output_artifact_type": self.output_artifact_type,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImageProviderRequest":
        params_raw = data.get("parameters", {})
        if isinstance(params_raw, dict):
            parameters = tuple(params_raw.items())
        else:
            parameters = tuple(params_raw)
        return cls(
            request_id=str(data.get("request_id", "")),
            provider_id=str(data.get("provider_id", "")),
            mode=str(data.get("mode", "mock_image")),
            prompt_text=str(data.get("prompt_text", "")),
            negative_prompt_text=str(data.get("negative_prompt_text", "")),
            model=str(data.get("model", "")),
            parameters=parameters,
            source_type=str(data.get("source_type", "")),
            source_id=str(data.get("source_id", "")),
            profile_id=str(data.get("profile_id", "")),
            template_id=str(data.get("template_id", "")),
            output_artifact_type=str(data.get("output_artifact_type", "mock_image_result")),
            created_at=str(data.get("created_at", _utc_now())),
        )


# ---------------------------------------------------------------------------
# ImageProviderResponse
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ImageProviderResponse:
    """A response from an image provider adapter.

    No image bytes. No base64. Mock URI uses mock:// scheme. No secrets.
    """

    response_id: str
    request_id: str
    provider_id: str
    mode: str
    status: str
    artifact_id: str = ""
    image_uri: str = ""          # e.g. "mock://image/<request_id>"
    output_text: str = ""
    raw_response_preview: str = ""  # truncated/sanitized preview only
    usage: tuple[tuple[str, Any], ...] = ()
    error_message: str = ""
    network_call: bool = False
    mock_response: bool = False
    created_at: str = field(default_factory=_utc_now)

    def usage_as_dict(self) -> dict[str, Any]:
        return dict(self.usage)

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "mode": self.mode,
            "status": self.status,
            "artifact_id": self.artifact_id,
            "image_uri": self.image_uri,
            "output_text": self.output_text,
            "raw_response_preview": self.raw_response_preview,
            "usage": self.usage_as_dict(),
            "error_message": self.error_message,
            "network_call": self.network_call,
            "mock_response": self.mock_response,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImageProviderResponse":
        usage_raw = data.get("usage", {})
        if isinstance(usage_raw, dict):
            usage = tuple(usage_raw.items())
        else:
            usage = tuple(usage_raw)
        return cls(
            response_id=str(data.get("response_id", "")),
            request_id=str(data.get("request_id", "")),
            provider_id=str(data.get("provider_id", "")),
            mode=str(data.get("mode", "mock_image")),
            status=str(data.get("status", "blocked")),
            artifact_id=str(data.get("artifact_id", "")),
            image_uri=str(data.get("image_uri", "")),
            output_text=str(data.get("output_text", "")),
            raw_response_preview=str(data.get("raw_response_preview", "")),
            usage=usage,
            error_message=str(data.get("error_message", "")),
            network_call=bool(data.get("network_call", False)),
            mock_response=bool(data.get("mock_response", False)),
            created_at=str(data.get("created_at", _utc_now())),
        )
