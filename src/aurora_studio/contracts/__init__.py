"""Aurora Studio contracts package — public exports."""

from aurora_studio.contracts.project import ProjectMetadata
from aurora_studio.contracts.workspace import WorkspaceState, DEFAULT_WORKSPACE_MODE
from aurora_studio.contracts.scene import SceneRecord, SceneRef, SCENE_STATE_DRAFT, SCENE_STATE_ARCHIVED
from aurora_studio.contracts.shot import ShotRecord, ShotRef, SHOT_STATE_DRAFT, SHOT_STATE_ARCHIVED
from aurora_studio.contracts.timeline import (
    TimelineRecord, TimelineRef, TimelineItem,
    TIMELINE_STATE_DRAFT, TIMELINE_STATE_ARCHIVED,
)
from aurora_studio.contracts.asset import (
    AssetRecord, AssetRef,
    ASSET_STATE_ACTIVE, ASSET_STATE_MISSING, ASSET_STATE_ARCHIVED,
)
from aurora_studio.contracts.character import (
    CharacterRecord, CharacterRef,
    CHARACTER_STATE_ACTIVE, CHARACTER_STATE_ARCHIVED,
)
from aurora_studio.contracts.afl import (
    AFLValidationReport, AFLValidationIssue,
    AFL_STATUS_VALID, AFL_STATUS_INVALID, AFL_STATUS_NOT_CHECKED,
)
from aurora_studio.contracts.export import (
    ExportArtifactRecord, ExportArtifactRef,
    EXPORT_STATUS_DRAFT, EXPORT_STATUS_READY, EXPORT_STATUS_FAILED,
)
from aurora_studio.contracts.plugin import (
    PluginMetadata,
    PLUGIN_STATE_DISCOVERED, PLUGIN_STATE_ENABLED,
    PLUGIN_STATE_DISABLED, PLUGIN_STATE_INVALID,
)
from aurora_studio.contracts.project_bundle import (
    ProjectBundle, CURRENT_BUNDLE_VERSION, DEFAULT_BUNDLE_FILENAME,
)
from aurora_studio.contracts.validation import ValidationIssue, ValidationReport

__all__ = [
    # project
    "ProjectMetadata",
    # workspace
    "WorkspaceState", "DEFAULT_WORKSPACE_MODE",
    # scene
    "SceneRecord", "SceneRef", "SCENE_STATE_DRAFT", "SCENE_STATE_ARCHIVED",
    # shot
    "ShotRecord", "ShotRef", "SHOT_STATE_DRAFT", "SHOT_STATE_ARCHIVED",
    # timeline
    "TimelineRecord", "TimelineRef", "TimelineItem",
    "TIMELINE_STATE_DRAFT", "TIMELINE_STATE_ARCHIVED",
    # asset
    "AssetRecord", "AssetRef",
    "ASSET_STATE_ACTIVE", "ASSET_STATE_MISSING", "ASSET_STATE_ARCHIVED",
    # character
    "CharacterRecord", "CharacterRef",
    "CHARACTER_STATE_ACTIVE", "CHARACTER_STATE_ARCHIVED",
    # afl
    "AFLValidationReport", "AFLValidationIssue",
    "AFL_STATUS_VALID", "AFL_STATUS_INVALID", "AFL_STATUS_NOT_CHECKED",
    # export
    "ExportArtifactRecord", "ExportArtifactRef",
    "EXPORT_STATUS_DRAFT", "EXPORT_STATUS_READY", "EXPORT_STATUS_FAILED",
    # plugin
    "PluginMetadata",
    "PLUGIN_STATE_DISCOVERED", "PLUGIN_STATE_ENABLED",
    "PLUGIN_STATE_DISABLED", "PLUGIN_STATE_INVALID",
    # bundle
    "ProjectBundle", "CURRENT_BUNDLE_VERSION", "DEFAULT_BUNDLE_FILENAME",
    # legacy validation
    "ValidationIssue", "ValidationReport",
]
