"""Scene Manager implementation (v0.2: update_scene_details added)."""

from __future__ import annotations

from aurora_studio.contracts.scene import (
    SCENE_STATE_ARCHIVED,
    SCENE_STATE_DRAFT,
    SceneRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness

_DETAIL_FIELDS = frozenset({
    "description", "location", "time_of_day", "mood",
    "conflict", "narrative_beat", "notes",
})


class SceneManager:
    """Minimal Scene Manager implementation.

    It does not implement: Shot creation, Timeline placement, Character Presence,
    AFL validation, Prompt export, Database persistence, Provider integration,
    Plugin execution, GUI behavior.
    """

    module_name = "Scene Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._scenes: dict[str, SceneRecord] = {}

    def get_readiness(self) -> Readiness:
        return self.readiness

    def describe(self) -> str:
        return (
            "Scene Manager supports minimal in-memory Scene records "
            "and remains not ready for full product implementation."
        )

    def create_scene(self, project_id: str, title: str, purpose: str = "") -> SceneRecord:
        """Create an in-memory Scene record."""

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        clean_title = self._validate_required_ref(title, "title")
        clean_purpose = purpose.strip()
        now = utc_now_iso()

        scene = SceneRecord(
            scene_id=new_id("scene"),
            project_id=clean_project_id,
            title=clean_title,
            purpose=clean_purpose,
            state=SCENE_STATE_DRAFT,
            created_at=now,
            modified_at=now,
        )
        self._scenes[scene.scene_id] = scene
        return scene

    def list_scenes(self, project_id: str | None = None) -> list[SceneRecord]:
        """List Scene records, optionally filtered by project reference."""

        if project_id is None:
            return list(self._scenes.values())

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        return [s for s in self._scenes.values() if s.project_id == clean_project_id]

    def get_scene(self, scene_id: str) -> SceneRecord:
        """Return a Scene record by ID."""

        clean_scene_id = self._validate_required_ref(scene_id, "scene_id")
        try:
            return self._scenes[clean_scene_id]
        except KeyError as exc:
            raise ValidationError(f"Scene not found: {clean_scene_id}") from exc

    def update_scene(
        self,
        scene_id: str,
        *,
        title: str | None = None,
        purpose: str | None = None,
    ) -> SceneRecord:
        """Update minimal Scene-owned fields (title, purpose).

        Does not update Shots, Timeline, Characters or export state.
        """

        scene = self.get_scene(scene_id)
        changes: dict = {"modified_at": utc_now_iso()}

        if title is not None:
            changes["title"] = self._validate_required_ref(title, "title")
        if purpose is not None:
            changes["purpose"] = purpose.strip()

        updated = scene.with_updates(**changes)
        self._scenes[updated.scene_id] = updated
        return updated

    def update_scene_details(
        self,
        scene_id: str,
        **fields: str,
    ) -> SceneRecord:
        """Update any combination of Scene detail fields.

        Accepted keyword fields: title, purpose, description, location,
        time_of_day, mood, conflict, narrative_beat, notes.

        title must not be empty when provided.
        Unknown field names raise ValidationError.
        """

        allowed = _DETAIL_FIELDS | {"title", "purpose"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValidationError(f"Unknown scene detail fields: {', '.join(sorted(unknown))}")

        scene = self.get_scene(scene_id)
        changes: dict = {"modified_at": utc_now_iso()}

        for key, val in fields.items():
            if not isinstance(val, str):
                val = str(val)
            if key == "title":
                changes["title"] = self._validate_required_ref(val, "title")
            else:
                changes[key] = val.strip() if key != "notes" else val

        updated = scene.with_updates(**changes)
        self._scenes[updated.scene_id] = updated
        return updated

    def archive_scene(self, scene_id: str) -> SceneRecord:
        """Archive a Scene record in memory."""

        scene = self.get_scene(scene_id)
        now = utc_now_iso()
        archived = scene.with_updates(
            state=SCENE_STATE_ARCHIVED,
            modified_at=now,
            archived_at=now,
        )
        self._scenes[archived.scene_id] = archived
        return archived

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def replace_scenes(self, records: list) -> None:
        """Replace in-memory scene store. Used by bundle rehydration."""

        from aurora_studio.contracts.scene import SceneRecord as _SceneRecord
        for item in records:
            if not isinstance(item, _SceneRecord):
                raise ValidationError("replace_scenes requires SceneRecord instances.")
        self._scenes = {r.scene_id: r for r in records}
