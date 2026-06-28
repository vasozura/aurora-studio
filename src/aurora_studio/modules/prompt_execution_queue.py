"""Local in-memory prompt execution queue for Aurora Studio v0.3.

No background workers. No threads. No database. No network calls.
"""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.prompt_execution import (
    QUEUE_STATUSES,
    PromptExecutionQueueItem,
    PromptExecutionQueueStatus,
    PromptExecutionRequest,
)
from aurora_studio.core.errors import ValidationError


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PromptExecutionQueue:
    """In-memory queue for local prompt execution requests.

    Items are stored in insertion order.
    No background execution. No threads. No async.
    """

    def __init__(self) -> None:
        self._items: dict[str, PromptExecutionQueueItem] = {}
        self._requests: dict[str, PromptExecutionRequest] = {}

    # ------------------------------------------------------------------
    # Enqueue
    # ------------------------------------------------------------------

    def enqueue_request(
        self, request: PromptExecutionRequest, priority: int = 0
    ) -> PromptExecutionQueueItem:
        if not request.provider_id.strip():
            raise ValidationError("provider_id must not be empty.")
        if not request.source_type.strip():
            raise ValidationError("source_type must not be empty.")
        if not request.prompt_text.strip():
            raise ValidationError("prompt_text must not be empty.")

        qid = f"qi-{uuid.uuid4().hex[:12]}"
        now = _utc_now()
        item = PromptExecutionQueueItem(
            queue_item_id=qid,
            request_id=request.request_id,
            project_id=request.project_id,
            provider_id=request.provider_id,
            source_type=request.source_type,
            source_id=request.source_id,
            status="queued",
            priority=priority,
            attempt_count=0,
            max_attempts=1,
            created_at=now,
            updated_at=now,
        )
        self._items[qid] = item
        self._requests[request.request_id] = request
        return item

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_items(
        self,
        status: str | None = None,
        provider_id: str | None = None,
        source_type: str | None = None,
    ) -> list[PromptExecutionQueueItem]:
        results = list(self._items.values())
        if status is not None:
            results = [r for r in results if r.status == status]
        if provider_id is not None:
            results = [r for r in results if r.provider_id == provider_id]
        if source_type is not None:
            results = [r for r in results if r.source_type == source_type]
        return results

    def get_item(self, queue_item_id: str) -> PromptExecutionQueueItem:
        if queue_item_id not in self._items:
            raise ValidationError(f"Queue item not found: {queue_item_id!r}")
        return self._items[queue_item_id]

    def get_request(self, request_id: str) -> PromptExecutionRequest:
        if request_id not in self._requests:
            raise ValidationError(f"Request not found: {request_id!r}")
        return self._requests[request_id]

    def queue_status(self) -> PromptExecutionQueueStatus:
        items = list(self._items.values())
        return PromptExecutionQueueStatus(
            total=len(items),
            queued=sum(1 for i in items if i.status == "queued"),
            running=sum(1 for i in items if i.status == "running"),
            completed=sum(1 for i in items if i.status == "completed"),
            failed=sum(1 for i in items if i.status == "failed"),
            blocked=sum(1 for i in items if i.status == "blocked"),
            cancelled=sum(1 for i in items if i.status == "cancelled"),
        )

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def _update(self, qid: str, **kwargs: Any) -> PromptExecutionQueueItem:
        item = self.get_item(qid)
        updated = replace(item, updated_at=_utc_now(), **kwargs)
        self._items[qid] = updated
        return updated

    def mark_running(self, queue_item_id: str) -> PromptExecutionQueueItem:
        return self._update(queue_item_id, status="running")

    def mark_completed(self, queue_item_id: str) -> PromptExecutionQueueItem:
        item = self.get_item(queue_item_id)
        return self._update(
            queue_item_id,
            status="completed",
            attempt_count=item.attempt_count + 1,
        )

    def mark_failed(
        self, queue_item_id: str, error_message: str = ""
    ) -> PromptExecutionQueueItem:
        item = self.get_item(queue_item_id)
        return self._update(
            queue_item_id,
            status="failed",
            attempt_count=item.attempt_count + 1,
            error_message=str(error_message),
        )

    def mark_blocked(
        self, queue_item_id: str, error_message: str = ""
    ) -> PromptExecutionQueueItem:
        return self._update(
            queue_item_id,
            status="blocked",
            error_message=str(error_message),
        )

    def cancel_item(self, queue_item_id: str) -> PromptExecutionQueueItem:
        return self._update(queue_item_id, status="cancelled")

    def clear_completed(self) -> int:
        completed = [qid for qid, i in self._items.items() if i.status == "completed"]
        for qid in completed:
            del self._items[qid]
        return len(completed)

    # ------------------------------------------------------------------
    # Optional: execute one queued item with dry-run adapter
    # ------------------------------------------------------------------

    def execute_next_with_dry_run(self, dry_run_adapter: Any) -> dict[str, Any] | None:
        """Process the next queued item using a dry-run adapter. Returns None if queue empty."""
        queued = [i for i in self._items.values() if i.status == "queued"]
        if not queued:
            return None

        # Pick highest priority (larger int = higher), then earliest
        queued.sort(key=lambda i: (-i.priority, i.created_at))
        item = queued[0]

        self.mark_running(item.queue_item_id)
        try:
            request = self.get_request(item.request_id)
            # Build a ProviderRequest from our PromptExecutionRequest
            from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
            provider_req = ProviderDryRunAdapter.build_request(
                provider_id=request.provider_id,
                source_type=request.source_type,
                source_id=request.source_id,
                prompt_text=request.prompt_text,
                profile_id=request.profile_id,
                template_id=request.template_id,
                parameters=dict(request.parameters),
            )
            response = dry_run_adapter.execute(provider_req)
            self.mark_completed(item.queue_item_id)
            return {
                "queue_item_id": item.queue_item_id,
                "request_id": item.request_id,
                "response_id": response.response_id,
                "status": "completed",
                "output_text": response.output_text,
            }
        except Exception as exc:
            self.mark_failed(item.queue_item_id, str(exc))
            return {
                "queue_item_id": item.queue_item_id,
                "request_id": item.request_id,
                "status": "failed",
                "error_message": str(exc),
            }
