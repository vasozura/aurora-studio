"""Scene contract placeholders and first minimal Scene record contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

SCENE_STATE_DRAFT = "draft"
SCENE_STATE_ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SceneRef:
    """Placeholder Scene reference contract."""

    scene_id: str
    title: str = ""


@dataclass(frozen=True)
class SceneRecord:
    """Scene record contract (v0.2: expanded with detail fields).

    Backward compatible with v0.1 bundles: all new fields are optional
    with empty-string defaults and are handled by from_dict() via .get().
    """

    scene_id: str
    project_id: str
    title: str
    purpose: str = ""
    state: str = SCENE_STATE_DRAFT
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None
    # v0.2 detail fields — all optional, default ""
    description: str = ""
    location: str = ""
    time_of_day: str = ""
    mood: str = ""
    conflict: str = ""
    narrative_beat: str = ""
    notes: str = ""

    def to_ref(self) -> SceneRef:
        """Return lightweight Scene reference."""

        return SceneRef(scene_id=self.scene_id, title=self.title)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable Scene record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "SceneRecord":
        """Return a new Scene record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneRecord":
        """Create a Scene record from JSON-like data.

        Required: scene_id, project_id, title, state, created_at, modified_at.
        v0.2 detail fields are optional (default "") for backward compatibility.
        """

        required = ("scene_id", "project_id", "title", "state", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Scene record missing required keys: {', '.join(missing)}")

        return cls(
            scene_id=str(data["scene_id"]),
            project_id=str(data["project_id"]),
            title=str(data["title"]),
            purpose=str(data.get("purpose", "")),
            state=str(data["state"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
            description=str(data.get("description", "")),
            location=str(data.get("location", "")),
            time_of_day=str(data.get("time_of_day", "")),
            mood=str(data.get("mood", "")),
            conflict=str(data.get("conflict", "")),
            narrative_beat=str(data.get("narrative_beat", "")),
            notes=str(data.get("notes", "")),
        )
