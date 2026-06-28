"""Mock image provider adapter for Aurora Studio v0.4.

Deterministic local responses. No network. No image generation. No image files.
No provider SDK. No secrets required. Standard library only.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.image_provider import ImageProviderRequest, ImageProviderResponse
from aurora_studio.modules.image_provider_adapter import ImageProviderAdapter, validate_image_provider_request

MOCK_PROVIDER_ID = "mock-image"
MOCK_PROVIDER_NAME = "Mock Image Provider (Local)"
MOCK_IMAGE_URI_TEMPLATE = "mock://image/{request_id}"
MOCK_MODEL_DEFAULT = "mock-image-v0.4"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MockImageProviderAdapter(ImageProviderAdapter):
    """Mock image provider: deterministic local results, no network, no image files.

    Returns mock://image/<request_id> as the image URI.
    No secret required. Real execution always blocked.
    """

    provider_id: str = MOCK_PROVIDER_ID
    provider_name: str = MOCK_PROVIDER_NAME
    supports_real_image: bool = False

    def supports(self, provider_id: str) -> bool:
        return str(provider_id).strip().lower() in {MOCK_PROVIDER_ID, "mock_image", "mock"}

    def execute(
        self,
        request: ImageProviderRequest,
        secret_value: str = "",
        gate_decision: Any = None,
        config: Any = None,
    ) -> ImageProviderResponse:
        """Route by mode. Mock always allowed. Real always blocked."""
        if request.mode == "mock_image":
            return self.execute_mock(request)
        return ImageProviderResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode=request.mode,
            status="blocked",
            error_message="Real image execution is blocked in mock adapter.",
            network_call=False,
            created_at=_utc_now(),
        )

    def execute_mock(self, request: ImageProviderRequest) -> ImageProviderResponse:
        """Deterministic mock response — no network, no image file, no secret."""
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

        image_uri = self.build_mock_image_uri(request)
        return self.build_mock_response(request, image_uri=image_uri)

    def build_mock_response(
        self,
        request: ImageProviderRequest,
        image_uri: str = "",
    ) -> ImageProviderResponse:
        if not image_uri:
            image_uri = self.build_mock_image_uri(request)
        return ImageProviderResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode="mock_image",
            status="mock",
            image_uri=image_uri,
            output_text=f"[Mock image result for: {request.prompt_text[:80]}]",
            raw_response_preview=f"MOCK_IMAGE:{MOCK_PROVIDER_ID}:{request.request_id}:v0.4",
            usage=(("mock_tokens", 0), ("network_call", False)),
            mock_response=True,
            network_call=False,
            created_at=_utc_now(),
        )

    def build_mock_image_uri(self, request: ImageProviderRequest) -> str:
        return MOCK_IMAGE_URI_TEMPLATE.format(request_id=request.request_id)

    def sanitize_error(self, error: Exception) -> str:
        msg = str(error)
        for forbidden in {"api_key", "secret", "token", "password", "authorization"}:
            if forbidden in msg.lower():
                msg = "<error message redacted: may contain sensitive data>"
                break
        return msg
