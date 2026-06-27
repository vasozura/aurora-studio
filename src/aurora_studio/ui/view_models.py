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
class TimelineViewModel:
    """Minimal timeline representation for UI display."""

    timeline_id: str
    project_id: str
    title: str
    state: str
    item_count: int

    @classmethod
    def from_record(cls, record: Any) -> "TimelineViewModel":
        return cls(
            timeline_id=record.timeline_id,
            project_id=record.project_id,
            title=record.title,
            state=record.state,
            item_count=len(record.items),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TimelineItemViewModel:
    """Minimal timeline item representation for UI display."""

    item_id: str
    item_type: str
    target_id: str
    order_index: int

    @classmethod
    def from_record(cls, record: Any) -> "TimelineItemViewModel":
        return cls(
            item_id=record.item_id,
            item_type=record.item_type,
            target_id=record.target_id,
            order_index=record.order_index,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssetViewModel:
    """Minimal asset representation for UI display."""

    asset_id: str
    project_id: str
    asset_type: str
    display_name: str
    location: str
    state: str
    owner_ref: str | None

    @classmethod
    def from_record(cls, record: Any) -> "AssetViewModel":
        return cls(
            asset_id=record.asset_id,
            project_id=record.project_id,
            asset_type=record.asset_type,
            display_name=record.display_name,
            location=record.location,
            state=record.state,
            owner_ref=record.owner_ref,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CharacterViewModel:
    """Minimal character representation for UI display."""

    character_id: str
    project_id: str
    display_name: str
    description: str
    reference_asset_ids: tuple[str, ...]
    state: str

    @classmethod
    def from_record(cls, record: Any) -> "CharacterViewModel":
        return cls(
            character_id=record.character_id,
            project_id=record.project_id,
            display_name=record.display_name,
            description=record.description,
            reference_asset_ids=tuple(record.reference_asset_ids),
            state=record.state,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reference_asset_ids"] = list(d["reference_asset_ids"])
        return d


@dataclass(frozen=True)
class AppStateViewModel:
    """Snapshot of current application state for UI rendering.

    project may be None when no project is active.
    All collection fields default to empty tuples.
    """

    project: ProjectViewModel | None
    workspace: WorkspaceViewModel
    scenes: tuple[SceneViewModel, ...]
    shots: tuple[ShotViewModel, ...]
    timelines: tuple[TimelineViewModel, ...] = ()
    assets: tuple[AssetViewModel, ...] = ()
    characters: tuple[CharacterViewModel, ...] = ()
    afl_reports: tuple["AFLReportViewModel", ...] = ()
    export_artifacts: tuple["ExportArtifactViewModel", ...] = ()
    plugins: tuple["PluginViewModel", ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project.to_dict() if self.project is not None else None,
            "workspace": self.workspace.to_dict(),
            "scenes": [s.to_dict() for s in self.scenes],
            "shots": [s.to_dict() for s in self.shots],
            "timelines": [t.to_dict() for t in self.timelines],
            "assets": [a.to_dict() for a in self.assets],
            "characters": [c.to_dict() for c in self.characters],
            "afl_reports": [r.to_dict() for r in self.afl_reports],
            "export_artifacts": [e.to_dict() for e in self.export_artifacts],
            "plugins": [p.to_dict() for p in self.plugins],
        }


@dataclass(frozen=True)
class AFLReportViewModel:
    """Minimal AFL validation report representation for UI display."""

    report_id: str
    target_ref: str
    status: str
    issue_count: int
    created_at: str

    @classmethod
    def from_record(cls, record: Any) -> "AFLReportViewModel":
        return cls(
            report_id=record.report_id,
            target_ref=record.target_ref,
            status=record.status,
            issue_count=len(record.issues),
            created_at=record.created_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExportArtifactViewModel:
    """Minimal export artifact representation for UI display."""

    artifact_id: str
    source_id: str
    artifact_type: str
    status: str
    provider_target: str | None

    @classmethod
    def from_record(cls, record: Any) -> "ExportArtifactViewModel":
        return cls(
            artifact_id=record.artifact_id,
            source_id=record.source_id,
            artifact_type=record.artifact_type,
            status=record.status,
            provider_target=record.provider_target,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PluginViewModel:
    """Minimal plugin metadata representation for UI display."""

    plugin_id: str
    name: str
    version: str
    state: str
    capabilities: tuple[str, ...]
    permissions: tuple[str, ...]

    @classmethod
    def from_record(cls, record: Any) -> "PluginViewModel":
        return cls(
            plugin_id=record.plugin_id,
            name=record.name,
            version=record.version,
            state=record.state,
            capabilities=tuple(record.capabilities),
            permissions=tuple(record.permissions),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capabilities"] = list(d["capabilities"])
        d["permissions"] = list(d["permissions"])
        return d
