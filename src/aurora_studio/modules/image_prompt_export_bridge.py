"""Image prompt export bridge for Aurora Studio v0.4.

Connects prompt export artifacts and templates to the mock image provider workflow.
No network calls. No image generation. No image files. Standard library only.
Real image execution blocked. Mock always available.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.image_provider import ImageProviderRequest, ImageProviderResponse
from aurora_studio.modules.mock_image_provider_adapter import MockImageProviderAdapter


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_request_id() -> str:
    return str(uuid.uuid4())


class ImagePromptExportBridge:
    """Bridge between prompt export system and the image provider adapter.

    All execution is mock only in v0.4.
    No network. No image generation. No file creation. No secrets.
    """

    def __init__(self) -> None:
        self._adapter = MockImageProviderAdapter()
        self._runs: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Core builder methods
    # ------------------------------------------------------------------

    def build_image_prompt_from_export(
        self, export_artifact_id: str
    ) -> str:
        """Retrieve prompt text from an export artifact (stub in v0.4).

        In v0.4, returns a safe placeholder prompt referencing the artifact.
        Does not read binary data or local files.
        """
        if not export_artifact_id or not export_artifact_id.strip():
            return "[no export artifact id]"
        return f"[Image prompt from export artifact: {export_artifact_id}]"

    def build_image_prompt_from_template(
        self,
        source_type: str,
        source_id: str,
        template_id: str | None = None,
        profile_id: str | None = None,
    ) -> str:
        """Build prompt text from source template/profile metadata (stub in v0.4).

        Returns a safe text prompt. Does not process media or binary data.
        """
        parts = [f"source_type={source_type}", f"source_id={source_id}"]
        if template_id:
            parts.append(f"template_id={template_id}")
        if profile_id:
            parts.append(f"profile_id={profile_id}")
        return f"[Image prompt from template: {', '.join(parts)}]"

    def create_image_provider_request_from_prompt(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict[str, Any] | None = None,
        source_type: str = "",
        source_id: str = "",
        template_id: str | None = None,
        profile_id: str | None = None,
    ) -> ImageProviderRequest:
        """Build an ImageProviderRequest from a prompt string."""
        params_raw = parameters or {}
        params_tuple = tuple(params_raw.items())
        return ImageProviderRequest(
            request_id=_make_request_id(),
            provider_id=provider_id,
            mode="mock_image",
            prompt_text=prompt_text,
            negative_prompt_text=negative_prompt_text,
            model=model or "",
            parameters=params_tuple,
            source_type=source_type,
            source_id=source_id,
            profile_id=profile_id or "",
            template_id=template_id or "",
            output_artifact_type="mock_image_result",
        )

    # ------------------------------------------------------------------
    # Run methods
    # ------------------------------------------------------------------

    def run_mock_image_from_export(
        self,
        provider_id: str,
        export_artifact_id: str,
        model: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run mock image from a prompt export artifact. No network, no image file."""
        prompt_text = self.build_image_prompt_from_export(export_artifact_id)
        request = self.create_image_provider_request_from_prompt(
            provider_id=provider_id,
            prompt_text=prompt_text,
            model=model,
            parameters=parameters,
            source_type="export_artifact",
            source_id=export_artifact_id,
        )
        response = self._adapter.execute_mock(request)
        result = self._build_result(request, response, source="export")
        self._runs.append(result)
        return result

    def run_mock_image_from_template(
        self,
        provider_id: str,
        source_type: str,
        source_id: str,
        template_id: str | None = None,
        profile_id: str | None = None,
        model: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run mock image from template/profile metadata. No network, no image file."""
        prompt_text = self.build_image_prompt_from_template(
            source_type, source_id, template_id, profile_id
        )
        request = self.create_image_provider_request_from_prompt(
            provider_id=provider_id,
            prompt_text=prompt_text,
            model=model,
            parameters=parameters,
            source_type=source_type,
            source_id=source_id,
            template_id=template_id,
            profile_id=profile_id,
        )
        response = self._adapter.execute_mock(request)
        result = self._build_result(request, response, source="template")
        self._runs.append(result)
        return result

    def run_mock_image_from_prompt(
        self,
        provider_id: str,
        prompt_text: str,
        negative_prompt_text: str = "",
        model: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run mock image directly from prompt text. No network, no image file."""
        request = self.create_image_provider_request_from_prompt(
            provider_id=provider_id,
            prompt_text=prompt_text,
            negative_prompt_text=negative_prompt_text,
            model=model,
            parameters=parameters,
        )
        response = self._adapter.execute_mock(request)
        result = self._build_result(request, response, source="prompt")
        self._runs.append(result)
        return result

    def list_image_provider_runs(
        self,
        provider_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List in-memory image provider runs. Ephemeral — cleared on restart."""
        runs = self._runs
        if provider_id:
            runs = [r for r in runs if r.get("provider_id") == provider_id]
        if status:
            runs = [r for r in runs if r.get("status") == status]
        return runs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_result(
        self,
        request: ImageProviderRequest,
        response: ImageProviderResponse,
        source: str = "prompt",
    ) -> dict[str, Any]:
        """Build a safe, JSON-serializable result dict. No secrets, no image bytes."""
        return {
            "request_id": request.request_id,
            "provider_id": request.provider_id,
            "mode": request.mode,
            "source": source,
            "prompt_preview": request.prompt_text[:120],
            "negative_prompt_preview": request.negative_prompt_text[:80],
            "model": request.model,
            "status": response.status,
            "image_uri": response.image_uri,
            "response_id": response.response_id,
            "mock_response": response.mock_response,
            "network_call": response.network_call,
            "error_message": response.error_message,
            "created_at": response.created_at,
        }
