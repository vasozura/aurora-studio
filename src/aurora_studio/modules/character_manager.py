"""Character Manager first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.character import (
    CHARACTER_STATE_ACTIVE,
    CHARACTER_STATE_ARCHIVED,
    CharacterRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class CharacterManager:
    """Minimal Character Manager implementation.

    This class manages only in-memory Character records.

    It does not implement:
    - Asset existence validation
    - Face recognition
    - Image processing
    - Provider integration
    - Plugin execution
    - Database persistence
    - GUI behavior
    """

    module_name = "Character Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._characters: dict[str, CharacterRecord] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Character Manager supports minimal in-memory Character records "
            "and remains not ready for full product implementation."
        )

    def create_character(
        self,
        project_id: str,
        display_name: str,
        description: str = "",
    ) -> CharacterRecord:
        """Create an in-memory Character record."""

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        clean_display_name = self._validate_required_ref(display_name, "display_name")
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
        """List Character records, optionally filtered by project reference."""

        if project_id is None:
            return list(self._characters.values())

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        return [c for c in self._characters.values() if c.project_id == clean_project_id]

    def get_character(self, character_id: str) -> CharacterRecord:
        """Return a Character record by ID."""

        clean_character_id = self._validate_required_ref(character_id, "character_id")
        try:
            return self._characters[clean_character_id]
        except KeyError as exc:
            raise ValidationError(f"Character not found: {clean_character_id}") from exc

    def update_character(
        self,
        character_id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
    ) -> CharacterRecord:
        """Update minimal Character-owned fields."""

        character = self.get_character(character_id)
        changes: dict = {"modified_at": utc_now_iso()}

        if display_name is not None:
            changes["display_name"] = self._validate_required_ref(display_name, "display_name")

        if description is not None:
            changes["description"] = description.strip()

        updated = character.with_updates(**changes)
        self._characters[updated.character_id] = updated
        return updated

    def add_reference_asset(self, character_id: str, asset_id: str) -> CharacterRecord:
        """Add an Asset reference to a Character.

        This does not validate whether the Asset exists.
        Duplicate asset IDs are not added.
        """

        character = self.get_character(character_id)
        clean_asset_id = self._validate_required_ref(asset_id, "asset_id")

        if clean_asset_id in character.reference_asset_ids:
            return character

        updated = character.with_updates(
            reference_asset_ids=character.reference_asset_ids + (clean_asset_id,),
            modified_at=utc_now_iso(),
        )
        self._characters[updated.character_id] = updated
        return updated

    def remove_reference_asset(self, character_id: str, asset_id: str) -> CharacterRecord:
        """Remove an Asset reference from a Character."""

        character = self.get_character(character_id)
        clean_asset_id = self._validate_required_ref(asset_id, "asset_id")

        updated = character.with_updates(
            reference_asset_ids=tuple(a for a in character.reference_asset_ids if a != clean_asset_id),
            modified_at=utc_now_iso(),
        )
        self._characters[updated.character_id] = updated
        return updated

    def archive_character(self, character_id: str) -> CharacterRecord:
        """Archive a Character record. The record is preserved."""

        character = self.get_character(character_id)
        now = utc_now_iso()
        archived = character.with_updates(
            state=CHARACTER_STATE_ARCHIVED,
            modified_at=now,
            archived_at=now,
        )
        self._characters[archived.character_id] = archived
        return archived

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value
