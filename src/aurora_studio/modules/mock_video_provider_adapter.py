"""Mock video provider adapter for Aurora Studio v0.4.

No network. No video generation. No video files. No provider SDK.
No PIL/cv2/moviepy. No external media calls. Standard library only.

TASK-000118
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.video_provider import (
    VideoProviderRequest,
    VideoProviderResponse,
)
from aurora_studio.modules.video_provider_adapter import (
    VideoProviderAdapter,
    validate_video_provider_request,
)
from aurora_studio.modules.provider_secret_redaction import redact_secret


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


MOCK_PROVIDER_ID = "mock-video"
MOCK_VIDEO_URI_TEMPLATE = "mock://video/{request_id}"
MOCK_JOB_ID_TEMPLATE = "mock-job-{request_id}"
MOCK_MODEL_DEFAULT = "mock-video-v0.4"


class MockVideoProviderAdapter(VideoProviderAdapter):
    """Mock video adapter — deterministic, local, no network, no video file.

    Returns mock://video/<request_id> URI. No generation. No secrets required.
    """

    def supports(self, provider_id: str) -> bool:
        return provider_id in {"mock-video", "mock_video", "mock-vid"}

    def execute(
        self,
        request: VideoProviderRequest,
        secret_value: str = "",
        gate_decision: Any = None,
        config: Any = None,
    ) -> VideoProviderResponse:
        mode = getattr(request, "mode", "mock_video")
        if mode == "mock_video":
            return self.execute_mock(request)
        # real_video and blocked_real_video always blocked
        return VideoProviderResponse(
            response_id=_make_id(),
            request_id=getattr(request, "request_id", ""),
            provider_id=getattr(request, "provider_id", MOCK_PROVIDER_ID),
            mode=mode,
            status="blocked",
            error_message=(
                "Real video provider execution is blocked in Aurora Studio v0.4. "
                "Use mock_video mode."
            ),
            network_call=False,
        )

    def execute_mock(self, request: VideoProviderRequest) -> VideoProviderResponse:
        errors = validate_video_provider_request(request)
        if errors:
            return VideoProviderResponse(
                response_id=_make_id(),
                request_id=getattr(request, "request_id", ""),
                provider_id=getattr(request, "provider_id", MOCK_PROVIDER_ID),
                mode=getattr(request, "mode", "mock_video"),
                status="invalid_request",
                error_message=f"Validation errors: {errors}",
                network_call=False,
            )
        return self.build_mock_response(request)

    def build_mock_response(
        self,
        request: VideoProviderRequest,
        video_uri: str = "",
    ) -> VideoProviderResponse:
        uri = video_uri or self.build_mock_video_uri(request)
        job_id = self.build_mock_job_id(request)
        prompt_preview = getattr(request, "prompt_text", "")[:80]
        return VideoProviderResponse(
            response_id=_make_id(),
            request_id=request.request_id,
            provider_id=request.provider_id,
            mode="mock_video",
            status="mock",
            video_uri=uri,
            job_id=job_id,
            output_text=f"[Mock video result for: {prompt_preview}]",
            raw_response_preview=(
                f"MOCK_VIDEO:{request.provider_id}:{request.request_id}:v0.4"
            ),
            mock_response=True,
            network_call=False,
        )

    def build_mock_video_uri(self, request: VideoProviderRequest) -> str:
        return MOCK_VIDEO_URI_TEMPLATE.format(request_id=request.request_id)

    def build_mock_job_id(self, request: VideoProviderRequest) -> str:
        return MOCK_JOB_ID_TEMPLATE.format(request_id=request.request_id)

    def sanitize_error(self, error: Exception) -> str:
        return redact_secret(str(error))
