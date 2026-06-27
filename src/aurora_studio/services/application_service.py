"""Application service — coordinates existing managers for core use cases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aurora_studio.contracts.project_bundle import ProjectBundle
from aurora_studio.contracts.project import ProjectMetadata
from aurora_studio.contracts.scene import SceneRecord
from aurora_studio.contracts.shot import ShotRecord
from aurora_studio.contracts.workspace import WorkspaceState
from aurora_studio.core.errors import ValidationError
from aurora_studio.modules.afl_engine import AFLEngine
from aurora_studio.modules.asset_manager import AssetManager
from aurora_studio.modules.character_manager import CharacterManager
from aurora_studio.modules.plugin_manager import PluginManager
from aurora_studio.modules.project_manager import ProjectManager
from aurora_studio.modules.prompt_export_manager import PromptExportManager
from aurora_studio.modules.scene_manager import SceneManager
from aurora_studio.modules.shot_manager import ShotManager
from aurora_studio.modules.timeline_manager import TimelineManager
from aurora_studio.modules.workspace import Workspace
from aurora_studio.persistence import LocalProjectStore


class ApplicationService:
    """Minimal application service.

    Coordinates existing managers without changing their ownership boundaries.
    Does not implement GUI, database, web API, event bus, autosave,
    provider integration, plugin execution or automatic manager rehydration.
    """

    def __init__(
        self,
        project_manager: ProjectManager | None = None,
        workspace: Workspace | None = None,
        scene_manager: SceneManager | None = None,
        shot_manager: ShotManager | None = None,
        timeline_manager: TimelineManager | None = None,
        asset_manager: AssetManager | None = None,
        character_manager: CharacterManager | None = None,
        afl_engine: AFLEngine | None = None,
        prompt_export_manager: PromptExportManager | None = None,
        plugin_manager: PluginManager | None = None,
        project_store: LocalProjectStore | None = None,
    ) -> None:
        self.project_manager = project_manager or ProjectManager()
        self.workspace = workspace or Workspace()
        self.scene_manager = scene_manager or SceneManager()
        self.shot_manager = shot_manager or ShotManager()
        self.timeline_manager = timeline_manager or TimelineManager()
        self.asset_manager = asset_manager or AssetManager()
        self.character_manager = character_manager or CharacterManager()
        self.afl_engine = afl_engine or AFLEngine()
        self.prompt_export_manager = prompt_export_manager or PromptExportManager()
        self.plugin_manager = plugin_manager or PluginManager()
        self.project_store = project_store or LocalProjectStore()
        self._current_project_metadata: ProjectMetadata | None = None

    def create_project(self, path: str | Path, title: str) -> ProjectMetadata:
        """Create a local project and activate workspace.

        Does not create Scenes, Shots, Assets, Characters or Timelines.
        Does not save a bundle automatically.
        """

        metadata = self.project_manager.create_project(path, title)
        self._current_project_metadata = metadata
        self.workspace.activate(metadata.project_id)
        return metadata

    def open_project(self, path: str | Path) -> ProjectMetadata:
        """Open an existing local project and activate workspace.

        Does not load a bundle.
        Does not rehydrate managers.
        """

        metadata = self.project_manager.open_project(path)
        self._current_project_metadata = metadata
        self.workspace.activate(metadata.project_id)
        return metadata

    def create_scene(self, title: str, purpose: str = "") -> SceneRecord:
        """Create a Scene for the active project and select it in workspace.

        Requires an active project. Raises ValidationError if none.
        Does not create Shots automatically.
        """

        active_project_id = self._require_active_project()
        scene = self.scene_manager.create_scene(active_project_id, title, purpose)
        self.workspace.set_active_scene(scene.scene_id)
        return scene

    def create_shot(
        self,
        scene_id: str,
        title: str,
        purpose: str = "",
        order_index: int | None = None,
    ) -> ShotRecord:
        """Create a Shot under a Scene and select it in workspace.

        Requires an active project. Raises ValidationError if none.
        Does not validate whether Scene exists.
        Does not create Timeline items automatically.
        """

        self._require_active_project()
        shot = self.shot_manager.create_shot(scene_id, title, purpose, order_index)
        self.workspace.set_active_scene(scene_id)
        self.workspace.set_active_shot(shot.shot_id)
        return shot

    def save_bundle(self, path: str | Path) -> Path:
        """Save current in-memory state as a local JSON bundle.

        Does not mutate managers.
        """

        bundle = self.project_store.create_bundle(
            project_metadata=self._current_project_metadata,
            workspace=self.workspace,
            scene_manager=self.scene_manager,
            shot_manager=self.shot_manager,
            timeline_manager=self.timeline_manager,
            asset_manager=self.asset_manager,
            character_manager=self.character_manager,
            afl_engine=self.afl_engine,
            prompt_export_manager=self.prompt_export_manager,
            plugin_manager=self.plugin_manager,
        )
        return self.project_store.save_bundle(path, bundle)

    def load_bundle(self, path: str | Path) -> ProjectBundle:
        """Load a local JSON bundle.

        Does not automatically rehydrate managers.
        Does not overwrite current in-memory managers.
        """

        return self.project_store.load_bundle(path)

    def get_workspace_state(self) -> WorkspaceState:
        """Return current workspace state."""

        return self.workspace.get_state()

    def _require_active_project(self) -> str:
        """Return active project ID or raise ValidationError."""

        state = self.workspace.get_state()
        if not state.active_project_id:
            raise ValidationError(
                "No active project. Call create_project() or open_project() first."
            )
        return state.active_project_id
