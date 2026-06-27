"""Timeline contract placeholders and first minimal Timeline record contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

TIMELINE_STATE_DRAFT = "draft"
TIMELINE_STATE_ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TimelineRef:
    """Lightweight Timeline reference contract."""

    timeline_id: str
    title: str = ""


@dataclass(frozen=True)
class TimelineItem:
    """Minimal Timeline item contract.

    Represents a reference to a Scene or Shot placed on a Timeline.
    It does not own Scene or Shot data.
    """

    item_id: str
    item_type: str
    target_id: str
    order_index: int = 0


@dataclass(frozen=True)
class TimelineRecord:
    """Minimal Timeline record contract.

    This is the first controlled implementation contract for Timeline Manager.
    It is not a final Timeline schema.
    """

    timeline_id: str
    project_id: str
    title: str
    items: tuple[TimelineItem, ...] = ()
    state: str = TIMELINE_STATE_DRAFT
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None

    def to_ref(self) -> TimelineRef:
        """Return lightweight Timeline reference."""

        return TimelineRef(timeline_id=self.timeline_id, title=self.title)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable Timeline record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "TimelineRecord":
        """Return a new Timeline record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimelineRecord":
        """Create a Timeline record from JSON-like data."""

        required = ("timeline_id", "project_id", "title", "state", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Timeline record missing required keys: {', '.join(missing)}")

        raw_items = data.get("items", [])
        items = tuple(
            TimelineItem(
                item_id=str(item["item_id"]),
                item_type=str(item["item_type"]),
                target_id=str(item["target_id"]),
                order_index=int(item.get("order_index", 0)),
            )
            for item in raw_items
        )

        return cls(
            timeline_id=str(data["timeline_id"]),
            project_id=str(data["project_id"]),
            title=str(data["title"]),
            items=items,
            state=str(data["state"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
        )
