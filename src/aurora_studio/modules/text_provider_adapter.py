"""Text provider adapter base class and validation helpers for Aurora Studio v0.4.

No provider SDK imports. No network calls by default. Standard library only.
Real execution is blocked by default; requires gate approval and ephemeral secret.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.text_provider import (
    MAX_PROMPT_LENGTH,
    MAX_TOKEN_LIMIT,
    TEMPERATURE_RANGE,
    TEXT_PROVIDER_EXECUTION_MODES,
    VALIDATION_ERRORS,
    TextProviderRequest,
    TextProviderResponse,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_text_provider_request(request: TextProviderRequest) -> list[str]:
    """Validate a TextProviderRequest. Returns list of error codes."""
    errors: list[str] = []

    if not request.provider_id:
        errors.append("provider_id_missing")

    if not request.prompt or not request.prompt.strip():
        errors.append("prompt_empty")
    elif len(request.prompt) > MAX_PROMPT_LENGTH:
        errors.append("prompt_too_long")

    if request.execution_mode not in TEXT_PROVIDER_EXECUTION_MODES:
        errors.append("execution_mode_invalid")

    return errors


def validate_text_provider_parameters(
    max_tokens: int | None = None,
    temperature: float | None = None,
    model_id: str | None = None,
) -> list[str]:
    """Validate individual parameters independently. Returns list of error codes."""
    errors: list[str] = []

    if max_tokens is not None:
        if max_tokens <= 0 or max_tokens > MAX_TOKEN_LIMIT:
            errors.append("max_tokens_out_of_range")

    if temperature is not None:
        lo, hi = TEMPERATURE_RANGE
        if temperature < lo or temperature > hi:
            errors.append("temperature_out_of_range")

    if model_id is not None and not model_id.strip():
        errors.append("model_id_missing")

    return errors


# ---------------------------------------------------------------------------
# TextProviderAdapter base class
# ---------------------------------------------------------------------------

class TextProviderAdapter:
    """Abstract-style base class for text provider adapters.

    Subclasses must implement:
      - execute_mock(request) → TextProviderResponse
      - execute_real_text(request, ephemeral_secret) → TextProviderResponse

    execute_real_text may only be called after gate approval and requires
    an ephemeral secret passed at call time — never stored.
    """

    provider_id: str = ""
    provider_name: str = ""
    supports_real_text: bool = False

    def validate(self, request: TextProviderRequest) -> list[str]:
        """Validate the request. Returns list of error codes (empty = valid)."""
        return validate_text_provider_request(request)

    def execute_dry_run(self, request: TextProviderRequest) -> TextProviderResponse:
        """Dry-run: validate only, no text generation, no network call."""
        errors = self.validate(request)
        if errors:
            return TextProviderResponse(
                provider_id=request.provider_id,
                request_id=request.request_id or str(uuid.uuid4()),
                status="invalid_request",
                error_message="; ".join(errors),
                execution_mode="dry_run",
                network_call=False,
                created_at=_utc_now(),
            )
        return TextProviderResponse(
            provider_id=request.provider_id,
            request_id=request.request_id or str(uuid.uuid4()),
            status="dry_run",
            text="[dry-run: no text generated]",
            model_id=request.model_id,
            execution_mode="dry_run",
            network_call=False,
            created_at=_utc_now(),
        )

    def execute_mock(self, request: TextProviderRequest) -> TextProviderResponse:
        """Mock execution: deterministic local response, no network call.

        Subclasses should override for provider-specific mock output.
        """
        errors = self.validate(request)
        if errors:
            return TextProviderResponse(
                provider_id=request.provider_id,
                request_id=request.request_id or str(uuid.uuid4()),
                status="invalid_request",
                error_message="; ".join(errors),
                execution_mode="mock",
                network_call=False,
                mock_response=True,
                created_at=_utc_now(),
            )
        return TextProviderResponse(
            provider_id=request.provider_id,
            request_id=request.request_id or str(uuid.uuid4()),
            status="mock",
            text=f"MOCK_RESPONSE:{self.provider_id}:{request.model_id}:v0.4",
            model_id=request.model_id,
            execution_mode="mock",
            mock_response=True,
            network_call=False,
            created_at=_utc_now(),
        )

    def execute_real_text(
        self,
        request: TextProviderRequest,
        ephemeral_secret: str,
    ) -> TextProviderResponse:
        """Real text execution. Must only be called after gate approval.

        ephemeral_secret is used call-time only — never stored or logged.
        Subclasses must override this method.
        Base class always returns blocked.
        """
        return TextProviderResponse(
            provider_id=request.provider_id,
            request_id=request.request_id or str(uuid.uuid4()),
            status="blocked",
            error_message=(
                "Real text execution is not implemented in the base adapter. "
                "Subclass and implement execute_real_text()."
            ),
            execution_mode="real_text",
            network_call=False,
            created_at=_utc_now(),
        )

    def execute(
        self,
        request: TextProviderRequest,
        ephemeral_secret: str = "",
    ) -> TextProviderResponse:
        """Route execution by mode. Real text requires gate approval + ephemeral secret."""
        from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate

        mode = request.execution_mode

        if mode == "dry_run":
            return self.execute_dry_run(request)

        if mode == "mock":
            return self.execute_mock(request)

        if mode == "real_text":
            gate = ProviderExecutionGate()
            decision = gate.is_real_execution_allowed(request.provider_id)
            if not decision:
                return TextProviderResponse(
                    provider_id=request.provider_id,
                    request_id=request.request_id or str(uuid.uuid4()),
                    status="blocked",
                    error_message="Real text execution is blocked by the provider gate.",
                    execution_mode="real_text",
                    network_call=False,
                    created_at=_utc_now(),
                )
            if not ephemeral_secret:
                return TextProviderResponse(
                    provider_id=request.provider_id,
                    request_id=request.request_id or str(uuid.uuid4()),
                    status="blocked",
                    error_message="Real text execution requires an ephemeral secret at call time.",
                    execution_mode="real_text",
                    network_call=False,
                    created_at=_utc_now(),
                )
            return self.execute_real_text(request, ephemeral_secret)

        # blocked_real or unknown
        return TextProviderResponse(
            provider_id=request.provider_id,
            request_id=request.request_id or str(uuid.uuid4()),
            status="blocked",
            error_message=f"Execution mode '{mode}' is blocked or unsupported.",
            execution_mode=mode,
            network_call=False,
            created_at=_utc_now(),
        )
