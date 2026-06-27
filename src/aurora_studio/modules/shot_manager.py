"""Shot Manager implementation (v0.2: update_shot_details, project_id filter added)."""

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

_DETAIL_FIELDS = frozenset({
    "description", "shot_type", "camera_angle", "camera_movement",
    "framing", "lens", "duration_seconds", "emotion_target",
    "visual_focus", "notes",
})


class ShotManager:
    """Minimal Shot Manager implementation.

    Does not implement: Scene creation, Scene existence validation,
    Timeline placement, Camera modeling, AFL validation, Prompt export,
    Database persistence, Provider integration, Plugin execution, GUI behavior.
    """

    module_name = "Shot Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._shots: dict[str, ShotRecord] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
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
        project_id: str = "",
    ) -> ShotRecord:
        """Create an in-memory Shot record.

        Does not validate whether the parent Scene exists.
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
            project_id=project_id.strip() if project_id else "",
        )
        self._shots[shot.shot_id] = shot
        return shot

    def list_shots(
        self,
        scene_id: str | None = None,
        project_id: str | None = None,
    ) -> list[ShotRecord]:
        """List Shot records, optionally filtered by scene_id or project_id."""

        shots = list(self._shots.values())

        if scene_id is not None:
            clean_scene_id = self._validate_required_ref(scene_id, "scene_id")
            shots = [s for s in shots if s.scene_id == clean_scene_id]

        if project_id is not None:
            clean_project_id = self._validate_required_ref(project_id, "project_id")
            shots = [s for s in shots if s.project_id == clean_project_id]

        return sorted(shots, key=lambda s: (s.scene_id, s.order_index, s.created_at))

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
        """Update minimal Shot-owned fields (title, purpose)."""

        shot = self.get_shot(shot_id)
        changes: dict = {"modified_at": utc_now_iso()}

        if title is not None:
            changes["title"] = self._validate_required_ref(title, "title")
        if purpose is not None:
            changes["purpose"] = purpose.strip()

        updated = shot.with_updates(**changes)
        self._shots[updated.shot_id] = updated
        return updated

    def update_shot_details(
        self,
        shot_id: str,
        **fields,
    ) -> ShotRecord:
        """Update any combination of Shot detail fields.

        Accepted keyword fields: title, purpose, description, shot_type,
        camera_angle, camera_movement, framing, lens, duration_seconds,
        emotion_target, visual_focus, notes.

        title must not be empty when provided.
        duration_seconds must be numeric and non-negative.
        Unknown field names raise ValidationError.
        """

        allowed = _DETAIL_FIELDS | {"title", "purpose"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValidationError(f"Unknown shot detail fields: {', '.join(sorted(unknown))}")

        shot = self.get_shot(shot_id)
        changes: dict = {"modified_at": utc_now_iso()}

        for key, val in fields.items():
            if key == "title":
                changes["title"] = self._validate_required_ref(str(val), "title")
            elif key == "duration_seconds":
                try:
                    d = float(val)
                except (TypeError, ValueError):
                    raise ValidationError("duration_seconds must be a number.")
                if d < 0:
                    raise ValidationError("duration_seconds must not be negative.")
                changes["duration_seconds"] = d
            else:
                changes[key] = str(val) if not isinstance(val, str) else val

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
        if order_index is not None:
            return self._validate_order_index(order_index)

        scene_shots = [s for s in self._shots.values() if s.scene_id == scene_id]
        if not scene_shots:
            return 0
        return max(s.order_index for s in scene_shots) + 1

    def _validate_order_index(self, order_index: int) -> int:
        if not isinstance(order_index, int):
            raise ValidationError("order_index must be an integer.")
        if order_index < 0:
            raise ValidationError("order_index must not be negative.")
        return order_index

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def replace_shots(self, records: list) -> None:
        """Replace in-memory shot store. Used by bundle rehydration."""

        from aurora_studio.contracts.shot import ShotRecord as _ShotRecord
        for item in records:
            if not isinstance(item, _ShotRecord):
                raise ValidationError("replace_shots requires ShotRecord instances.")
        self._shots = {r.shot_id: r for r in records}
