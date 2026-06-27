"""Tests for the Local Project Store and ProjectBundle."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.project_bundle import (
    CURRENT_BUNDLE_VERSION,
    DEFAULT_BUNDLE_FILENAME,
    ProjectBundle,
)
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


class ProjectBundleTests(unittest.TestCase):
    def test_bundle_empty(self) -> None:
        bundle = ProjectBundle.empty()

        self.assertEqual(bundle.schema_version, CURRENT_BUNDLE_VERSION)
        self.assertEqual(bundle.project_metadata, {})
        self.assertIsNone(bundle.workspace_state)
        self.assertEqual(bundle.scenes, ())
        self.assertNotEqual(bundle.created_at, "")

    def test_bundle_empty_with_metadata(self) -> None:
        bundle = ProjectBundle.empty({"title": "My Film"})

        self.assertEqual(bundle.project_metadata, {"title": "My Film"})

    def test_bundle_to_dict(self) -> None:
        bundle = ProjectBundle.empty({"title": "My Film"})

        data = bundle.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["schema_version"], CURRENT_BUNDLE_VERSION)
        self.assertEqual(data["project_metadata"], {"title": "My Film"})
        self.assertIsInstance(data["scenes"], list)
        self.assertIsInstance(data["shots"], list)

    def test_bundle_from_dict_roundtrip(self) -> None:
        bundle = ProjectBundle.empty({"title": "My Film"})

        restored = ProjectBundle.from_dict(bundle.to_dict())

        self.assertEqual(restored.schema_version, CURRENT_BUNDLE_VERSION)
        self.assertEqual(restored.project_metadata, {"title": "My Film"})
        self.assertEqual(restored.scenes, ())

    def test_bundle_from_dict_rejects_missing_schema_version(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectBundle.from_dict({"project_metadata": {}})

    def test_bundle_from_dict_rejects_unsupported_schema_version(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectBundle.from_dict({"schema_version": "99.0.0", "project_metadata": {}})

    def test_bundle_from_dict_rejects_non_dict_project_metadata(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectBundle.from_dict({
                "schema_version": CURRENT_BUNDLE_VERSION,
                "project_metadata": "not a dict",
            })

    def test_bundle_from_dict_rejects_non_list_collection_field(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectBundle.from_dict({
                "schema_version": CURRENT_BUNDLE_VERSION,
                "project_metadata": {},
                "scenes": "not a list",
            })

    def test_bundle_from_dict_rejects_non_dict(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectBundle.from_dict("not a dict")


class LocalProjectStoreTests(unittest.TestCase):
    def test_save_bundle_writes_json_file(self) -> None:
        store = LocalProjectStore()
        bundle = ProjectBundle.empty({"title": "Test"})

        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "bundle.json"
            result = store.save_bundle(file_path, bundle)

            self.assertTrue(result.exists())
            self.assertEqual(result.name, "bundle.json")

    def test_load_bundle_reads_json_file(self) -> None:
        store = LocalProjectStore()
        bundle = ProjectBundle.empty({"title": "Test"})

        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "bundle.json"
            store.save_bundle(file_path, bundle)
            loaded = store.load_bundle(file_path)

            self.assertEqual(loaded.schema_version, CURRENT_BUNDLE_VERSION)
            self.assertEqual(loaded.project_metadata, {"title": "Test"})

    def test_save_and_load_directory_path(self) -> None:
        store = LocalProjectStore()
        bundle = ProjectBundle.empty({"title": "Test"})

        with tempfile.TemporaryDirectory() as tmp:
            result = store.save_bundle(Path(tmp), bundle)
            self.assertEqual(result.name, DEFAULT_BUNDLE_FILENAME)

            loaded = store.load_bundle(Path(tmp))
            self.assertEqual(loaded.project_metadata, {"title": "Test"})

    def test_load_bundle_rejects_missing_file(self) -> None:
        store = LocalProjectStore()

        with self.assertRaises(ValidationError):
            store.load_bundle(Path("/nonexistent/path/bundle.json"))

    def test_load_bundle_rejects_invalid_json(self) -> None:
        store = LocalProjectStore()

        with tempfile.TemporaryDirectory() as tmp:
            bad_file = Path(tmp) / "bad.json"
            bad_file.write_text("not valid json{{{{", encoding="utf-8")

            with self.assertRaises(ValidationError):
                store.load_bundle(bad_file)

    def test_validate_bundle_accepts_valid_bundle(self) -> None:
        store = LocalProjectStore()
        bundle = ProjectBundle.empty()

        result = store.validate_bundle(bundle)

        self.assertTrue(result)

    def test_validate_bundle_rejects_non_bundle(self) -> None:
        store = LocalProjectStore()

        with self.assertRaises(ValidationError):
            store.validate_bundle({"schema_version": "0.1.0"})

    def test_create_bundle_from_managers(self) -> None:
        store = LocalProjectStore()

        scene_manager = SceneManager()
        scene_manager.create_scene("project-1", "Opening Scene")

        shot_manager = ShotManager()
        shot_manager.create_shot("scene-1", "Wide Shot")

        asset_manager = AssetManager()
        asset_manager.import_asset("project-1", "image", "hero.png")

        character_manager = CharacterManager()
        character_manager.create_character("project-1", "Elena")

        timeline_manager = TimelineManager()
        timeline_manager.create_timeline("project-1", "Main Timeline")

        afl_engine = AFLEngine()
        afl_engine.validate_structure("scene-ref-1", {"title": "Opening"})

        export_manager = PromptExportManager()
        export_manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        plugin_manager = PluginManager()
        plugin_manager.register_plugin("test-plugin", "1.0.0")

        workspace = Workspace()
        workspace.activate("project-1")

        bundle = store.create_bundle(
            project_metadata={"title": "Test Film"},
            workspace=workspace,
            scene_manager=scene_manager,
            shot_manager=shot_manager,
            timeline_manager=timeline_manager,
            asset_manager=asset_manager,
            character_manager=character_manager,
            afl_engine=afl_engine,
            prompt_export_manager=export_manager,
            plugin_manager=plugin_manager,
        )

        self.assertEqual(bundle.project_metadata, {"title": "Test Film"})
        self.assertIsNotNone(bundle.workspace_state)
        self.assertEqual(len(bundle.scenes), 1)
        self.assertEqual(len(bundle.shots), 1)
        self.assertEqual(len(bundle.assets), 1)
        self.assertEqual(len(bundle.characters), 1)
        self.assertEqual(len(bundle.timelines), 1)
        self.assertEqual(len(bundle.afl_reports), 1)
        self.assertEqual(len(bundle.export_artifacts), 1)
        self.assertEqual(len(bundle.plugins), 1)


class IntegrationTest(unittest.TestCase):
    def test_full_save_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as project_root_str:
            project_root = Path(project_root_str) / "my-film"

            # Build in-memory state
            pm = ProjectManager()
            metadata = pm.create_project(project_root, "My Film")

            workspace = Workspace()
            workspace.activate(metadata.project_id)

            scene_manager = SceneManager()
            scene = scene_manager.create_scene(metadata.project_id, "Opening Scene", "Intro")

            shot_manager = ShotManager()
            shot_manager.create_shot(scene.scene_id, "Wide Shot")

            timeline_manager = TimelineManager()
            timeline_manager.create_timeline(metadata.project_id, "Main Timeline")

            asset_manager = AssetManager()
            asset_manager.import_asset(metadata.project_id, "image", "hero.png", "/path/to/hero.png")

            character_manager = CharacterManager()
            character_manager.create_character(metadata.project_id, "Elena", "Protagonist")

            afl_engine = AFLEngine()
            afl_engine.validate_structure(scene.scene_id, {"title": "Opening Scene"})

            export_manager = PromptExportManager()
            export_manager.create_export_artifact(scene.scene_id, "image_prompt", "Wide shot of Elena.")

            plugin_manager = PluginManager()
            plugin_manager.register_plugin("export-plugin", "1.0.0", capabilities=["export"])

            # Create bundle
            store = LocalProjectStore()
            bundle = store.create_bundle(
                project_metadata=metadata,
                workspace=workspace,
                scene_manager=scene_manager,
                shot_manager=shot_manager,
                timeline_manager=timeline_manager,
                asset_manager=asset_manager,
                character_manager=character_manager,
                afl_engine=afl_engine,
                prompt_export_manager=export_manager,
                plugin_manager=plugin_manager,
            )

            # Save and reload
            bundle_path = store.save_bundle(project_root, bundle)
            self.assertTrue(bundle_path.exists())
            self.assertEqual(bundle_path.name, DEFAULT_BUNDLE_FILENAME)

            loaded = store.load_bundle(project_root)

            # Verify roundtrip
            self.assertEqual(loaded.schema_version, CURRENT_BUNDLE_VERSION)
            self.assertEqual(loaded.project_metadata["title"], "My Film")
            self.assertIsNotNone(loaded.workspace_state)
            self.assertEqual(len(loaded.scenes), 1)
            self.assertEqual(loaded.scenes[0]["title"], "Opening Scene")
            self.assertEqual(len(loaded.shots), 1)
            self.assertEqual(len(loaded.timelines), 1)
            self.assertEqual(len(loaded.assets), 1)
            self.assertEqual(len(loaded.characters), 1)
            self.assertEqual(len(loaded.afl_reports), 1)
            self.assertEqual(len(loaded.export_artifacts), 1)
            self.assertEqual(len(loaded.plugins), 1)
            self.assertEqual(loaded.plugins[0]["name"], "export-plugin")


if __name__ == "__main__":
    unittest.main()
