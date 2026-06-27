"""Placeholder contracts for Aurora Studio skeleton."""

from aurora_studio.contracts.project import ProjectMetadata
from aurora_studio.contracts.workspace import WorkspaceState
from aurora_studio.contracts.scene import SceneRef
from aurora_studio.contracts.shot import ShotRef
from aurora_studio.contracts.asset import AssetRef
from aurora_studio.contracts.character import CharacterRef
from aurora_studio.contracts.afl import AFLValidationReport
from aurora_studio.contracts.export import ExportArtifactRef
from aurora_studio.contracts.plugin import PluginMetadata
from aurora_studio.contracts.validation import ValidationIssue, ValidationReport

__all__ = [
    "ProjectMetadata",
    "WorkspaceState",
    "SceneRef",
    "ShotRef",
    "AssetRef",
    "CharacterRef",
    "AFLValidationReport",
    "ExportArtifactRef",
    "PluginMetadata",
    "ValidationIssue",
    "ValidationReport",
]
