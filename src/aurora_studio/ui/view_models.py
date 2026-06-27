"""Aurora Studio UI view models.

Thin read-only projections of core contracts for UI consumption.
Dataclasses only — no business logic, no persistence, no provider calls.
All fields are JSON-serializable primitives or tuples of view models.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectViewModel:
    """Minimal project representation for UI display."""

    project_id: str
    title: str
    version: str

    @classmethod
    def from_metadata(cls, metadata: Any) -> "ProjectViewModel":
        return cls(
            project_id=metadata.project_id,
            title=metadata.title,
            version=metadata.version,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkspaceViewModel:
    """Minimal workspace state representation for UI display."""

    active_project_id: str | None
    active_scene_id: str | None
    active_shot_id: str | None
    mode: str

    @classmethod
    def from_state(cls, state: Any) -> "WorkspaceViewModel":
        return cls(
            active_project_id=state.active_project_id,
            active_scene_id=state.active_scene_id,
            active_shot_id=state.active_shot_id,
            mode=state.mode,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SceneViewModel:
    """Minimal scene representation for UI display."""

    scene_id: str
    project_id: str
    title: str
    state: str

    @classmethod
    def from_record(cls, record: Any) -> "SceneViewModel":
        return cls(
            scene_id=record.scene_id,
            project_id=record.project_id,
            title=record.title,
            state=record.state,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ShotViewModel:
    """Minimal shot representation for UI display."""

    shot_id: str
    scene_id: str
    title: str
    order_index: int
    state: str

    @classmethod
    def from_record(cls, record: Any) -> "ShotViewModel":
        return cls(
            shot_id=record.shot_id,
            scene_id=record.scene_id,
            title=record.title,
            order_index=record.order_index,
            state=record.state,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AppStateViewModel:
    """Snapshot of current application state for UI rendering.

    project may be None when no project is active.
    scenes and shots are tuples of view model instances.
    """

    project: ProjectViewModel | None
    workspace: WorkspaceViewModel
    scenes: tuple[SceneViewModel, ...]
    shots: tuple[ShotViewModel, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project.to_dict() if self.project is not None else None,
            "workspace": self.workspace.to_dict(),
            "scenes": [s.to_dict() for s in self.scenes],
            "shots": [s.to_dict() for s in self.shots],
        }
