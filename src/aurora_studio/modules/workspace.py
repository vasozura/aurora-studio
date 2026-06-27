"""Workspace first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.workspace import DEFAULT_WORKSPACE_MODE, WorkspaceState
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness


class Workspace:
    """Minimal Workspace implementation.

    This class manages only in-memory active context references.

    It does not implement:
    - GUI state rendering
    - Project persistence
    - Scene data ownership
    - Shot data ownership
    - Timeline editing
    - Asset management
    - Provider integration
    - Plugin execution
    """

    module_name = "Workspace"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._state = WorkspaceState()

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Workspace supports minimal in-memory active context references "
            "and remains not ready for full product implementation."
        )

    def activate(self, project_id: str) -> WorkspaceState:
        """Activate workspace for a project reference."""

        clean_project_id = self._validate_required_ref(project_id, "project_id")
        self._state = WorkspaceState(active_project_id=clean_project_id)
        return self._state

    def set_mode(self, mode: str) -> WorkspaceState:
        """Set active workspace mode."""

        clean_mode = self._validate_required_ref(mode, "mode")
        self._state = self._state.with_updates(mode=clean_mode)
        return self._state

    def set_active_scene(self, scene_id: str | None) -> WorkspaceState:
        """Set active Scene reference.

        This does not read or mutate Scene data.
        """

        clean_scene_id = self._validate_optional_ref(scene_id, "scene_id")
        self._state = self._state.with_updates(active_scene_id=clean_scene_id)
        return self._state

    def set_active_shot(self, shot_id: str | None) -> WorkspaceState:
        """Set active Shot reference.

        This does not read or mutate Shot data.
        """

        clean_shot_id = self._validate_optional_ref(shot_id, "shot_id")
        self._state = self._state.with_updates(active_shot_id=clean_shot_id)
        return self._state

    def set_active_timeline(self, timeline_id: str | None) -> WorkspaceState:
        """Set active Timeline reference."""

        clean_timeline_id = self._validate_optional_ref(timeline_id, "timeline_id")
        self._state = self._state.with_updates(active_timeline_id=clean_timeline_id)
        return self._state

    def set_selection(self, selected_ref: str | None) -> WorkspaceState:
        """Set generic active selection reference."""

        clean_selected_ref = self._validate_optional_ref(selected_ref, "selected_ref")
        self._state = self._state.with_updates(selected_ref=clean_selected_ref)
        return self._state

    def clear_selection(self) -> WorkspaceState:
        """Clear active selection context."""

        self._state = self._state.with_updates(
            active_scene_id=None,
            active_shot_id=None,
            active_timeline_id=None,
            selected_ref=None,
        )
        return self._state

    def get_state(self) -> WorkspaceState:
        """Return current workspace state."""

        return self._state

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

    def _validate_optional_ref(self, value: str | None, field_name: str) -> str | None:
        """Validate an optional reference-like string."""

        if value is None:
            return None

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty when provided.")
        return clean_value
