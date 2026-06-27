"""Character contract placeholders and first minimal Character record contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

CHARACTER_STATE_ACTIVE = "active"
CHARACTER_STATE_ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CharacterRef:
    """Placeholder Character reference contract."""

    character_id: str
    display_name: str = ""


@dataclass(frozen=True)
class CharacterRecord:
    """Minimal Character record contract.

    This is the first controlled implementation contract for Character Manager.
    It is not a final Character schema.
    """

    character_id: str
    project_id: str
    display_name: str
    description: str = ""
    reference_asset_ids: tuple[str, ...] = ()
    state: str = CHARACTER_STATE_ACTIVE
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None

    def to_ref(self) -> CharacterRef:
        """Return lightweight Character reference."""

        return CharacterRef(character_id=self.character_id, display_name=self.display_name)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable Character record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "CharacterRecord":
        """Return a new Character record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterRecord":
        """Create a Character record from JSON-like data."""

        required = ("character_id", "project_id", "display_name", "state", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Character record missing required keys: {', '.join(missing)}")

        return cls(
            character_id=str(data["character_id"]),
            project_id=str(data["project_id"]),
            display_name=str(data["display_name"]),
            description=str(data.get("description", "")),
            reference_asset_ids=tuple(str(a) for a in data.get("reference_asset_ids", [])),
            state=str(data["state"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
        )
