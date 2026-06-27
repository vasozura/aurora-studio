"""Bundle rehydration — restores in-memory manager state from a ProjectBundle.

Does not instantiate managers.
Does not write files.
Does not call providers.
Does not execute plugins.
Does not change module readiness.
Standard-library only.
"""

from __future__ import annotations

from typing import Any

from aurora_studio.contracts.afl import AFLValidationReport
from aurora_studio.contracts.asset import AssetRecord
from aurora_studio.contracts.character import CharacterRecord
from aurora_studio.contracts.export import ExportArtifactRecord
from aurora_studio.contracts.plugin import PluginMetadata
from aurora_studio.contracts.project_bundle import ProjectBundle
from aurora_studio.contracts.scene import SceneRecord
from aurora_studio.contracts.shot import ShotRecord
from aurora_studio.contracts.timeline import TimelineRecord
from aurora_studio.contracts.workspace import WorkspaceState
from aurora_studio.core.errors import ValidationError


class BundleRehydrator:
    """Converts a ProjectBundle back into in-memory manager state.

    Callers pass the managers they want restored.
    Managers not provided are silently skipped.
    The bundle is never mutated.
    """

    def rehydrate(
        self,
        bundle: ProjectBundle,
        *,
        workspace=None,
        scene_manager=None,
        shot_manager=None,
        timeline_manager=None,
        asset_manager=None,
        character_manager=None,
        afl_engine=None,
        prompt_export_manager=None,
        plugin_manager=None,
    ) -> dict[str, Any]:
        """Restore managers from bundle. Returns a summary of counts restored.

        Args:
            bundle: A valid ProjectBundle.
            workspace: Optional Workspace to restore state into.
            scene_manager: Optional SceneManager to restore scenes into.
            shot_manager: Optional ShotManager to restore shots into.
            timeline_manager: Optional TimelineManager to restore timelines into.
            asset_manager: Optional AssetManager to restore assets into.
            character_manager: Optional CharacterManager to restore characters into.
            afl_engine: Optional AFLEngine to restore validation reports into.
            prompt_export_manager: Optional PromptExportManager to restore artifacts into.
            plugin_manager: Optional PluginManager to restore plugins into.

        Returns:
            dict with keys: scenes, shots, timelines, assets, characters,
            afl_reports, export_artifacts, plugins, workspace_restored.
        """

        if not isinstance(bundle, ProjectBundle):
            raise ValidationError("rehydrate requires a ProjectBundle instance.")

        summary: dict[str, Any] = {
            "scenes": 0,
            "shots": 0,
            "timelines": 0,
            "assets": 0,
            "characters": 0,
            "afl_reports": 0,
            "export_artifacts": 0,
            "plugins": 0,
            "workspace_restored": False,
        }

        # Scenes
        if scene_manager is not None:
            records = [SceneRecord.from_dict(d) for d in bundle.scenes]
            scene_manager.replace_scenes(records)
            summary["scenes"] = len(records)

        # Shots
        if shot_manager is not None:
            records = [ShotRecord.from_dict(d) for d in bundle.shots]
            shot_manager.replace_shots(records)
            summary["shots"] = len(records)

        # Timelines
        if timeline_manager is not None:
            records = [TimelineRecord.from_dict(d) for d in bundle.timelines]
            timeline_manager.replace_timelines(records)
            summary["timelines"] = len(records)

        # Assets
        if asset_manager is not None:
            records = [AssetRecord.from_dict(d) for d in bundle.assets]
            asset_manager.replace_assets(records)
            summary["assets"] = len(records)

        # Characters
        if character_manager is not None:
            records = [CharacterRecord.from_dict(d) for d in bundle.characters]
            character_manager.replace_characters(records)
            summary["characters"] = len(records)

        # AFL reports
        if afl_engine is not None:
            records = [AFLValidationReport.from_dict(d) for d in bundle.afl_reports]
            afl_engine.replace_validation_reports(records)
            summary["afl_reports"] = len(records)

        # Export artifacts
        if prompt_export_manager is not None:
            records = [ExportArtifactRecord.from_dict(d) for d in bundle.export_artifacts]
            prompt_export_manager.replace_export_artifacts(records)
            summary["export_artifacts"] = len(records)

        # Plugins
        if plugin_manager is not None:
            records = [PluginMetadata.from_dict(d) for d in bundle.plugins]
            plugin_manager.replace_plugins(records)
            summary["plugins"] = len(records)

        # Workspace
        if workspace is not None and bundle.workspace_state is not None:
            state = WorkspaceState.from_dict(bundle.workspace_state)
            workspace.replace_state(state)
            summary["workspace_restored"] = True

        return summary
