"""Asset contract — v0.2 expanded with metadata fields."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

ASSET_STATE_ACTIVE = "active"
ASSET_STATE_MISSING = "missing"
ASSET_STATE_ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# Media metadata constants (TASK-000092)
# ---------------------------------------------------------------------------

MEDIA_KINDS = frozenset({
    "image", "video", "audio", "document", "text", "reference", "unknown", "other",
})

PREVIEW_STATUSES = frozenset({
    "not_supported", "not_generated", "planned", "error", "disabled",
})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AssetRef:
    asset_id: str
    asset_type: str
    display_name: str = ""


@dataclass(frozen=True)
class AssetRecord:
    """Asset record contract — v0.2 adds description, tags, usage_count, notes."""

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
    # v0.2 metadata fields
    description: str = ""
    tags: tuple[str, ...] = ()
    usage_count: int = 0
    notes: str = ""
    # v0.3 media reference metadata (TASK-000092) — metadata hints only, no file inspection
    media_kind: str = "unknown"
    mime_hint: str = ""
    extension_hint: str = ""
    size_hint_bytes: int | None = None
    checksum_hint: str = ""
    external_ref: str = ""
    preview_status: str = "not_generated"
    preview_error: str = ""

    def to_ref(self) -> AssetRef:
        return AssetRef(asset_id=self.asset_id, asset_type=self.asset_type, display_name=self.display_name)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(d["tags"])
        return d

    def with_updates(self, **changes: Any) -> "AssetRecord":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetRecord":
        required = ("asset_id", "project_id", "asset_type", "display_name", "state", "created_at", "modified_at")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Asset record missing required keys: {', '.join(missing)}")

        try:
            usage_count = int(data.get("usage_count", 0))
        except (TypeError, ValueError):
            usage_count = 0

        size_hint_bytes = data.get("size_hint_bytes")
        if size_hint_bytes is not None:
            try:
                size_hint_bytes = int(size_hint_bytes)
                if size_hint_bytes < 0:
                    size_hint_bytes = None
            except (TypeError, ValueError):
                size_hint_bytes = None

        raw_media_kind = str(data.get("media_kind", "unknown"))
        media_kind = raw_media_kind if raw_media_kind in MEDIA_KINDS else "unknown"

        raw_preview_status = str(data.get("preview_status", "not_generated"))
        preview_status = raw_preview_status if raw_preview_status in PREVIEW_STATUSES else "not_generated"

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
            description=str(data.get("description", "")),
            tags=tuple(str(t) for t in data.get("tags", [])),
            usage_count=usage_count,
            notes=str(data.get("notes", "")),
            media_kind=media_kind,
            mime_hint=str(data.get("mime_hint", "")),
            extension_hint=str(data.get("extension_hint", "")),
            size_hint_bytes=size_hint_bytes,
            checksum_hint=str(data.get("checksum_hint", "")),
            external_ref=str(data.get("external_ref", "")),
            preview_status=preview_status,
            preview_error=str(data.get("preview_error", "")),
        )
