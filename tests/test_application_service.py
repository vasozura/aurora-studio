"""Tests for the minimal Application Service."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.project_bundle import ProjectBundle
from aurora_studio.contracts.scene import SceneRecord
from aurora_studio.contracts.shot import ShotRecord
from aurora_studio.core.errors import ValidationError
from aurora_studio.services import ApplicationService


class ApplicationServiceInitTests(unittest.TestCase):
    def test_initializes_with_default_managers(self) -> None:
        service = ApplicationService()

        self.assertIsNotNone(service.project_manager)
        self.assertIsNotNone(service.workspace)
        self.assertIsNotNone(service.scene_manager)
        self.assertIsNotNone(service.shot_manager)
        self.assertIsNotNone(service.timeline_manager)
        self.assertIsNotNone(service.asset_manager)
        self.assertIsNotNone(service.character_manager)
        self.assertIsNotNone(service.afl_engine)
        self.assertIsNotNone(service.prompt_export_manager)
        self.assertIsNotNone(service.plugin_manager)
        self.assertIsNotNone(service.project_store)

    def test_service_does_not_change_module_readiness(self) -> None:
        from aurora_studio.core.readiness import Readiness
        service = ApplicationService()

        self.assertEqual(service.scene_manager.get_readiness(), Readiness.NOT_READY)
        self.assertEqual(service.shot_manager.get_readiness(), Readiness.NOT_READY)


class CreateProjectTests(unittest.TestCase):
    def test_create_project_returns_metadata_and_activates_workspace(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            metadata = service.create_project(project_root, "My Film")

            self.assertEqual(metadata.title, "My Film")
            state = service.get_workspace_state()
            self.assertEqual(state.active_project_id, metadata.project_id)

    def test_create_project_does_not_create_scenes(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            service.create_project(Path(tmp) / "my-film", "My Film")

            scenes = service.scene_manager.list_scenes()
            self.assertEqual(scenes, [])


class OpenProjectTests(unittest.TestCase):
    def test_open_project_activates_workspace(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            created = service.create_project(project_root, "My Film")

            service2 = ApplicationService()
            opened = service2.open_project(project_root)

            self.assertEqual(opened.project_id, created.project_id)
            state = service2.get_workspace_state()
            self.assertEqual(state.active_project_id, opened.project_id)

    def test_open_project_does_not_rehydrate_managers(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            service.create_project(project_root, "My Film")
            service.create_scene("Opening Scene")

            service2 = ApplicationService()
            service2.open_project(project_root)

            # Managers are fresh — no scenes loaded
            self.assertEqual(service2.scene_manager.list_scenes(), [])


class CreateSceneTests(unittest.TestCase):
    def test_create_scene_requires_active_project(self) -> None:
        service = ApplicationService()

        with self.assertRaises(ValidationError):
            service.create_scene("Opening Scene")

    def test_create_scene_creates_record_and_sets_active_scene(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            service.create_project(Path(tmp) / "my-film", "My Film")
            scene = service.create_scene("Opening Scene", "Establish the world.")

            self.assertIsInstance(scene, SceneRecord)
            self.assertEqual(scene.title, "Opening Scene")
            state = service.get_workspace_state()
            self.assertEqual(state.active_scene_id, scene.scene_id)


class CreateShotTests(unittest.TestCase):
    def test_create_shot_requires_active_project(self) -> None:
        service = ApplicationService()

        with self.assertRaises(ValidationError):
            service.create_shot("scene-123", "Wide Shot")

    def test_create_shot_creates_record_and_sets_active_scene_and_shot(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            service.create_project(Path(tmp) / "my-film", "My Film")
            scene = service.create_scene("Opening Scene")
            shot = service.create_shot(scene.scene_id, "Wide Shot")

            self.assertIsInstance(shot, ShotRecord)
            self.assertEqual(shot.title, "Wide Shot")
            state = service.get_workspace_state()
            self.assertEqual(state.active_scene_id, scene.scene_id)
            self.assertEqual(state.active_shot_id, shot.shot_id)


class SaveLoadBundleTests(unittest.TestCase):
    def test_save_bundle_writes_json_file(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            service.create_project(project_root, "My Film")
            bundle_path = service.save_bundle(project_root)

            self.assertTrue(bundle_path.exists())
            self.assertEqual(bundle_path.name, "aurora_bundle.json")

    def test_load_bundle_returns_project_bundle(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            service.create_project(project_root, "My Film")
            service.save_bundle(project_root)

            bundle = service.load_bundle(project_root)

            self.assertIsInstance(bundle, ProjectBundle)
            self.assertEqual(bundle.project_metadata["title"], "My Film")

    def test_save_bundle_includes_scenes_and_shots(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            service.create_project(project_root, "My Film")
            scene = service.create_scene("Opening Scene")
            service.create_shot(scene.scene_id, "Wide Shot")
            service.save_bundle(project_root)

            bundle = service.load_bundle(project_root)

            self.assertEqual(len(bundle.scenes), 1)
            self.assertEqual(bundle.scenes[0]["title"], "Opening Scene")
            self.assertEqual(len(bundle.shots), 1)
            self.assertEqual(bundle.shots[0]["title"], "Wide Shot")

    def test_load_bundle_does_not_rehydrate_managers(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            service.create_project(project_root, "My Film")
            service.create_scene("Opening Scene")
            service.save_bundle(project_root)

            service2 = ApplicationService()
            service2.load_bundle(project_root)

            # Managers are untouched
            self.assertEqual(service2.scene_manager.list_scenes(), [])
            self.assertIsNone(service2.get_workspace_state().active_project_id)

    def test_get_workspace_state_returns_current_state(self) -> None:
        service = ApplicationService()

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "my-film"
            metadata = service.create_project(project_root, "My Film")
            state = service.get_workspace_state()

            self.assertEqual(state.active_project_id, metadata.project_id)


if __name__ == "__main__":
    unittest.main()
