"""Batch prompt export for Aurora Studio v0.3.

Renders prompts locally for multiple sources and creates export artifacts.
No provider calls. No network. No dry-run execution unless explicitly requested.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.prompt_execution import (
    BatchPromptExportItemResult,
    BatchPromptExportRequest,
    BatchPromptExportResult,
)
from aurora_studio.core.errors import ValidationError


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_batch_id() -> str:
    return f"batch-{uuid.uuid4().hex[:12]}"


class BatchPromptExportManager:
    """Handles batch prompt export across multiple sources.

    Uses existing template/profile/export infrastructure.
    No external provider calls. No network.
    """

    def validate_batch_request(self, request: BatchPromptExportRequest) -> list[str]:
        """Return a list of validation errors (empty list = valid)."""
        errors: list[str] = []
        if not request.source_type.strip():
            errors.append("source_type must not be empty.")
        if not request.source_ids:
            errors.append("source_ids must not be empty.")
        if not request.template_id.strip() and not request.profile_id.strip():
            errors.append("Either template_id or profile_id must be provided.")
        return errors

    def render_batch(
        self,
        request: BatchPromptExportRequest,
        template_manager: Any = None,
        profile_manager: Any = None,
    ) -> dict[str, str]:
        """Render prompt text for each source_id. Returns {source_id: rendered_text}."""
        results: dict[str, str] = {}
        for source_id in request.source_ids:
            rendered = self._render_one(
                request=request,
                source_id=source_id,
                template_manager=template_manager,
                profile_manager=profile_manager,
            )
            results[source_id] = rendered
        return results

    def _render_one(
        self,
        request: BatchPromptExportRequest,
        source_id: str,
        template_manager: Any = None,
        profile_manager: Any = None,
    ) -> str:
        """Render a prompt for a single source_id."""
        context = {
            "source_type": request.source_type,
            "source_id": source_id,
            "batch_id": request.batch_id,
            "project_id": request.project_id,
        }

        # Try profile first, then template, then fallback
        if request.profile_id and profile_manager is not None:
            try:
                result = profile_manager.render_with_profile(
                    request.profile_id, context
                )
                return result if isinstance(result, str) else str(result)
            except Exception:
                pass  # Fall through to template

        if request.template_id and template_manager is not None:
            try:
                return template_manager.render_template(request.template_id, context)
            except Exception:
                pass  # Fall through to default

        # Default: plain context render
        return (
            f"[{request.source_type.upper()}] {source_id}\n"
            f"Project: {request.project_id or 'default'}\n"
            f"Batch: {request.batch_id}\n"
            f"Provider target: {request.provider_target or 'none'}"
        )

    def create_export_artifacts_for_batch(
        self,
        request: BatchPromptExportRequest,
        export_manager: Any,
        template_manager: Any = None,
        profile_manager: Any = None,
    ) -> BatchPromptExportResult:
        """Render and create export artifacts for all sources in a batch."""
        errors = self.validate_batch_request(request)
        if errors:
            items = tuple(
                BatchPromptExportItemResult(
                    source_id=sid,
                    status="failed",
                    error_message="; ".join(errors),
                )
                for sid in request.source_ids
            )
            return BatchPromptExportResult(
                batch_id=request.batch_id,
                status="failed",
                total_count=len(request.source_ids),
                success_count=0,
                failed_count=len(request.source_ids),
                items=items,
                created_at=_utc_now(),
            )

        rendered = self.render_batch(request, template_manager, profile_manager)

        item_results: list[BatchPromptExportItemResult] = []
        success_count = 0
        failed_count = 0

        for source_id in request.source_ids:
            prompt_text = rendered.get(source_id, "")
            if not prompt_text.strip():
                item_results.append(BatchPromptExportItemResult(
                    source_id=source_id,
                    status="failed",
                    error_message="Rendered prompt was empty.",
                ))
                failed_count += 1
                continue
            try:
                artifact = export_manager.create_export_artifact(
                    source_id=source_id,
                    artifact_type=request.artifact_type or "prompt",
                    content=prompt_text,
                    provider_target=request.provider_target or None,
                    project_id=request.project_id,
                    source_type=request.source_type,
                    profile_id=request.profile_id,
                    template_id=request.template_id,
                )
                item_results.append(BatchPromptExportItemResult(
                    source_id=source_id,
                    status="completed",
                    artifact_id=artifact.artifact_id,
                ))
                success_count += 1
            except Exception as exc:
                item_results.append(BatchPromptExportItemResult(
                    source_id=source_id,
                    status="failed",
                    error_message=str(exc),
                ))
                failed_count += 1

        if success_count == 0:
            overall_status = "failed"
        elif failed_count > 0:
            overall_status = "partial"
        else:
            overall_status = "completed"

        return BatchPromptExportResult(
            batch_id=request.batch_id,
            status=overall_status,
            total_count=len(request.source_ids),
            success_count=success_count,
            failed_count=failed_count,
            items=tuple(item_results),
            created_at=_utc_now(),
        )
