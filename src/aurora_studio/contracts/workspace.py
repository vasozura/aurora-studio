"""Workspace contract placeholders and first minimal workspace state contract."""

from dataclasses import asdict, dataclass, replace
from typing import Any


DEFAULT_WORKSPACE_MODE = "default"


@dataclass(frozen=True)
class WorkspaceState:
    """Minimal workspace state contract.

    Workspace state is active context, not source creative meaning.
    It must not own Scene, Shot, Asset or Character data.
    """

    active_project_id: str | None = None
    active_scene_id: str | None = None
    active_shot_id: str | None = None
    active_timeline_id: str | None = None
    selected_ref: str | None = None
    mode: str = DEFAULT_WORKSPACE_MODE

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable workspace state."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "WorkspaceState":
        """Return a new workspace state with selected fields changed."""

        return replace(self, **changes)
