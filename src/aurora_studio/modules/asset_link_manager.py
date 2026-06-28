"""Asset Link Manager — TASK-000057.

Stores metadata links between assets and scenes/shots/characters.
All in-memory. No file inspection. No provider calls.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id

ALLOWED_TARGET_TYPES = frozenset({"scene", "shot", "character"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AssetLink:
    """Metadata link between an asset and a target (scene/shot/character)."""

    link_id: str
    project_id: str
    asset_id: str
    target_type: str
    target_id: str
    created_at: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetLink":
        required = ("link_id", "project_id", "asset_id", "target_type", "target_id", "created_at")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"AssetLink missing keys: {', '.join(missing)}")
        return cls(
            link_id=str(data["link_id"]),
            project_id=str(data["project_id"]),
            asset_id=str(data["asset_id"]),
            target_type=str(data["target_type"]),
            target_id=str(data["target_id"]),
            created_at=str(data["created_at"]),
            notes=str(data.get("notes", "")),
        )


class AssetLinkManager:
    """Manages asset↔target metadata links in memory."""

    def __init__(self) -> None:
        self._links: dict[str, AssetLink] = {}

    def link(
        self,
        project_id: str,
        asset_id: str,
        target_type: str,
        target_id: str,
        notes: str = "",
    ) -> AssetLink:
        self._validate_non_empty(asset_id, "asset_id")
        self._validate_non_empty(target_id, "target_id")
        self._validate_non_empty(target_type, "target_type")
        if target_type not in ALLOWED_TARGET_TYPES:
            raise ValidationError(
                f"target_type must be one of {sorted(ALLOWED_TARGET_TYPES)}, got: {target_type!r}")

        # Prevent duplicates
        for existing in self._links.values():
            if (existing.asset_id == asset_id and
                    existing.target_type == target_type and
                    existing.target_id == target_id):
                return existing

        link = AssetLink(
            link_id=new_id("link"),
            project_id=project_id,
            asset_id=asset_id,
            target_type=target_type,
            target_id=target_id,
            created_at=_now(),
            notes=notes,
        )
        self._links[link.link_id] = link
        return link

    def unlink(self, asset_id: str, target_type: str, target_id: str) -> bool:
        """Remove a link. Returns True if found and removed."""
        self._validate_non_empty(asset_id, "asset_id")
        self._validate_non_empty(target_id, "target_id")
        to_remove = [
            lid for lid, lnk in self._links.items()
            if lnk.asset_id == asset_id and lnk.target_type == target_type
               and lnk.target_id == target_id
        ]
        for lid in to_remove:
            del self._links[lid]
        return bool(to_remove)

    def list_links_for_target(self, target_type: str, target_id: str) -> list[AssetLink]:
        """Return all links for a given target."""
        self._validate_non_empty(target_id, "target_id")
        return [
            lnk for lnk in self._links.values()
            if lnk.target_type == target_type and lnk.target_id == target_id
        ]

    def list_links_for_asset(self, asset_id: str) -> list[AssetLink]:
        """Return all links for a given asset."""
        self._validate_non_empty(asset_id, "asset_id")
        return [lnk for lnk in self._links.values() if lnk.asset_id == asset_id]

    def list_all(self) -> list[AssetLink]:
        return list(self._links.values())

    def replace_links(self, records: list) -> None:
        """Replace store from rehydration."""
        for item in records:
            if not isinstance(item, AssetLink):
                raise ValidationError("replace_links requires AssetLink instances.")
        self._links = {r.link_id: r for r in records}

    def _validate_non_empty(self, value: str, field: str) -> str:
        v = value.strip() if isinstance(value, str) else ""
        if not v:
            raise ValidationError(f"{field} must not be empty.")
        return v
