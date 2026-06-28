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
class SceneDetailViewModel:
    """Full scene detail representation for inspector/editor UI.

    status maps to record.state.
    updated_at maps to record.modified_at.
    """

    scene_id: str
    project_id: str
    title: str
    description: str
    purpose: str
    location: str
    time_of_day: str
    mood: str
    conflict: str
    narrative_beat: str
    status: str
    notes: str
    created_at: str
    updated_at: str

    @classmethod
    def from_record(cls, record: Any) -> "SceneDetailViewModel":
        return cls(
            scene_id=record.scene_id,
            project_id=record.project_id,
            title=record.title,
            description=getattr(record, "description", ""),
            purpose=getattr(record, "purpose", ""),
            location=getattr(record, "location", ""),
            time_of_day=getattr(record, "time_of_day", ""),
            mood=getattr(record, "mood", ""),
            conflict=getattr(record, "conflict", ""),
            narrative_beat=getattr(record, "narrative_beat", ""),
            status=record.state,
            notes=getattr(record, "notes", ""),
            created_at=record.created_at,
            updated_at=record.modified_at,
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
class ShotDetailViewModel:
    """Full shot detail representation for inspector/editor UI.

    status maps to record.state.
    updated_at maps to record.modified_at.
    """

    shot_id: str
    project_id: str
    scene_id: str
    title: str
    description: str
    shot_type: str
    camera_angle: str
    camera_movement: str
    framing: str
    lens: str
    duration_seconds: float
    emotion_target: str
    visual_focus: str
    status: str
    notes: str
    order_index: int
    created_at: str
    updated_at: str

    @classmethod
    def from_record(cls, record: Any) -> "ShotDetailViewModel":
        return cls(
            shot_id=record.shot_id,
            project_id=getattr(record, "project_id", ""),
            scene_id=record.scene_id,
            title=record.title,
            description=getattr(record, "description", ""),
            shot_type=getattr(record, "shot_type", ""),
            camera_angle=getattr(record, "camera_angle", ""),
            camera_movement=getattr(record, "camera_movement", ""),
            framing=getattr(record, "framing", ""),
            lens=getattr(record, "lens", ""),
            duration_seconds=float(getattr(record, "duration_seconds", 0.0) or 0.0),
            emotion_target=getattr(record, "emotion_target", ""),
            visual_focus=getattr(record, "visual_focus", ""),
            status=record.state,
            notes=getattr(record, "notes", ""),
            order_index=record.order_index,
            created_at=record.created_at,
            updated_at=record.modified_at,
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
    """Timeline item representation for UI display (includes timeline_id)."""

    item_id: str
    timeline_id: str
    item_type: str
    target_id: str
    order_index: int

    @classmethod
    def from_item(cls, item: Any, timeline_id: str) -> "TimelineItemViewModel":
        return cls(
            item_id=item.item_id,
            timeline_id=timeline_id,
            item_type=item.item_type,
            target_id=item.target_id,
            order_index=item.order_index,
        )

    @classmethod
    def from_record(cls, record: Any) -> "TimelineItemViewModel":
        """Legacy compatibility — timeline_id defaults to empty string."""
        return cls(
            item_id=record.item_id,
            timeline_id="",
            item_type=record.item_type,
            target_id=record.target_id,
            order_index=record.order_index,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TimelineSummaryViewModel:
    """Summary of a Timeline for display."""

    timeline_id: str
    item_count: int
    scene_item_count: int
    shot_item_count: int
    total_duration_seconds: float
    ordered_items: tuple[dict, ...]

    @classmethod
    def from_summary(cls, summary: dict[str, Any]) -> "TimelineSummaryViewModel":
        return cls(
            timeline_id=str(summary.get("timeline_id", "")),
            item_count=int(summary.get("item_count", 0)),
            scene_item_count=int(summary.get("scene_item_count", 0)),
            shot_item_count=int(summary.get("shot_item_count", 0)),
            total_duration_seconds=float(summary.get("total_duration_seconds", 0.0)),
            ordered_items=tuple(summary.get("ordered_items", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeline_id": self.timeline_id,
            "item_count": self.item_count,
            "scene_item_count": self.scene_item_count,
            "shot_item_count": self.shot_item_count,
            "total_duration_seconds": self.total_duration_seconds,
            "ordered_items": list(self.ordered_items),
        }


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
class AssetDetailViewModel:
    """Full asset detail for inspector/editor."""

    asset_id: str
    project_id: str
    asset_type: str
    display_name: str
    location: str
    description: str
    tags: tuple[str, ...]
    usage_count: int
    notes: str
    status: str  # ← record.state
    owner_ref: str | None
    created_at: str
    updated_at: str  # ← record.modified_at

    @classmethod
    def from_record(cls, record: Any) -> "AssetDetailViewModel":
        return cls(
            asset_id=record.asset_id,
            project_id=record.project_id,
            asset_type=record.asset_type,
            display_name=record.display_name,
            location=record.location,
            description=getattr(record, "description", ""),
            tags=tuple(getattr(record, "tags", ())),
            usage_count=int(getattr(record, "usage_count", 0)),
            notes=getattr(record, "notes", ""),
            status=record.state,
            owner_ref=record.owner_ref,
            created_at=record.created_at,
            updated_at=record.modified_at,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(d["tags"])
        return d


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
class CharacterDetailViewModel:
    """Full character detail for inspector/editor (TASK-000058/059)."""

    character_id: str
    project_id: str
    display_name: str
    description: str
    role: str
    visual_description: str
    personality: str
    motivation: str
    conflict: str
    arc_notes: str
    notes: str
    status: str  # ← record.state
    reference_asset_ids: tuple[str, ...]
    reference_assets: tuple[dict, ...]  # serialized CharacterReference dicts
    created_at: str
    updated_at: str  # ← record.modified_at

    @classmethod
    def from_record(cls, record: Any) -> "CharacterDetailViewModel":
        ref_assets = tuple(
            r.to_dict() if hasattr(r, "to_dict") else dict(r)
            for r in getattr(record, "reference_assets", ())
        )
        return cls(
            character_id=record.character_id,
            project_id=record.project_id,
            display_name=record.display_name,
            description=getattr(record, "description", ""),
            role=getattr(record, "role", ""),
            visual_description=getattr(record, "visual_description", ""),
            personality=getattr(record, "personality", ""),
            motivation=getattr(record, "motivation", ""),
            conflict=getattr(record, "conflict", ""),
            arc_notes=getattr(record, "arc_notes", ""),
            notes=getattr(record, "notes", ""),
            status=record.state,
            reference_asset_ids=tuple(record.reference_asset_ids),
            reference_assets=ref_assets,
            created_at=record.created_at,
            updated_at=record.modified_at,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reference_asset_ids"] = list(d["reference_asset_ids"])
        d["reference_assets"] = list(d["reference_assets"])
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
            source_id=getattr(record, "source_id", ""),
            artifact_type=record.artifact_type,
            status=getattr(record, "status", getattr(record, "state", "")),
            provider_target=getattr(record, "provider_target", None),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PluginViewModel:
    """Minimal plugin representation for UI display."""

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
            state=getattr(record, "state", "registered"),
            capabilities=tuple(getattr(record, "capabilities", ())),
            permissions=tuple(getattr(record, "permissions", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capabilities"] = list(d["capabilities"])
        d["permissions"] = list(d["permissions"])
        return d

@dataclass(frozen=True)
class ProviderCapabilityViewModel:
    """Minimal provider capability for UI display."""

    name: str
    description: str

    @classmethod
    def from_record(cls, record: Any) -> "ProviderCapabilityViewModel":
        return cls(name=record.name, description=record.description)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderViewModel:
    """Minimal provider representation for UI display."""

    provider_id: str
    name: str
    version: str
    provider_type: str
    state: str
    requires_api_key: bool
    supports_dry_run: bool
    description: str
    error_message: str
    capabilities: tuple["ProviderCapabilityViewModel", ...]

    @classmethod
    def from_record(cls, record: Any) -> "ProviderViewModel":
        caps = tuple(
            ProviderCapabilityViewModel.from_record(c)
            for c in getattr(record, "capabilities", ())
        )
        return cls(
            provider_id=record.provider_id,
            name=record.name,
            version=record.version,
            provider_type=record.provider_type,
            state=record.state,
            requires_api_key=getattr(record, "requires_api_key", False),
            supports_dry_run=getattr(record, "supports_dry_run", True),
            description=getattr(record, "description", ""),
            error_message=getattr(record, "error_message", ""),
            capabilities=caps,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capabilities"] = [c for c in d["capabilities"]]
        return d

@dataclass(frozen=True)
class PromptExecutionQueueItemViewModel:
    """Minimal queue item representation for UI display."""

    queue_item_id: str
    request_id: str
    provider_id: str
    source_type: str
    source_id: str
    status: str
    priority: int
    attempt_count: int
    error_message: str

    @classmethod
    def from_record(cls, record: Any) -> "PromptExecutionQueueItemViewModel":
        return cls(
            queue_item_id=record.queue_item_id,
            request_id=record.request_id,
            provider_id=record.provider_id,
            source_type=record.source_type,
            source_id=record.source_id,
            status=record.status,
            priority=record.priority,
            attempt_count=record.attempt_count,
            error_message=record.error_message,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderConfigViewModel:
    """View model for provider config UI state.

    Never includes real secret values.
    real_execution_allowed is always False in v0.4.
    """

    provider_id: str
    enabled: bool = False
    configured: bool = False
    config_status: str = "not_configured"
    display_name: str = ""
    provider_type: str = "other"
    requires_api_key: bool = False
    supports_dry_run: bool = True
    real_execution_allowed: bool = False
    secret_storage_status: str = "not_configured"
    last_error: str = ""
    notes: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict — never includes secret fields."""
        return {
            "provider_id": self.provider_id,
            "enabled": self.enabled,
            "configured": self.configured,
            "config_status": self.config_status,
            "display_name": self.display_name,
            "provider_type": self.provider_type,
            "requires_api_key": self.requires_api_key,
            "supports_dry_run": self.supports_dry_run,
            "real_execution_allowed": self.real_execution_allowed,
            "secret_storage_status": self.secret_storage_status,
            "last_error": self.last_error,
            "notes": self.notes,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_record(cls, record: Any) -> "ProviderConfigViewModel":
        """Build from a provider config metadata dict or similar record."""
        if isinstance(record, dict):
            d = record
        else:
            d = record.to_dict() if hasattr(record, "to_dict") else {}
        return cls(
            provider_id=str(d.get("provider_id", "")),
            enabled=bool(d.get("enabled", False)),
            configured=bool(d.get("configured", False)),
            config_status=str(d.get("config_status", "not_configured")),
            display_name=str(d.get("display_name", d.get("provider_id", ""))),
            provider_type=str(d.get("provider_type", "other")),
            requires_api_key=bool(d.get("requires_api_key", False)),
            supports_dry_run=bool(d.get("supports_dry_run", True)),
            real_execution_allowed=False,  # always False in v0.4
            secret_storage_status=str(d.get("secret_storage_status", "not_configured")),
            last_error=str(d.get("last_error", "")),
            notes=str(d.get("notes", "")),
            updated_at=str(d.get("updated_at", "")),
        )
