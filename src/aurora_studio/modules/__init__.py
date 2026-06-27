"""Aurora Studio module placeholders."""

from aurora_studio.modules.project_manager import ProjectManager
from aurora_studio.modules.workspace import Workspace
from aurora_studio.modules.scene_manager import SceneManager
from aurora_studio.modules.shot_manager import ShotManager
from aurora_studio.modules.timeline_manager import TimelineManager
from aurora_studio.modules.asset_manager import AssetManager
from aurora_studio.modules.character_manager import CharacterManager
from aurora_studio.modules.afl_engine import AFLEngine
from aurora_studio.modules.prompt_export_manager import PromptExportManager
from aurora_studio.modules.plugin_manager import PluginManager

__all__ = [
    "ProjectManager",
    "Workspace",
    "SceneManager",
    "ShotManager",
    "TimelineManager",
    "AssetManager",
    "CharacterManager",
    "AFLEngine",
    "PromptExportManager",
    "PluginManager",
]
