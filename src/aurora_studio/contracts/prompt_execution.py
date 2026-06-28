"""Prompt execution contracts for Aurora Studio v0.3.

No provider SDK. No network calls. No secrets.
Standard library dataclasses only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUEUE_STATUSES = frozenset({
    "queued", "running", "completed", "failed", "blocked", "cancelled",
})

BATCH_STATUSES = frozenset({"completed", "partial", "failed"})

RUN_TYPES = frozenset({"dry_run", "batch_export", "manual_export"})

RUN_STATUSES = frozenset({
    "completed", "failed", "blocked", "partial", "cancelled", "dry_run",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Prompt execution request
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PromptExecutionRequest:
    """A request to execute a prompt against a provider."""

    request_id: str
    project_id: str
    provider_id: str
    source_type: str
    source_id: str
    prompt_text: str
    profile_id: str = ""
    template_id: str = ""
    parameters: dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "project_id": self.project_id,
            "provider_id": self.provider_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "prompt_text": self.prompt_text,
            "profile_id": self.profile_id,
            "template_id": self.template_id,
            "parameters": dict(self.parameters),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "PromptExecutionRequest":
        return cls(
            request_id=str(data["request_id"]),
            project_id=str(data.get("project_id", "")),
            provider_id=str(data["provider_id"]),
            source_type=str(data["source_type"]),
            source_id=str(data["source_id"]),
            prompt_text=str(data["prompt_text"]),
            profile_id=str(data.get("profile_id", "")),
            template_id=str(data.get("template_id", "")),
            parameters=dict(data.get("parameters") or {}),
            created_at=str(data.get("created_at", "")),
        )


# ---------------------------------------------------------------------------
# Queue item
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PromptExecutionQueueItem:
    """A single item in the local prompt execution queue."""

    queue_item_id: str
    request_id: str
    project_id: str
    provider_id: str
    source_type: str
    source_id: str
    status: str = "queued"
    priority: int = 0
    attempt_count: int = 0
    max_attempts: int = 1
    created_at: str = ""
    updated_at: str = ""
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "PromptExecutionQueueItem":
        return cls(
            queue_item_id=str(data["queue_item_id"]),
            request_id=str(data["request_id"]),
            project_id=str(data.get("project_id", "")),
            provider_id=str(data["provider_id"]),
            source_type=str(data["source_type"]),
            source_id=str(data["source_id"]),
            status=str(data.get("status", "queued")),
            priority=int(data.get("priority", 0)),
            attempt_count=int(data.get("attempt_count", 0)),
            max_attempts=int(data.get("max_attempts", 1)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            error_message=str(data.get("error_message", "")),
        )


# ---------------------------------------------------------------------------
# Queue status summary
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PromptExecutionQueueStatus:
    """Summary snapshot of the queue state."""

    total: int
    queued: int
    running: int
    completed: int
    failed: int
    blocked: int
    cancelled: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Batch prompt export
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BatchPromptExportRequest:
    """A request to batch-export prompts for multiple sources."""

    batch_id: str
    project_id: str
    source_type: str
    source_ids: tuple[str, ...]
    template_id: str = ""
    profile_id: str = ""
    artifact_type: str = "prompt"
    provider_target: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "project_id": self.project_id,
            "source_type": self.source_type,
            "source_ids": list(self.source_ids),
            "template_id": self.template_id,
            "profile_id": self.profile_id,
            "artifact_type": self.artifact_type,
            "provider_target": self.provider_target,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "BatchPromptExportRequest":
        return cls(
            batch_id=str(data["batch_id"]),
            project_id=str(data.get("project_id", "")),
            source_type=str(data["source_type"]),
            source_ids=tuple(str(x) for x in data.get("source_ids", [])),
            template_id=str(data.get("template_id", "")),
            profile_id=str(data.get("profile_id", "")),
            artifact_type=str(data.get("artifact_type", "prompt")),
            provider_target=str(data.get("provider_target", "")),
            created_at=str(data.get("created_at", "")),
        )


@dataclass(frozen=True)
class BatchPromptExportItemResult:
    """Result for a single item in a batch export."""

    source_id: str
    status: str
    artifact_id: str = ""
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BatchPromptExportResult:
    """Result of a complete batch export operation."""

    batch_id: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    items: tuple[BatchPromptExportItemResult, ...]
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "status": self.status,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "items": [i.to_dict() for i in self.items],
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Prompt run history
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PromptRunHistoryRecord:
    """A sanitized history record for a prompt execution event."""

    run_id: str
    project_id: str
    run_type: str
    provider_id: str
    source_type: str
    source_id: str
    profile_id: str = ""
    template_id: str = ""
    status: str = "completed"
    prompt_preview: str = ""
    output_preview: str = ""
    artifact_id: str = ""
    queue_item_id: str = ""
    batch_id: str = ""
    error_message: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "PromptRunHistoryRecord":
        return cls(
            run_id=str(data["run_id"]),
            project_id=str(data.get("project_id", "")),
            run_type=str(data.get("run_type", "dry_run")),
            provider_id=str(data.get("provider_id", "")),
            source_type=str(data.get("source_type", "")),
            source_id=str(data.get("source_id", "")),
            profile_id=str(data.get("profile_id", "")),
            template_id=str(data.get("template_id", "")),
            status=str(data.get("status", "completed")),
            prompt_preview=str(data.get("prompt_preview", "")),
            output_preview=str(data.get("output_preview", "")),
            artifact_id=str(data.get("artifact_id", "")),
            queue_item_id=str(data.get("queue_item_id", "")),
            batch_id=str(data.get("batch_id", "")),
            error_message=str(data.get("error_message", "")),
            created_at=str(data.get("created_at", "")),
        )
