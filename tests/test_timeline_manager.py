"""Tests for the first minimal Timeline Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.timeline import (
    TIMELINE_STATE_ARCHIVED,
    TIMELINE_STATE_DRAFT,
    TimelineItem,
    TimelineRecord,
    TimelineRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.timeline_manager import TimelineManager


class TimelineManagerImplementationTests(unittest.TestCase):
    def test_create_timeline_returns_record(self) -> None:
        manager = TimelineManager()

        timeline = manager.create_timeline("project-123", "Main Timeline")

        self.assertIsInstance(timeline, TimelineRecord)
        self.assertTrue(timeline.timeline_id.startswith("timeline-"))
        self.assertEqual(timeline.project_id, "project-123")
        self.assertEqual(timeline.title, "Main Timeline")
        self.assertEqual(timeline.state, TIMELINE_STATE_DRAFT)
        self.assertEqual(timeline.items, ())

    def test_create_timeline_rejects_empty_project_id(self) -> None:
        manager = TimelineManager()

        with self.assertRaises(ValidationError):
            manager.create_timeline("   ", "Main Timeline")

    def test_create_timeline_rejects_empty_title(self) -> None:
        manager = TimelineManager()

        with self.assertRaises(ValidationError):
            manager.create_timeline("project-123", "   ")

    def test_list_timelines_all_and_filtered(self) -> None:
        manager = TimelineManager()
        a = manager.create_timeline("project-1", "A")
        b = manager.create_timeline("project-2", "B")

        all_timelines = manager.list_timelines()
        project_one = manager.list_timelines("project-1")

        self.assertEqual({t.timeline_id for t in all_timelines}, {a.timeline_id, b.timeline_id})
        self.assertEqual([t.timeline_id for t in project_one], [a.timeline_id])

    def test_get_timeline_returns_existing(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        fetched = manager.get_timeline(created.timeline_id)

        self.assertEqual(fetched.timeline_id, created.timeline_id)

    def test_get_timeline_rejects_missing(self) -> None:
        manager = TimelineManager()

        with self.assertRaises(ValidationError):
            manager.get_timeline("timeline-missing")

    def test_update_timeline_title(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        updated = manager.update_timeline(created.timeline_id, title="Renamed Timeline")

        self.assertEqual(updated.title, "Renamed Timeline")
        self.assertEqual(updated.timeline_id, created.timeline_id)

    def test_archive_timeline_preserves_items(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")
        manager.add_item(created.timeline_id, "scene", "scene-1")

        archived = manager.archive_timeline(created.timeline_id)

        self.assertEqual(archived.state, TIMELINE_STATE_ARCHIVED)
        self.assertIsNotNone(archived.archived_at)
        self.assertEqual(len(archived.items), 1)

    def test_add_item_assigns_auto_order_index(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        t1 = manager.add_item(created.timeline_id, "scene", "scene-1")
        t2 = manager.add_item(created.timeline_id, "shot", "shot-1")

        self.assertEqual(t1.items[0].order_index, 0)
        self.assertEqual(t2.items[1].order_index, 1)

    def test_add_item_accepts_explicit_order_index(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        updated = manager.add_item(created.timeline_id, "scene", "scene-1", order_index=5)

        self.assertEqual(updated.items[0].order_index, 5)

    def test_add_item_rejects_negative_order_index(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        with self.assertRaises(ValidationError):
            manager.add_item(created.timeline_id, "scene", "scene-1", order_index=-1)

    def test_add_item_rejects_empty_item_type(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        with self.assertRaises(ValidationError):
            manager.add_item(created.timeline_id, "   ", "scene-1")

    def test_remove_item_removes_by_item_id(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")
        with_item = manager.add_item(created.timeline_id, "scene", "scene-1")
        item_id = with_item.items[0].item_id

        removed = manager.remove_item(created.timeline_id, item_id)

        self.assertEqual(removed.items, ())

    def test_remove_item_rejects_missing_item(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")

        with self.assertRaises(ValidationError):
            manager.remove_item(created.timeline_id, "item-missing")

    def test_move_item_updates_order_index(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")
        with_item = manager.add_item(created.timeline_id, "scene", "scene-1")
        item_id = with_item.items[0].item_id

        moved = manager.move_item(created.timeline_id, item_id, 10)

        self.assertEqual(moved.items[0].order_index, 10)

    def test_move_item_rejects_negative_order_index(self) -> None:
        manager = TimelineManager()
        created = manager.create_timeline("project-123", "Main Timeline")
        with_item = manager.add_item(created.timeline_id, "scene", "scene-1")
        item_id = with_item.items[0].item_id

        with self.assertRaises(ValidationError):
            manager.move_item(created.timeline_id, item_id, -1)

    def test_timeline_record_to_ref_and_dict(self) -> None:
        manager = TimelineManager()
        timeline = manager.create_timeline("project-123", "Main Timeline")

        ref = timeline.to_ref()
        data = timeline.to_dict()

        self.assertIsInstance(ref, TimelineRef)
        self.assertEqual(ref.timeline_id, timeline.timeline_id)
        self.assertEqual(data["timeline_id"], timeline.timeline_id)
        self.assertEqual(data["state"], TIMELINE_STATE_DRAFT)

    def test_timeline_record_from_dict(self) -> None:
        manager = TimelineManager()
        timeline = manager.create_timeline("project-123", "Main Timeline")

        restored = TimelineRecord.from_dict(timeline.to_dict())

        self.assertEqual(restored.timeline_id, timeline.timeline_id)
        self.assertEqual(restored.project_id, "project-123")
        self.assertEqual(restored.title, "Main Timeline")

    def test_timeline_manager_still_reports_not_ready(self) -> None:
        manager = TimelineManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()
