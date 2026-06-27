"""Tests for TASK-000054: Timeline Minimal Editor Pack."""

import json
import tempfile
import unittest

from aurora_studio.modules.timeline_manager import TimelineManager
from aurora_studio.ui.actions import UISession
from aurora_studio.ui import desktop_shell


class TestTimelineManagerExtended(unittest.TestCase):
    def setUp(self):
        self.mgr = TimelineManager()
        self.tl = self.mgr.create_timeline("p1", "Main TL")
        self.tl = self.mgr.add_item(self.tl.timeline_id, "scene", "s1")
        self.tl = self.mgr.add_item(self.tl.timeline_id, "shot", "sh1")
        self.tl = self.mgr.add_item(self.tl.timeline_id, "shot", "sh2")

    def test_list_items_returns_sorted(self):
        items = self.mgr.list_items(self.tl.timeline_id)
        self.assertEqual(len(items), 3)
        orders = [it.order_index for it in items]
        self.assertEqual(orders, sorted(orders))

    def test_list_items_unknown_timeline_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.list_items("no-such")

    def test_move_item_up(self):
        items_before = self.mgr.list_items(self.tl.timeline_id)
        second_item = items_before[1]
        record = self.mgr.move_item_up(self.tl.timeline_id, second_item.item_id)
        items_after = self.mgr.list_items(record.timeline_id)
        # The moved item should now be first (or at least higher)
        first_target = items_after[0].target_id
        self.assertEqual(first_target, second_item.target_id)

    def test_move_item_down(self):
        items_before = self.mgr.list_items(self.tl.timeline_id)
        first_item = items_before[0]
        record = self.mgr.move_item_down(self.tl.timeline_id, first_item.item_id)
        items_after = self.mgr.list_items(record.timeline_id)
        # First item should now be second
        second_target = items_after[1].target_id
        self.assertEqual(second_target, first_item.target_id)

    def test_move_item_up_at_top_no_change(self):
        items = self.mgr.list_items(self.tl.timeline_id)
        first_id = items[0].item_id
        record = self.mgr.move_item_up(self.tl.timeline_id, first_id)
        items_after = self.mgr.list_items(record.timeline_id)
        self.assertEqual(items_after[0].item_id, first_id)

    def test_move_item_down_at_bottom_no_change(self):
        items = self.mgr.list_items(self.tl.timeline_id)
        last_id = items[-1].item_id
        record = self.mgr.move_item_down(self.tl.timeline_id, last_id)
        items_after = self.mgr.list_items(record.timeline_id)
        self.assertEqual(items_after[-1].item_id, last_id)

    def test_move_item_up_unknown_item_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.move_item_up(self.tl.timeline_id, "no-such")

    def test_move_item_down_unknown_item_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.move_item_down(self.tl.timeline_id, "no-such")


class TestUISessionTimelineExtended(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self.session = UISession()
        self.session.service.create_project(self._tmpdir, "Test")
        r_tl = self.session.create_timeline("Main TL")
        self.timeline_id = r_tl.payload["timeline_id"]
        r_scene = self.session.create_scene("Scene A")
        self.scene_id = r_scene.payload["scene_id"]
        r_shot = self.session.create_shot(self.scene_id, "Shot 1")
        self.shot_id = r_shot.payload["shot_id"]

    def test_add_scene_to_timeline(self):
        r = self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["item_count"], 1)

    def test_add_shot_to_timeline(self):
        r = self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["item_count"], 1)

    def test_add_scene_no_timeline_returns_fail(self):
        r = self.session.add_scene_to_timeline("", self.scene_id)
        self.assertFalse(r.ok)

    def test_add_scene_no_scene_returns_fail(self):
        r = self.session.add_scene_to_timeline(self.timeline_id, "")
        self.assertFalse(r.ok)

    def test_add_shot_no_timeline_returns_fail(self):
        r = self.session.add_shot_to_timeline("", self.shot_id)
        self.assertFalse(r.ok)

    def test_add_shot_no_shot_returns_fail(self):
        r = self.session.add_shot_to_timeline(self.timeline_id, "")
        self.assertFalse(r.ok)

    def test_list_timeline_items(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        r = self.session.list_timeline_items(self.timeline_id)
        self.assertTrue(r.ok)
        items = r.payload["items"]
        self.assertEqual(len(items), 2)
        # timeline_id must be exposed in each item
        for item in items:
            self.assertEqual(item["timeline_id"], self.timeline_id)

    def test_move_timeline_item_up(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        items_r = self.session.list_timeline_items(self.timeline_id)
        second_item_id = items_r.payload["items"][1]["item_id"]
        r = self.session.move_timeline_item_up(self.timeline_id, second_item_id)
        self.assertTrue(r.ok)

    def test_move_timeline_item_down(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        items_r = self.session.list_timeline_items(self.timeline_id)
        first_item_id = items_r.payload["items"][0]["item_id"]
        r = self.session.move_timeline_item_down(self.timeline_id, first_item_id)
        self.assertTrue(r.ok)

    def test_remove_item(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        items_r = self.session.list_timeline_items(self.timeline_id)
        item_id = items_r.payload["items"][0]["item_id"]
        r = self.session.remove_timeline_item(self.timeline_id, item_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["item_count"], 0)

    def test_order_stable_after_multiple_moves(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        r = self.session.list_timeline_items(self.timeline_id)
        items = r.payload["items"]
        first_id = items[0]["item_id"]
        # Move second item up
        self.session.move_timeline_item_up(self.timeline_id, items[1]["item_id"])
        r2 = self.session.list_timeline_items(self.timeline_id)
        orders = [it["order_index"] for it in r2.payload["items"]]
        self.assertEqual(orders, sorted(orders))


class TestTimelineItemBundlePersistence(unittest.TestCase):
    def test_bundle_roundtrip_preserves_timeline_items(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "Test")
            tl = svc.timeline_manager.create_timeline("p1", "Main")
            svc.timeline_manager.add_item(tl.timeline_id, "scene", "s1")
            svc.timeline_manager.add_item(tl.timeline_id, "shot", "sh1")

            store = LocalProjectStore()
            bundle = store.create_bundle(timeline_manager=svc.timeline_manager)
            path = store.save_bundle(tmp, bundle)

            bundle2 = store.load_bundle(path)
            tl_dict = bundle2.timelines[0]
            self.assertEqual(len(tl_dict["items"]), 2)


class TestDesktopShellTimelineButtons(unittest.TestCase):
    def test_desktop_timeline_methods_exist(self):
        methods = dir(desktop_shell.DesktopShell)
        for m in [
            "add_selected_scene_to_timeline",
            "add_selected_shot_to_timeline",
            "move_timeline_item_up",
            "move_timeline_item_down",
            "refresh_timeline_summary",
        ]:
            self.assertIn(m, methods, f"Missing: {m}")

    def test_headless_smoke_still_works(self):
        result = desktop_shell.headless_smoke()
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
