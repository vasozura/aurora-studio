"""Project contract placeholders and first minimal project metadata contract."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

CURRENT_PROJECT_VERSION = "0.1.0"
PROJECT_FILENAME = "aurora_project.json"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectMetadata:
    """Minimal project metadata contract.

    This is the first controlled implementation contract for Project Manager.
    It is not a final project schema.
    """

    project_id: str
    title: str
    version: str = CURRENT_PROJECT_VERSION
    created_at: str = ""
    modified_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable metadata."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectMetadata":
        """Create metadata from JSON-like data."""

        required = ("project_id", "title", "version", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Project metadata missing required keys: {', '.join(missing)}")

        return cls(
            project_id=str(data["project_id"]),
            title=str(data["title"]),
            version=str(data["version"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
        )
