"""Export contract placeholders and first minimal export artifact contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

EXPORT_STATUS_DRAFT = "draft"
EXPORT_STATUS_READY = "ready"
EXPORT_STATUS_FAILED = "failed"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ExportArtifactRef:
    """Placeholder export artifact reference contract.

    Export artifacts are outputs, not source meaning.
    """

    artifact_id: str
    source_id: str
    artifact_type: str


@dataclass(frozen=True)
class ExportArtifactRecord:
    """Minimal export artifact record contract.

    This is the first controlled implementation contract for Prompt Export Manager.
    It does not implement real prompt generation or provider calls.
    """

    artifact_id: str
    source_id: str
    artifact_type: str
    content: str
    status: str = EXPORT_STATUS_DRAFT
    provider_target: str | None = None
    created_at: str = ""
    modified_at: str = ""

    def to_ref(self) -> ExportArtifactRef:
        """Return lightweight export artifact reference."""

        return ExportArtifactRef(
            artifact_id=self.artifact_id,
            source_id=self.source_id,
            artifact_type=self.artifact_type,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable export artifact record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "ExportArtifactRecord":
        """Return a new record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExportArtifactRecord":
        """Create an export artifact record from JSON-like data."""

        required = ("artifact_id", "source_id", "artifact_type", "content", "status", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"ExportArtifactRecord missing required keys: {', '.join(missing)}")

        return cls(
            artifact_id=str(data["artifact_id"]),
            source_id=str(data["source_id"]),
            artifact_type=str(data["artifact_type"]),
            content=str(data["content"]),
            status=str(data["status"]),
            provider_target=None if data.get("provider_target") is None else str(data["provider_target"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
        )
