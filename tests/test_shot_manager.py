"""Tests for the first minimal Shot Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.shot import (
    SHOT_STATE_ARCHIVED,
    SHOT_STATE_DRAFT,
    ShotRecord,
    ShotRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.shot_manager import ShotManager


class ShotManagerImplementationTests(unittest.TestCase):
    def test_create_shot_returns_shot_record(self) -> None:
        manager = ShotManager()

        shot = manager.create_shot("scene-123", "Opening Shot", "Establish subject.")

        self.assertIsInstance(shot, ShotRecord)
        self.assertTrue(shot.shot_id.startswith("shot-"))
        self.assertEqual(shot.scene_id, "scene-123")
        self.assertEqual(shot.title, "Opening Shot")
        self.assertEqual(shot.purpose, "Establish subject.")
        self.assertEqual(shot.order_index, 0)
        self.assertEqual(shot.state, SHOT_STATE_DRAFT)

    def test_create_shot_trims_scene_title_and_purpose(self) -> None:
        manager = ShotManager()

        shot = manager.create_shot(" scene-123 ", " Opening Shot ", " Purpose ")

        self.assertEqual(shot.scene_id, "scene-123")
        self.assertEqual(shot.title, "Opening Shot")
        self.assertEqual(shot.purpose, "Purpose")

    def test_create_shot_assigns_next_order_index_per_scene(self) -> None:
        manager = ShotManager()

        first = manager.create_shot("scene-1", "First")
        second = manager.create_shot("scene-1", "Second")
        other_scene = manager.create_shot("scene-2", "Other Scene First")

        self.assertEqual(first.order_index, 0)
        self.assertEqual(second.order_index, 1)
        self.assertEqual(other_scene.order_index, 0)

    def test_create_shot_accepts_explicit_order_index(self) -> None:
        manager = ShotManager()

        shot = manager.create_shot("scene-1", "Insert", order_index=7)

        self.assertEqual(shot.order_index, 7)

    def test_create_shot_rejects_empty_scene_id(self) -> None:
        manager = ShotManager()

        with self.assertRaises(ValidationError):
            manager.create_shot("   ", "Opening Shot")

    def test_create_shot_rejects_empty_title(self) -> None:
        manager = ShotManager()

        with self.assertRaises(ValidationError):
            manager.create_shot("scene-123", "   ")

    def test_create_shot_rejects_negative_order_index(self) -> None:
        manager = ShotManager()

        with self.assertRaises(ValidationError):
            manager.create_shot("scene-123", "Opening Shot", order_index=-1)

    def test_list_shots_returns_all_or_scene_filtered(self) -> None:
        manager = ShotManager()
        first = manager.create_shot("scene-1", "First")
        second = manager.create_shot("scene-2", "Second")

        all_shots = manager.list_shots()
        scene_one_shots = manager.list_shots("scene-1")

        self.assertEqual({shot.shot_id for shot in all_shots}, {first.shot_id, second.shot_id})
        self.assertEqual([shot.shot_id for shot in scene_one_shots], [first.shot_id])

    def test_list_shots_orders_by_scene_and_order_index(self) -> None:
        manager = ShotManager()
        second = manager.create_shot("scene-1", "Second", order_index=2)
        first = manager.create_shot("scene-1", "First", order_index=1)

        ordered = manager.list_shots("scene-1")

        self.assertEqual([shot.shot_id for shot in ordered], [first.shot_id, second.shot_id])

    def test_get_shot_returns_existing_shot(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot")

        fetched = manager.get_shot(created.shot_id)

        self.assertEqual(fetched.shot_id, created.shot_id)
        self.assertEqual(fetched.title, "Opening Shot")

    def test_get_shot_rejects_missing_shot(self) -> None:
        manager = ShotManager()

        with self.assertRaises(ValidationError):
            manager.get_shot("shot-missing")

    def test_update_shot_updates_title_and_purpose(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot", "Old purpose")

        updated = manager.update_shot(
            created.shot_id,
            title="Renamed Shot",
            purpose="New purpose",
        )

        self.assertEqual(updated.title, "Renamed Shot")
        self.assertEqual(updated.purpose, "New purpose")
        self.assertEqual(updated.scene_id, created.scene_id)
        self.assertEqual(updated.shot_id, created.shot_id)

    def test_update_shot_rejects_empty_title_when_provided(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot")

        with self.assertRaises(ValidationError):
            manager.update_shot(created.shot_id, title="   ")

    def test_archive_shot_marks_shot_archived(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot")

        archived = manager.archive_shot(created.shot_id)

        self.assertEqual(archived.state, SHOT_STATE_ARCHIVED)
        self.assertIsNotNone(archived.archived_at)

    def test_reorder_shot_updates_order_index(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot")

        reordered = manager.reorder_shot(created.shot_id, 5)

        self.assertEqual(reordered.order_index, 5)

    def test_reorder_shot_rejects_negative_order_index(self) -> None:
        manager = ShotManager()
        created = manager.create_shot("scene-123", "Opening Shot")

        with self.assertRaises(ValidationError):
            manager.reorder_shot(created.shot_id, -1)

    def test_shot_record_to_ref_and_dict(self) -> None:
        manager = ShotManager()
        shot = manager.create_shot("scene-123", "Opening Shot")

        shot_ref = shot.to_ref()
        data = shot.to_dict()

        self.assertIsInstance(shot_ref, ShotRef)
        self.assertEqual(shot_ref.shot_id, shot.shot_id)
        self.assertEqual(shot_ref.scene_id, "scene-123")
        self.assertEqual(shot_ref.title, "Opening Shot")
        self.assertEqual(data["shot_id"], shot.shot_id)
        self.assertEqual(data["state"], SHOT_STATE_DRAFT)

    def test_shot_record_from_dict(self) -> None:
        manager = ShotManager()
        shot = manager.create_shot("scene-123", "Opening Shot")

        restored = ShotRecord.from_dict(shot.to_dict())

        self.assertEqual(restored.shot_id, shot.shot_id)
        self.assertEqual(restored.scene_id, "scene-123")
        self.assertEqual(restored.title, "Opening Shot")

    def test_shot_manager_still_reports_not_ready(self) -> None:
        manager = ShotManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()
