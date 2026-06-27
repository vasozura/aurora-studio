"""Shot Manager first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.shot import (
    SHOT_STATE_ARCHIVED,
    SHOT_STATE_DRAFT,
    ShotRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class ShotManager:
    """Minimal Shot Manager implementation.

    This class manages only in-memory Shot records.

    It does not implement:
    - Scene creation
    - Scene existence validation
    - Timeline placement
    - Camera modeling
    - Composition modeling
    - Motion modeling
    - AFL validation
    - Prompt export
    - Database persistence
    - Provider integration
    - Plugin execution
    - GUI behavior
    """

    module_name = "Shot Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._shots: dict[str, ShotRecord] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Shot Manager supports minimal in-memory Shot records "
            "and remains not ready for full product implementation."
        )

    def create_shot(
        self,
        scene_id: str,
        title: str,
        purpose: str = "",
        order_index: int | None = None,
    ) -> ShotRecord:
        """Create an in-memory Shot record.

        This does not validate whether the parent Scene exists.
        """

        clean_scene_id = self._validate_required_ref(scene_id, "scene_id")
        clean_title = self._validate_required_ref(title, "title")
        clean_purpose = purpose.strip()
        resolved_order_index = self._resolve_order_index(clean_scene_id, order_index)
        now = utc_now_iso()

        shot = ShotRecord(
            shot_id=new_id("shot"),
            scene_id=clean_scene_id,
            title=clean_title,
            purpose=clean_purpose,
            order_index=resolved_order_index,
            state=SHOT_STATE_DRAFT,
            created_at=now,
            modified_at=now,
        )
        self._shots[shot.shot_id] = shot
        return shot

    def list_shots(self, scene_id: str | None = None) -> list[ShotRecord]:
        """List Shot records, optionally filtered by parent Scene reference."""

        shots = list(self._shots.values())

        if scene_id is not None:
            clean_scene_id = self._validate_required_ref(scene_id, "scene_id")
            shots = [shot for shot in shots if shot.scene_id == clean_scene_id]

        return sorted(shots, key=lambda shot: (shot.scene_id, shot.order_index, shot.created_at))

    def get_shot(self, shot_id: str) -> ShotRecord:
        """Return a Shot record by ID."""

        clean_shot_id = self._validate_required_ref(shot_id, "shot_id")
        try:
            return self._shots[clean_shot_id]
        except KeyError as exc:
            raise ValidationError(f"Shot not found: {clean_shot_id}") from exc

    def update_shot(
        self,
        shot_id: str,
        *,
        title: str | None = None,
        purpose: str | None = None,
    ) -> ShotRecord:
        """Update minimal Shot-owned fields."""

        shot = self.get_shot(shot_id)

        changes: dict[str, str] = {"modified_at": utc_now_iso()}

        if title is not None:
            changes["title"] = self._validate_required_ref(title, "title")

        if purpose is not None:
            changes["purpose"] = purpose.strip()

        updated = shot.with_updates(**changes)
        self._shots[updated.shot_id] = updated
        return updated

    def archive_shot(self, shot_id: str) -> ShotRecord:
        """Archive a Shot record in memory."""

        shot = self.get_shot(shot_id)
        now = utc_now_iso()
        archived = shot.with_updates(
            state=SHOT_STATE_ARCHIVED,
            modified_at=now,
            archived_at=now,
        )
        self._shots[archived.shot_id] = archived
        return archived

    def reorder_shot(self, shot_id: str, order_index: int) -> ShotRecord:
        """Update Shot order index."""

        shot = self.get_shot(shot_id)
        clean_order_index = self._validate_order_index(order_index)
        updated = shot.with_updates(order_index=clean_order_index, modified_at=utc_now_iso())
        self._shots[updated.shot_id] = updated
        return updated

    def _resolve_order_index(self, scene_id: str, order_index: int | None) -> int:
        """Resolve explicit or next order index for a Scene."""

        if order_index is not None:
            return self._validate_order_index(order_index)

        scene_shots = [shot for shot in self._shots.values() if shot.scene_id == scene_id]
        if not scene_shots:
            return 0

        return max(shot.order_index for shot in scene_shots) + 1

    def _validate_order_index(self, order_index: int) -> int:
        """Validate order index."""

        if not isinstance(order_index, int):
            raise ValidationError("order_index must be an integer.")
        if order_index < 0:
            raise ValidationError("order_index must not be negative.")
        return order_index

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def replace_shots(self, records: list) -> None:
        """Replace in-memory shot store. Used by bundle rehydration.

        Accepts only ShotRecord instances. Does not change module readiness.
        """

        from aurora_studio.contracts.shot import ShotRecord as _ShotRecord
        for item in records:
            if not isinstance(item, _ShotRecord):
                raise ValidationError("replace_shots requires ShotRecord instances.")
        self._shots = {r.shot_id: r for r in records}
