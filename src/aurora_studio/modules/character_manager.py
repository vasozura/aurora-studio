"""Character Manager — v0.2 adds detail fields and structured references (TASK-000058/059)."""

from __future__ import annotations

from aurora_studio.contracts.character import (
    CHARACTER_STATE_ACTIVE,
    CHARACTER_STATE_ARCHIVED,
    REFERENCE_TYPES,
    CharacterRecord,
    CharacterReference,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness

_DETAIL_FIELDS = frozenset({
    "role", "visual_description", "personality", "motivation",
    "conflict", "arc_notes", "notes",
})


class CharacterManager:
    """Character Manager — in-memory only. No face recognition. No providers."""

    module_name = "Character Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._characters: dict[str, CharacterRecord] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
        return (
            "Character Manager supports in-memory Character records with v0.2 detail fields "
            "and remains not ready for full product implementation."
        )

    def create_character(
        self,
        project_id: str,
        display_name: str,
        description: str = "",
    ) -> CharacterRecord:
        clean_project_id = self._req(project_id, "project_id")
        clean_display_name = self._req(display_name, "display_name")
        now = utc_now_iso()

        character = CharacterRecord(
            character_id=new_id("character"),
            project_id=clean_project_id,
            display_name=clean_display_name,
            description=description.strip(),
            reference_asset_ids=(),
            state=CHARACTER_STATE_ACTIVE,
            created_at=now,
            modified_at=now,
        )
        self._characters[character.character_id] = character
        return character

    def list_characters(self, project_id: str | None = None) -> list[CharacterRecord]:
        if project_id is None:
            return list(self._characters.values())
        pid = self._req(project_id, "project_id")
        return [c for c in self._characters.values() if c.project_id == pid]

    def get_character(self, character_id: str) -> CharacterRecord:
        clean = self._req(character_id, "character_id")
        try:
            return self._characters[clean]
        except KeyError as exc:
            raise ValidationError(f"Character not found: {clean}") from exc

    def update_character(
        self,
        character_id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
    ) -> CharacterRecord:
        """Backward-compatible minimal update."""
        character = self.get_character(character_id)
        changes: dict = {"modified_at": utc_now_iso()}
        if display_name is not None:
            changes["display_name"] = self._req(display_name, "display_name")
        if description is not None:
            changes["description"] = description.strip()
        updated = character.with_updates(**changes)
        self._characters[updated.character_id] = updated
        return updated

    def update_character_details(self, character_id: str, **fields) -> CharacterRecord:
        """Update v0.2 detail fields plus display_name and description."""
        allowed = _DETAIL_FIELDS | {"display_name", "description"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValidationError(f"Unknown character detail fields: {', '.join(sorted(unknown))}")

        character = self.get_character(character_id)
        changes: dict = {"modified_at": utc_now_iso()}

        for key, val in fields.items():
            if key == "display_name":
                changes["display_name"] = self._req(str(val), "display_name")
            elif key == "description":
                changes["description"] = str(val).strip()
            else:
                changes[key] = str(val)

        updated = character.with_updates(**changes)
        self._characters[updated.character_id] = updated
        return updated

    # ------------------------------------------------------------------
    # v0.1 reference asset methods (kept for backward compat)
    # ------------------------------------------------------------------

    def add_reference_asset(self, character_id: str, asset_id: str) -> CharacterRecord:
        """Add an asset ID reference (v0.1 compat). Also adds a structured reference."""
        character = self.get_character(character_id)
        clean_asset_id = self._req(asset_id, "asset_id")

        if clean_asset_id in character.reference_asset_ids:
            return character

        updated = character.with_updates(
            reference_asset_ids=character.reference_asset_ids + (clean_asset_id,),
            modified_at=utc_now_iso(),
        )
        self._characters[updated.character_id] = updated
        return updated

    def remove_reference_asset(self, character_id: str, asset_id: str) -> CharacterRecord:
        character = self.get_character(character_id)
        clean_asset_id = self._req(asset_id, "asset_id")

        updated = character.with_updates(
            reference_asset_ids=tuple(
                a for a in character.reference_asset_ids if a != clean_asset_id
            ),
            reference_assets=tuple(
                r for r in character.reference_assets if r.asset_id != clean_asset_id
            ),
            modified_at=utc_now_iso(),
        )
        self._characters[updated.character_id] = updated
        return updated

    # ------------------------------------------------------------------
    # TASK-000059: Structured reference methods
    # ------------------------------------------------------------------

    def add_reference(
        self,
        character_id: str,
        asset_id: str,
        reference_type: str = "other",
        is_primary: bool = False,
        notes: str = "",
    ) -> CharacterRecord:
        """Add a typed structured reference."""
        character = self.get_character(character_id)
        clean_asset_id = self._req(asset_id, "asset_id")
        ref_type = reference_type.strip() or "other"
        if ref_type not in REFERENCE_TYPES:
            raise ValidationError(
                f"reference_type must be one of {sorted(REFERENCE_TYPES)}, got: {ref_type!r}")

        now = utc_now_iso()
        # Remove existing same asset+type combo to avoid duplicates
        existing = tuple(
            r for r in character.reference_assets
            if not (r.asset_id == clean_asset_id and r.reference_type == ref_type)
        )
        new_ref = CharacterReference(
            asset_id=clean_asset_id,
            reference_type=ref_type,
            is_primary=is_primary,
            notes=notes.strip(),
            created_at=now,
            updated_at=now,
        )
        # Sync reference_asset_ids
        ids = character.reference_asset_ids
        if clean_asset_id not in ids:
            ids = ids + (clean_asset_id,)

        updated = character.with_updates(
            reference_assets=existing + (new_ref,),
            reference_asset_ids=ids,
            modified_at=now,
        )
        self._characters[updated.character_id] = updated
        return updated

    def remove_reference(
        self, character_id: str, asset_id: str, reference_type: str | None = None
    ) -> CharacterRecord:
        """Remove structured reference(s). If reference_type is None, remove all for asset."""
        character = self.get_character(character_id)
        clean_asset_id = self._req(asset_id, "asset_id")

        if reference_type is None:
            remaining = tuple(r for r in character.reference_assets if r.asset_id != clean_asset_id)
            ids = tuple(i for i in character.reference_asset_ids if i != clean_asset_id)
        else:
            rt = reference_type.strip()
            remaining = tuple(
                r for r in character.reference_assets
                if not (r.asset_id == clean_asset_id and r.reference_type == rt)
            )
            # Only remove from ids if no other references for this asset
            still_has = any(r.asset_id == clean_asset_id for r in remaining)
            ids = character.reference_asset_ids if still_has else tuple(
                i for i in character.reference_asset_ids if i != clean_asset_id
            )

        updated = character.with_updates(
            reference_assets=remaining,
            reference_asset_ids=ids,
            modified_at=utc_now_iso(),
        )
        self._characters[updated.character_id] = updated
        return updated

    def mark_primary_reference(
        self, character_id: str, asset_id: str, reference_type: str = "face"
    ) -> CharacterRecord:
        """Mark one reference as primary, clear is_primary for same type."""
        character = self.get_character(character_id)
        clean_asset_id = self._req(asset_id, "asset_id")
        rt = reference_type.strip() or "face"

        now = utc_now_iso()
        updated_refs: list[CharacterReference] = []
        found = False
        for r in character.reference_assets:
            if r.reference_type == rt:
                updated_refs.append(CharacterReference(
                    asset_id=r.asset_id,
                    reference_type=r.reference_type,
                    is_primary=(r.asset_id == clean_asset_id),
                    notes=r.notes,
                    created_at=r.created_at,
                    updated_at=now,
                ))
                if r.asset_id == clean_asset_id:
                    found = True
            else:
                updated_refs.append(r)

        if not found:
            raise ValidationError(
                f"No structured reference found for asset {clean_asset_id!r} "
                f"with type {rt!r}."
            )

        updated = character.with_updates(
            reference_assets=tuple(updated_refs),
            modified_at=now,
        )
        self._characters[updated.character_id] = updated
        return updated

    def list_references(self, character_id: str) -> list[CharacterReference]:
        character = self.get_character(character_id)
        return list(character.reference_assets)

    def archive_character(self, character_id: str) -> CharacterRecord:
        character = self.get_character(character_id)
        now = utc_now_iso()
        archived = character.with_updates(
            state=CHARACTER_STATE_ARCHIVED, modified_at=now, archived_at=now,
        )
        self._characters[archived.character_id] = archived
        return archived

    # Alias
    def archive(self, character_id: str) -> CharacterRecord:
        return self.archive_character(character_id)

    def _req(self, value: str, field_name: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean

    def replace_characters(self, records: list) -> None:
        from aurora_studio.contracts.character import CharacterRecord as _CharacterRecord
        for item in records:
            if not isinstance(item, _CharacterRecord):
                raise ValidationError("replace_characters requires CharacterRecord instances.")
        self._characters = {r.character_id: r for r in records}
