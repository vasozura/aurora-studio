"""Provider dry-run adapter for Aurora Studio v0.3.

No network calls. No provider SDK. No secrets.
Accepts a ProviderRequest and returns a ProviderResponse with status="dry_run".
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from aurora_studio.contracts.provider import (
    DRY_RUN_PROVIDER_ID,
    ProviderRequest,
    ProviderResponse,
)
from aurora_studio.core.errors import ValidationError


_PREVIEW_MAX = 120
_OUTPUT_MAX = 200


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(text: str) -> str:
    """Truncate and strip control characters for safe preview logging."""
    cleaned = "".join(c if c.isprintable() or c == " " else "?" for c in text)
    return cleaned[:_PREVIEW_MAX] if len(cleaned) > _PREVIEW_MAX else cleaned


class ProviderDryRunAdapter:
    """Local dry-run adapter.

    Accepts a ProviderRequest and returns a synthetic ProviderResponse.
    Does not call any external API.
    Does not import any provider SDK.
    Does not read or write any secret.
    """

    def __init__(self, provider_id: str = DRY_RUN_PROVIDER_ID) -> None:
        self._provider_id = provider_id

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Execute a dry run. Returns immediately with a synthetic response."""
        if not request.prompt_text.strip():
            raise ValidationError("prompt_text must not be empty for dry-run execution.")

        preview = _sanitize(request.prompt_text)
        word_count = len(request.prompt_text.split())
        char_count = len(request.prompt_text)

        output_text = (
            f"[DRY-RUN] Provider: {self._provider_id}\n"
            f"Source: {request.source_type or 'unknown'}/{request.source_id or 'unknown'}\n"
            f"Prompt preview: {preview}\n"
            f"Prompt length: {char_count} chars / {word_count} words\n"
            f"Request ID: {request.request_id}\n"
            f"Status: dry_run — no network call was made."
        )
        if len(output_text) > _OUTPUT_MAX:
            output_text = output_text[:_OUTPUT_MAX] + "...[truncated]"

        return ProviderResponse(
            response_id=f"resp-{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            provider_id=self._provider_id,
            status="dry_run",
            output_text=output_text,
            created_at=_utc_now(),
        )

    @staticmethod
    def build_request(
        provider_id: str,
        source_type: str,
        source_id: str,
        prompt_text: str,
        profile_id: str = "",
        template_id: str = "",
        parameters: dict | None = None,
    ) -> ProviderRequest:
        """Helper to build a ProviderRequest with a generated request_id."""
        return ProviderRequest(
            request_id=f"req-{uuid.uuid4().hex[:12]}",
            provider_id=provider_id,
            source_type=source_type,
            source_id=source_id,
            prompt_text=prompt_text,
            profile_id=profile_id,
            template_id=template_id,
            parameters=dict(parameters or {}),
            created_at=_utc_now(),
        )
