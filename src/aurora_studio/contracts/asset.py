"""Asset contract placeholders and first minimal Asset record contract."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

ASSET_STATE_ACTIVE = "active"
ASSET_STATE_MISSING = "missing"
ASSET_STATE_ARCHIVED = "archived"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AssetRef:
    """Placeholder Asset reference contract."""

    asset_id: str
    asset_type: str
    display_name: str = ""


@dataclass(frozen=True)
class AssetRecord:
    """Minimal Asset record contract.

    This is the first controlled implementation contract for Asset Manager.
    It is not a final Asset schema.
    """

    asset_id: str
    project_id: str
    asset_type: str
    display_name: str
    location: str = ""
    state: str = ASSET_STATE_ACTIVE
    owner_ref: str | None = None
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None

    def to_ref(self) -> AssetRef:
        """Return lightweight Asset reference."""

        return AssetRef(asset_id=self.asset_id, asset_type=self.asset_type, display_name=self.display_name)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable Asset record."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "AssetRecord":
        """Return a new Asset record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetRecord":
        """Create an Asset record from JSON-like data."""

        required = ("asset_id", "project_id", "asset_type", "display_name", "state", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Asset record missing required keys: {', '.join(missing)}")

        return cls(
            asset_id=str(data["asset_id"]),
            project_id=str(data["project_id"]),
            asset_type=str(data["asset_type"]),
            display_name=str(data["display_name"]),
            location=str(data.get("location", "")),
            state=str(data["state"]),
            owner_ref=None if data.get("owner_ref") is None else str(data["owner_ref"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
        )
