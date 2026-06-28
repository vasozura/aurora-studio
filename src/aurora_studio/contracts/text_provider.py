"""Text provider request/response contracts for Aurora Studio v0.4.

No provider SDK imports. No network calls. Standard library only.
Ephemeral secrets only — no secret may be persisted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEXT_PROVIDER_REQUEST_STATUSES: frozenset[str] = frozenset({
    "pending",
    "validated",
    "invalid",
    "blocked",
})

TEXT_PROVIDER_RESPONSE_STATUSES: frozenset[str] = frozenset({
    "success",
    "error",
    "blocked",
    "mock",
    "dry_run",
    "timeout",
    "invalid_request",
})

TEXT_PROVIDER_EXECUTION_MODES: frozenset[str] = frozenset({
    "dry_run",
    "mock",
    "real_text",
    "blocked_real",
})

# Maximum prompt length enforced by validation
MAX_PROMPT_LENGTH: int = 32_000
# Maximum supported temperature range
TEMPERATURE_RANGE: tuple[float, float] = (0.0, 2.0)
# Maximum tokens
MAX_TOKEN_LIMIT: int = 32_768

VALIDATION_ERRORS: frozenset[str] = frozenset({
    "prompt_empty",
    "prompt_too_long",
    "provider_id_missing",
    "temperature_out_of_range",
    "max_tokens_out_of_range",
    "execution_mode_invalid",
    "model_id_missing",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# TextProviderRequest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TextProviderRequest:
    """A request to a text provider adapter.

    Secrets must NOT be embedded here; pass ephemeral secrets via the
    ephemeral_secret_ref field (a reference only, never the actual value).
    """

    provider_id: str
    prompt: str
    model_id: str = ""
    execution_mode: str = "dry_run"
    max_tokens: int = 512
    temperature: float = 0.7
    system_prompt: str = ""
    stop_sequences: tuple[str, ...] = ()
    extra_params: tuple[tuple[str, str], ...] = ()
    # ephemeral_secret_ref is a label/reference only — NEVER store actual key here
    ephemeral_secret_ref: str = ""
    request_id: str = ""
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict. ephemeral_secret_ref is included but should be a reference."""
        return {
            "provider_id": self.provider_id,
            "prompt": self.prompt,
            "model_id": self.model_id,
            "execution_mode": self.execution_mode,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
            "stop_sequences": list(self.stop_sequences),
            "extra_params": [list(kv) for kv in self.extra_params],
            "ephemeral_secret_ref": self.ephemeral_secret_ref,
            "request_id": self.request_id,
            "created_at": self.created_at,
        }

    def to_safe_dict(self) -> dict[str, Any]:
        """Serialize to dict with ephemeral_secret_ref redacted."""
        d = self.to_dict()
        d["ephemeral_secret_ref"] = "<redacted>" if self.ephemeral_secret_ref else ""
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_safe_dict())

    @classmethod
    def from_dict(cls, data: Any) -> "TextProviderRequest":
        return cls(
            provider_id=str(data.get("provider_id", "")),
            prompt=str(data.get("prompt", "")),
            model_id=str(data.get("model_id", "")),
            execution_mode=str(data.get("execution_mode", "dry_run")),
            max_tokens=int(data.get("max_tokens", 512)),
            temperature=float(data.get("temperature", 0.7)),
            system_prompt=str(data.get("system_prompt", "")),
            stop_sequences=tuple(data.get("stop_sequences", [])),
            extra_params=tuple(
                tuple(kv) for kv in data.get("extra_params", [])
            ),
            ephemeral_secret_ref=str(data.get("ephemeral_secret_ref", "")),
            request_id=str(data.get("request_id", "")),
            created_at=str(data.get("created_at", _utc_now())),
        )


# ---------------------------------------------------------------------------
# TextProviderResponse
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TextProviderResponse:
    """A response from a text provider adapter."""

    provider_id: str
    request_id: str
    status: str
    text: str = ""
    model_id: str = ""
    execution_mode: str = "dry_run"
    finish_reason: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    error_message: str = ""
    mock_response: bool = False
    network_call: bool = False
    latency_ms: int = 0
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "request_id": self.request_id,
            "status": self.status,
            "text": self.text,
            "model_id": self.model_id,
            "execution_mode": self.execution_mode,
            "finish_reason": self.finish_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "error_message": self.error_message,
            "mock_response": self.mock_response,
            "network_call": self.network_call,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Any) -> "TextProviderResponse":
        return cls(
            provider_id=str(data.get("provider_id", "")),
            request_id=str(data.get("request_id", "")),
            status=str(data.get("status", "error")),
            text=str(data.get("text", "")),
            model_id=str(data.get("model_id", "")),
            execution_mode=str(data.get("execution_mode", "dry_run")),
            finish_reason=str(data.get("finish_reason", "")),
            input_tokens=int(data.get("input_tokens", 0)),
            output_tokens=int(data.get("output_tokens", 0)),
            error_message=str(data.get("error_message", "")),
            mock_response=bool(data.get("mock_response", False)),
            network_call=bool(data.get("network_call", False)),
            latency_ms=int(data.get("latency_ms", 0)),
            created_at=str(data.get("created_at", _utc_now())),
        )
