"""Prompt run history for Aurora Studio v0.3.

Sanitized in-memory history of dry-run executions, batch exports, and manual exports.
No secrets. No full prompt storage. No network.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.prompt_execution import (
    BatchPromptExportRequest,
    BatchPromptExportResult,
    PromptExecutionRequest,
    PromptRunHistoryRecord,
    RUN_STATUSES,
    RUN_TYPES,
)
from aurora_studio.contracts.provider import ProviderRequest, ProviderResponse

_PREVIEW_MAX = 80


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_preview(text: str, max_len: int = _PREVIEW_MAX) -> str:
    """Truncate and redact secret-looking content from a text preview."""
    if not text:
        return ""
    _SECRET_PATTERNS = frozenset({
        "api_key", "apikey", "token", "bearer", "secret",
        "password", "credential", "authorization",
    })
    lines = text.splitlines()
    safe: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(pat in lower for pat in _SECRET_PATTERNS):
            safe.append("[REDACTED]")
        else:
            safe.append(line)
    result = " ".join(safe)
    # Strip control chars
    result = "".join(c if c.isprintable() or c == " " else "?" for c in result)
    if len(result) > max_len:
        result = result[:max_len] + "..."
    return result


class PromptRunHistory:
    """In-memory run history for prompt executions.

    Records sanitized previews only — no full prompt text, no secrets.
    """

    def __init__(self) -> None:
        self._records: list[PromptRunHistoryRecord] = []

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_dry_run(
        self,
        request: ProviderRequest,
        response: ProviderResponse,
        queue_item_id: str = "",
    ) -> PromptRunHistoryRecord:
        record = PromptRunHistoryRecord(
            run_id=f"run-{uuid.uuid4().hex[:12]}",
            project_id="",
            run_type="dry_run",
            provider_id=request.provider_id,
            source_type=request.source_type,
            source_id=request.source_id,
            profile_id=getattr(request, "profile_id", ""),
            template_id=getattr(request, "template_id", ""),
            status=response.status,
            prompt_preview=sanitize_preview(request.prompt_text),
            output_preview=sanitize_preview(response.output_text),
            artifact_id="",
            queue_item_id=queue_item_id,
            batch_id="",
            error_message=sanitize_preview(response.error_message),
            created_at=_utc_now(),
        )
        self._records.append(record)
        return record

    def record_batch_result(
        self,
        batch_request: BatchPromptExportRequest,
        batch_result: BatchPromptExportResult,
    ) -> list[PromptRunHistoryRecord]:
        records: list[PromptRunHistoryRecord] = []
        for item in batch_result.items:
            record = PromptRunHistoryRecord(
                run_id=f"run-{uuid.uuid4().hex[:12]}",
                project_id=batch_request.project_id,
                run_type="batch_export",
                provider_id="",
                source_type=batch_request.source_type,
                source_id=item.source_id,
                profile_id=batch_request.profile_id,
                template_id=batch_request.template_id,
                status=item.status if item.status in RUN_STATUSES else "completed",
                prompt_preview="",
                output_preview="",
                artifact_id=item.artifact_id,
                queue_item_id="",
                batch_id=batch_result.batch_id,
                error_message=sanitize_preview(item.error_message),
                created_at=_utc_now(),
            )
            self._records.append(record)
            records.append(record)
        return records

    def record_manual_export(
        self,
        source_type: str,
        source_id: str,
        artifact_id: str,
        profile_id: str = "",
        template_id: str = "",
        project_id: str = "",
    ) -> PromptRunHistoryRecord:
        record = PromptRunHistoryRecord(
            run_id=f"run-{uuid.uuid4().hex[:12]}",
            project_id=project_id,
            run_type="manual_export",
            provider_id="",
            source_type=source_type,
            source_id=source_id,
            profile_id=profile_id,
            template_id=template_id,
            status="completed",
            prompt_preview="",
            output_preview="",
            artifact_id=artifact_id,
            queue_item_id="",
            batch_id="",
            error_message="",
            created_at=_utc_now(),
        )
        self._records.append(record)
        return record

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_history(
        self,
        run_type: str | None = None,
        status: str | None = None,
        provider_id: str | None = None,
        source_type: str | None = None,
        limit: int = 200,
    ) -> list[PromptRunHistoryRecord]:
        results = list(self._records)
        if run_type is not None:
            results = [r for r in results if r.run_type == run_type]
        if status is not None:
            results = [r for r in results if r.status == status]
        if provider_id is not None:
            results = [r for r in results if r.provider_id == provider_id]
        if source_type is not None:
            results = [r for r in results if r.source_type == source_type]
        results.reverse()
        return results[:limit]

    def get_history(self, run_id: str) -> PromptRunHistoryRecord | None:
        for r in self._records:
            if r.run_id == run_id:
                return r
        return None

    def clear_history(self) -> int:
        count = len(self._records)
        self._records.clear()
        return count

    def count(self) -> int:
        return len(self._records)
