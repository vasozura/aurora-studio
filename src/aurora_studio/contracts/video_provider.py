"""Video provider request/response contracts for Aurora Studio v0.4.

Frozen dataclasses only. No network. No video/audio bytes. No base64 media.
No file upload. No secrets. Standard library only.

TASK-000117
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Forbidden parameter keys — blocked at validation time
# ---------------------------------------------------------------------------

FORBIDDEN_PARAMETER_KEYS: frozenset[str] = frozenset({
    "video_bytes",
    "video_base64",
    "image_bytes",
    "image_base64",
    "audio_bytes",
    "audio_base64",
    "mask_base64",
    "reference_video_base64",
    "reference_image_base64",
    "upload_file",
    "file_path",
    "asset_binary",
    "api_key",
    "token",
    "secret",
    "password",
})

# Allowed execution modes
VIDEO_PROVIDER_MODES: frozenset[str] = frozenset({
    "mock_video",
    "real_video",
    "blocked_real_video",
})

# Allowed response statuses
VIDEO_PROVIDER_STATUSES: frozenset[str] = frozenset({
    "mock",
    "success",
    "failed",
    "blocked",
    "queued",
    "invalid_request",
})


# ---------------------------------------------------------------------------
# VideoProviderRequest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VideoProviderRequest:
    """Immutable video provider request.

    No video/audio/image bytes. No base64 media. No file upload. No secrets.
    """

    request_id: str
    provider_id: str
    mode: str
    prompt_text: str
    negative_prompt_text: str = ""
    model: str = ""
    parameters: tuple[tuple[str, Any], ...] = ()
    source_type: str = ""
    source_id: str = ""
    profile_id: str = ""
    template_id: str = ""
    output_artifact_type: str = "mock_video_result"
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
            "parameters": list(self.parameters),
            "source_type": self.source_type,
            "source_id": self.source_id,
            "profile_id": self.profile_id,
            "template_id": self.template_id,
            "output_artifact_type": self.output_artifact_type,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


# ---------------------------------------------------------------------------
# VideoProviderResponse
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VideoProviderResponse:
    """Immutable video provider response.

    No video bytes. No base64. raw_response_preview is truncated.
    """

    response_id: str
    request_id: str
    provider_id: str
    mode: str
    status: str
    artifact_id: str = ""
    video_uri: str = ""       # mock://video/<id> in mock mode
    job_id: str = ""          # mock job ID in mock mode
    output_text: str = ""
    raw_response_preview: str = ""   # truncated, no secrets, no binary
    usage: tuple[tuple[str, Any], ...] = ()
    error_message: str = ""
    network_call: bool = False
    mock_response: bool = False
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "mode": self.mode,
            "status": self.status,
            "artifact_id": self.artifact_id,
            "video_uri": self.video_uri,
            "job_id": self.job_id,
            "output_text": self.output_text,
            "raw_response_preview": self.raw_response_preview[:200],
            "usage": list(self.usage),
            "error_message": self.error_message,
            "network_call": self.network_call,
            "mock_response": self.mock_response,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
