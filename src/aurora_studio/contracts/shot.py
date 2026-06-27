"""Shot contract placeholders and first minimal Shot record contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

SHOT_STATE_DRAFT = "draft"
SHOT_STATE_ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ShotRef:
    """Placeholder Shot reference contract."""

    shot_id: str
    scene_id: str
    title: str = ""


@dataclass(frozen=True)
class ShotRecord:
    """Shot record contract (v0.2: expanded with cinematic detail fields).

    Backward compatible with v0.1 bundles: all new fields are optional
    with safe defaults handled by from_dict() via .get().
    """

    shot_id: str
    scene_id: str
    title: str
    purpose: str = ""
    order_index: int = 0
    state: str = SHOT_STATE_DRAFT
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None
    # v0.2 detail fields — all optional
    project_id: str = ""
    description: str = ""
    shot_type: str = ""
    camera_angle: str = ""
    camera_movement: str = ""
    framing: str = ""
    lens: str = ""
    duration_seconds: float = 0.0
    emotion_target: str = ""
    visual_focus: str = ""
    notes: str = ""

    def to_ref(self) -> ShotRef:
        """Return lightweight Shot reference."""

        return ShotRef(shot_id=self.shot_id, scene_id=self.scene_id, title=self.title)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable Shot record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "ShotRecord":
        """Return a new Shot record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ShotRecord":
        """Create a Shot record from JSON-like data.

        Required: shot_id, scene_id, title, order_index, state, created_at, modified_at.
        v0.2 detail fields are optional (safe defaults) for backward compatibility.
        """

        required = (
            "shot_id",
            "scene_id",
            "title",
            "order_index",
            "state",
            "created_at",
            "modified_at",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Shot record missing required keys: {', '.join(missing)}")

        raw_duration = data.get("duration_seconds", 0)
        try:
            duration = float(raw_duration)
        except (TypeError, ValueError):
            duration = 0.0

        return cls(
            shot_id=str(data["shot_id"]),
            scene_id=str(data["scene_id"]),
            title=str(data["title"]),
            purpose=str(data.get("purpose", "")),
            order_index=int(data["order_index"]),
            state=str(data["state"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
            project_id=str(data.get("project_id", "")),
            description=str(data.get("description", "")),
            shot_type=str(data.get("shot_type", "")),
            camera_angle=str(data.get("camera_angle", "")),
            camera_movement=str(data.get("camera_movement", "")),
            framing=str(data.get("framing", "")),
            lens=str(data.get("lens", "")),
            duration_seconds=duration,
            emotion_target=str(data.get("emotion_target", "")),
            visual_focus=str(data.get("visual_focus", "")),
            notes=str(data.get("notes", "")),
        )
