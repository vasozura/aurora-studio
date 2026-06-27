"""Tests for the first minimal Scene Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.scene import (
    SCENE_STATE_ARCHIVED,
    SCENE_STATE_DRAFT,
    SceneRecord,
    SceneRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.scene_manager import SceneManager


class SceneManagerImplementationTests(unittest.TestCase):
    def test_create_scene_returns_scene_record(self) -> None:
        manager = SceneManager()

        scene = manager.create_scene("project-123", "Opening Scene", "Introduce the world.")

        self.assertIsInstance(scene, SceneRecord)
        self.assertTrue(scene.scene_id.startswith("scene-"))
        self.assertEqual(scene.project_id, "project-123")
        self.assertEqual(scene.title, "Opening Scene")
        self.assertEqual(scene.purpose, "Introduce the world.")
        self.assertEqual(scene.state, SCENE_STATE_DRAFT)

    def test_create_scene_trims_title_and_purpose(self) -> None:
        manager = SceneManager()

        scene = manager.create_scene(" project-123 ", " Opening Scene ", " Purpose ")

        self.assertEqual(scene.project_id, "project-123")
        self.assertEqual(scene.title, "Opening Scene")
        self.assertEqual(scene.purpose, "Purpose")

    def test_create_scene_rejects_empty_project_id(self) -> None:
        manager = SceneManager()

        with self.assertRaises(ValidationError):
            manager.create_scene("   ", "Opening Scene")

    def test_create_scene_rejects_empty_title(self) -> None:
        manager = SceneManager()

        with self.assertRaises(ValidationError):
            manager.create_scene("project-123", "   ")

    def test_list_scenes_returns_all_or_project_filtered(self) -> None:
        manager = SceneManager()
        first = manager.create_scene("project-1", "First")
        second = manager.create_scene("project-2", "Second")

        all_scenes = manager.list_scenes()
        project_one_scenes = manager.list_scenes("project-1")

        self.assertEqual({scene.scene_id for scene in all_scenes}, {first.scene_id, second.scene_id})
        self.assertEqual([scene.scene_id for scene in project_one_scenes], [first.scene_id])

    def test_get_scene_returns_existing_scene(self) -> None:
        manager = SceneManager()
        created = manager.create_scene("project-123", "Opening Scene")

        fetched = manager.get_scene(created.scene_id)

        self.assertEqual(fetched.scene_id, created.scene_id)
        self.assertEqual(fetched.title, "Opening Scene")

    def test_get_scene_rejects_missing_scene(self) -> None:
        manager = SceneManager()

        with self.assertRaises(ValidationError):
            manager.get_scene("scene-missing")

    def test_update_scene_updates_title_and_purpose(self) -> None:
        manager = SceneManager()
        created = manager.create_scene("project-123", "Opening Scene", "Old purpose")

        updated = manager.update_scene(
            created.scene_id,
            title="Renamed Scene",
            purpose="New purpose",
        )

        self.assertEqual(updated.title, "Renamed Scene")
        self.assertEqual(updated.purpose, "New purpose")
        self.assertEqual(updated.project_id, created.project_id)
        self.assertEqual(updated.scene_id, created.scene_id)

    def test_update_scene_rejects_empty_title_when_provided(self) -> None:
        manager = SceneManager()
        created = manager.create_scene("project-123", "Opening Scene")

        with self.assertRaises(ValidationError):
            manager.update_scene(created.scene_id, title="   ")

    def test_archive_scene_marks_scene_archived(self) -> None:
        manager = SceneManager()
        created = manager.create_scene("project-123", "Opening Scene")

        archived = manager.archive_scene(created.scene_id)

        self.assertEqual(archived.state, SCENE_STATE_ARCHIVED)
        self.assertIsNotNone(archived.archived_at)

    def test_scene_record_to_ref_and_dict(self) -> None:
        manager = SceneManager()
        scene = manager.create_scene("project-123", "Opening Scene")

        scene_ref = scene.to_ref()
        data = scene.to_dict()

        self.assertIsInstance(scene_ref, SceneRef)
        self.assertEqual(scene_ref.scene_id, scene.scene_id)
        self.assertEqual(scene_ref.title, "Opening Scene")
        self.assertEqual(data["scene_id"], scene.scene_id)
        self.assertEqual(data["state"], SCENE_STATE_DRAFT)

    def test_scene_record_from_dict(self) -> None:
        manager = SceneManager()
        scene = manager.create_scene("project-123", "Opening Scene")

        restored = SceneRecord.from_dict(scene.to_dict())

        self.assertEqual(restored.scene_id, scene.scene_id)
        self.assertEqual(restored.project_id, "project-123")
        self.assertEqual(restored.title, "Opening Scene")

    def test_scene_manager_still_reports_not_ready(self) -> None:
        manager = SceneManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()
