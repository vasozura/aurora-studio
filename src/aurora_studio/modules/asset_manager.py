"""Asset Manager — v0.2 adds update_asset_metadata, tags, description, notes."""

from __future__ import annotations

from aurora_studio.contracts.asset import (
    ASSET_STATE_ACTIVE,
    ASSET_STATE_ARCHIVED,
    ASSET_STATE_MISSING,
    AssetRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness

_METADATA_FIELDS = frozenset({
    "description", "tags", "usage_count", "notes",
})


def parse_tags(tags_text: str) -> tuple[str, ...]:
    """Parse a comma-separated tags string into a cleaned tuple."""
    if not tags_text or not tags_text.strip():
        return ()
    return tuple(t.strip() for t in tags_text.split(",") if t.strip())


class AssetManager:
    """Asset Manager — in-memory only. No file inspection, no providers."""

    module_name = "Asset Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._assets: dict[str, AssetRecord] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
        return (
            "Asset Manager supports in-memory Asset records with v0.2 metadata fields "
            "and remains not ready for full product implementation."
        )

    def import_asset(
        self,
        project_id: str,
        asset_type: str,
        display_name: str,
        location: str = "",
        owner_ref: str | None = None,
    ) -> AssetRecord:
        clean_project_id = self._req(project_id, "project_id")
        clean_asset_type = self._req(asset_type, "asset_type")
        clean_display_name = self._req(display_name, "display_name")
        now = utc_now_iso()

        asset = AssetRecord(
            asset_id=new_id("asset"),
            project_id=clean_project_id,
            asset_type=clean_asset_type,
            display_name=clean_display_name,
            location=location.strip(),
            state=ASSET_STATE_ACTIVE,
            owner_ref=owner_ref.strip() if owner_ref is not None else None,
            created_at=now,
            modified_at=now,
        )
        self._assets[asset.asset_id] = asset
        return asset

    def list_assets(
        self,
        project_id: str | None = None,
        asset_type: str | None = None,
    ) -> list[AssetRecord]:
        assets = list(self._assets.values())
        if project_id is not None:
            pid = self._req(project_id, "project_id")
            assets = [a for a in assets if a.project_id == pid]
        if asset_type is not None:
            atype = self._req(asset_type, "asset_type")
            assets = [a for a in assets if a.asset_type == atype]
        return assets

    def get_asset(self, asset_id: str) -> AssetRecord:
        clean = self._req(asset_id, "asset_id")
        try:
            return self._assets[clean]
        except KeyError as exc:
            raise ValidationError(f"Asset not found: {clean}") from exc

    def update_asset(
        self,
        asset_id: str,
        *,
        display_name: str | None = None,
        location: str | None = None,
        owner_ref: str | None = None,
    ) -> AssetRecord:
        """Backward-compatible minimal update."""
        asset = self.get_asset(asset_id)
        changes: dict = {"modified_at": utc_now_iso()}
        if display_name is not None:
            changes["display_name"] = self._req(display_name, "display_name")
        if location is not None:
            changes["location"] = location.strip()
        if owner_ref is not None:
            changes["owner_ref"] = owner_ref.strip() if owner_ref.strip() else None
        updated = asset.with_updates(**changes)
        self._assets[updated.asset_id] = updated
        return updated

    def update_asset_metadata(self, asset_id: str, **fields) -> AssetRecord:
        """Update v0.2 metadata fields plus display_name, location, owner_ref, asset_type."""
        allowed = _METADATA_FIELDS | {"display_name", "location", "owner_ref", "asset_type"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValidationError(f"Unknown asset metadata fields: {', '.join(sorted(unknown))}")

        asset = self.get_asset(asset_id)
        changes: dict = {"modified_at": utc_now_iso()}

        for key, val in fields.items():
            if key == "display_name":
                changes["display_name"] = self._req(str(val), "display_name")
            elif key == "asset_type":
                changes["asset_type"] = self._req(str(val), "asset_type")
            elif key == "location":
                changes["location"] = str(val).strip()
            elif key == "owner_ref":
                sv = str(val).strip() if val is not None else ""
                changes["owner_ref"] = sv if sv else None
            elif key == "description":
                changes["description"] = str(val)
            elif key == "tags":
                if isinstance(val, str):
                    changes["tags"] = parse_tags(val)
                else:
                    changes["tags"] = tuple(str(t) for t in val)
            elif key == "usage_count":
                try:
                    uc = int(val)
                except (TypeError, ValueError):
                    raise ValidationError("usage_count must be an integer.")
                if uc < 0:
                    raise ValidationError("usage_count must not be negative.")
                changes["usage_count"] = uc
            elif key == "notes":
                changes["notes"] = str(val)

        updated = asset.with_updates(**changes)
        self._assets[updated.asset_id] = updated
        return updated

    def mark_asset_missing(self, asset_id: str) -> AssetRecord:
        asset = self.get_asset(asset_id)
        updated = asset.with_updates(state=ASSET_STATE_MISSING, modified_at=utc_now_iso())
        self._assets[updated.asset_id] = updated
        return updated

    # Convenience aliases required by TASK-000056
    def mark_missing(self, asset_id: str) -> AssetRecord:
        return self.mark_asset_missing(asset_id)

    def archive_asset(self, asset_id: str) -> AssetRecord:
        asset = self.get_asset(asset_id)
        now = utc_now_iso()
        archived = asset.with_updates(
            state=ASSET_STATE_ARCHIVED, modified_at=now, archived_at=now,
        )
        self._assets[archived.asset_id] = archived
        return archived

    def archive(self, asset_id: str) -> AssetRecord:
        return self.archive_asset(asset_id)

    def _req(self, value: str, field_name: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean

    def replace_assets(self, records: list) -> None:
        from aurora_studio.contracts.asset import AssetRecord as _AssetRecord
        for item in records:
            if not isinstance(item, _AssetRecord):
                raise ValidationError("replace_assets requires AssetRecord instances.")
        self._assets = {r.asset_id: r for r in records}
    # ------------------------------------------------------------------
    # TASK-000092: Media reference metadata hardening
    # ------------------------------------------------------------------

    def update_media_reference_metadata(self, asset_id: str, **fields) -> AssetRecord:
        """Update media metadata fields. Never opens or decodes files."""
        from aurora_studio.contracts.asset import MEDIA_KINDS, PREVIEW_STATUSES
        asset = self.get_asset(asset_id)
        allowed = {
            "media_kind", "mime_hint", "extension_hint", "size_hint_bytes",
            "checksum_hint", "external_ref", "preview_status", "preview_error",
        }
        changes: dict = {}
        for key, val in fields.items():
            if key not in allowed:
                continue
            if key == "media_kind":
                changes[key] = val if val in MEDIA_KINDS else "unknown"
            elif key == "preview_status":
                changes[key] = val if val in PREVIEW_STATUSES else "not_generated"
            elif key == "size_hint_bytes":
                if val is None:
                    changes[key] = None
                else:
                    v = int(val)
                    if v < 0:
                        raise ValueError("size_hint_bytes must be non-negative.")
                    changes[key] = v
            else:
                changes[key] = str(val)
        updated = asset.with_updates(**changes)
        self._assets[asset_id] = updated
        return updated

    def infer_extension_hint_from_location(self, asset_id: str) -> str:
        """Derive extension_hint from location path string only. No file open."""
        import os
        asset = self.get_asset(asset_id)
        if asset.location:
            _, ext = os.path.splitext(asset.location)
            hint = ext.lstrip(".").lower()
        else:
            hint = ""
        self._assets[asset_id] = asset.with_updates(extension_hint=hint)
        return hint

    def set_preview_status(self, asset_id: str, preview_status: str, preview_error: str = "") -> AssetRecord:
        """Set preview_status and optional error. No file inspection."""
        from aurora_studio.contracts.asset import PREVIEW_STATUSES
        asset = self.get_asset(asset_id)
        safe_status = preview_status if preview_status in PREVIEW_STATUSES else "not_generated"
        updated = asset.with_updates(preview_status=safe_status, preview_error=str(preview_error))
        self._assets[asset_id] = updated
        return updated

