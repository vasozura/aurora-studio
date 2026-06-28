"""OpenAI-compatible text provider adapter for Aurora Studio v0.4.

Uses stdlib urllib.request for real HTTP — gated and never called in automated tests.
No openai SDK. No requests/httpx/aiohttp. Standard library only.
Real execution requires gate approval + ephemeral call-time secret + explicit confirm.
Ephemeral secret is NEVER stored, logged, or persisted.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.text_provider import (
    TextProviderRequest,
    TextProviderResponse,
)
from aurora_studio.modules.text_provider_adapter import TextProviderAdapter


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Default OpenAI-compatible base URL (can be overridden for local/compatible endpoints)
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
MOCK_TEXT_TEMPLATE = "MOCK_OPENAI_RESPONSE:{provider_id}:{model_id}:v0.4"


class OpenAICompatibleTextAdapter(TextProviderAdapter):
    """Adapter for OpenAI-compatible text APIs.

    Supports dry_run, mock, and (gated) real_text execution.
    All tests must use dry_run or mock — no real network calls in automated tests.
    """

    provider_id: str = "openai-compatible"
    provider_name: str = "OpenAI-Compatible Text Provider"
    supports_real_text: bool = True

    def __init__(
        self,
        provider_id: str = "openai-compatible",
        base_url: str = DEFAULT_BASE_URL,
        default_model: str = DEFAULT_MODEL,
    ) -> None:
        self._provider_id = provider_id
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def provider_id(self) -> str:  # type: ignore[override]
        return self._provider_id

    def execute_mock(self, request: TextProviderRequest) -> TextProviderResponse:
        """Mock execution: deterministic local response, no network call."""
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
        model = request.model_id or self.default_model
        mock_text = MOCK_TEXT_TEMPLATE.format(
            provider_id=request.provider_id,
            model_id=model,
        )
        return TextProviderResponse(
            provider_id=request.provider_id,
            request_id=request.request_id or str(uuid.uuid4()),
            status="mock",
            text=mock_text,
            model_id=model,
            execution_mode="mock",
            mock_response=True,
            network_call=False,
            finish_reason="stop",
            input_tokens=len(request.prompt.split()),
            output_tokens=len(mock_text.split()),
            created_at=_utc_now(),
        )

    def execute_real_text(
        self,
        request: TextProviderRequest,
        ephemeral_secret: str,
    ) -> TextProviderResponse:
        """Real HTTP call to OpenAI-compatible endpoint.

        ephemeral_secret is used in this call only — NEVER stored or logged.
        Only reachable after gate approval in execute().
        Not called in automated tests — monkeypatched in test suite.
        """
        if not ephemeral_secret or not ephemeral_secret.strip():
            return TextProviderResponse(
                provider_id=request.provider_id,
                request_id=request.request_id or str(uuid.uuid4()),
                status="blocked",
                error_message="No ephemeral secret provided for real text execution.",
                execution_mode="real_text",
                network_call=False,
                created_at=_utc_now(),
            )

        model = request.model_id or self.default_model
        request_id = request.request_id or str(uuid.uuid4())

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.stop_sequences:
            payload["stop"] = list(request.stop_sequences)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {ephemeral_secret}",
            "Content-Type": "application/json",
        }
        # ephemeral_secret used above and discarded — never assigned to self

        start = time.monotonic()
        try:
            import urllib.request as _urllib_request
            import urllib.error as _urllib_error

            data = json.dumps(payload).encode("utf-8")
            req = _urllib_request.Request(url, data=data, headers=headers, method="POST")
            with _urllib_request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))

            latency_ms = int((time.monotonic() - start) * 1000)
            choice = body.get("choices", [{}])[0]
            text_out = choice.get("message", {}).get("content", "")
            finish_reason = choice.get("finish_reason", "")
            usage = body.get("usage", {})

            return TextProviderResponse(
                provider_id=request.provider_id,
                request_id=request_id,
                status="success",
                text=text_out,
                model_id=model,
                execution_mode="real_text",
                finish_reason=finish_reason,
                input_tokens=int(usage.get("prompt_tokens", 0)),
                output_tokens=int(usage.get("completion_tokens", 0)),
                network_call=True,
                latency_ms=latency_ms,
                created_at=_utc_now(),
            )

        except Exception as exc:
            latency_ms = int((time.monotonic() - start) * 1000)
            # Never include ephemeral_secret in error message
            error_msg = str(exc)
            if ephemeral_secret in error_msg:
                error_msg = error_msg.replace(ephemeral_secret, "<redacted>")
            return TextProviderResponse(
                provider_id=request.provider_id,
                request_id=request_id,
                status="error",
                error_message=error_msg,
                model_id=model,
                execution_mode="real_text",
                network_call=True,
                latency_ms=latency_ms,
                created_at=_utc_now(),
            )
