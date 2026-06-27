"""Asset Manager first minimal implementation."""

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


class AssetManager:
    """Minimal Asset Manager implementation.

    This class manages only in-memory Asset records.

    It does not implement:
    - File inspection on disk
    - Image, video or audio loading
    - Asset metadata extraction
    - Provider integration
    - Plugin execution
    - Database persistence
    - GUI behavior
    """

    module_name = "Asset Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._assets: dict[str, AssetRecord] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Asset Manager supports minimal in-memory Asset records "
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
        """Register an Asset reference in memory.

        This does not inspect actual files on disk.
        """

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        clean_asset_type = self._validate_required_ref(asset_type, "asset_type")
        clean_display_name = self._validate_required_ref(display_name, "display_name")
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
        """List Asset records, optionally filtered by project or type."""

        assets = list(self._assets.values())

        if project_id is not None:
            clean_project_id = self._validate_required_ref(project_id, "project_id")
            assets = [a for a in assets if a.project_id == clean_project_id]

        if asset_type is not None:
            clean_asset_type = self._validate_required_ref(asset_type, "asset_type")
            assets = [a for a in assets if a.asset_type == clean_asset_type]

        return assets

    def get_asset(self, asset_id: str) -> AssetRecord:
        """Return an Asset record by ID."""

        clean_asset_id = self._validate_required_ref(asset_id, "asset_id")
        try:
            return self._assets[clean_asset_id]
        except KeyError as exc:
            raise ValidationError(f"Asset not found: {clean_asset_id}") from exc

    def update_asset(
        self,
        asset_id: str,
        *,
        display_name: str | None = None,
        location: str | None = None,
        owner_ref: str | None = None,
    ) -> AssetRecord:
        """Update minimal Asset-owned fields."""

        asset = self.get_asset(asset_id)
        changes: dict = {"modified_at": utc_now_iso()}

        if display_name is not None:
            changes["display_name"] = self._validate_required_ref(display_name, "display_name")

        if location is not None:
            changes["location"] = location.strip()

        if owner_ref is not None:
            changes["owner_ref"] = owner_ref.strip() if owner_ref.strip() else None

        updated = asset.with_updates(**changes)
        self._assets[updated.asset_id] = updated
        return updated

    def mark_asset_missing(self, asset_id: str) -> AssetRecord:
        """Mark an Asset as missing by state."""

        asset = self.get_asset(asset_id)
        updated = asset.with_updates(state=ASSET_STATE_MISSING, modified_at=utc_now_iso())
        self._assets[updated.asset_id] = updated
        return updated

    def archive_asset(self, asset_id: str) -> AssetRecord:
        """Archive an Asset record. The record is preserved."""

        asset = self.get_asset(asset_id)
        now = utc_now_iso()
        archived = asset.with_updates(
            state=ASSET_STATE_ARCHIVED,
            modified_at=now,
            archived_at=now,
        )
        self._assets[archived.asset_id] = archived
        return archived

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def replace_assets(self, records: list) -> None:
        """Replace in-memory asset store. Used by bundle rehydration.

        Accepts only AssetRecord instances. Does not change module readiness.
        """

        from aurora_studio.contracts.asset import AssetRecord as _AssetRecord
        for item in records:
            if not isinstance(item, _AssetRecord):
                raise ValidationError("replace_assets requires AssetRecord instances.")
        self._assets = {r.asset_id: r for r in records}
