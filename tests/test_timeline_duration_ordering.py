"""Tests for TASK-000055: Timeline Duration and Ordering Pack."""

import json
import tempfile
import unittest

from aurora_studio.modules.timeline_manager import TimelineManager
from aurora_studio.modules.shot_manager import ShotManager
from aurora_studio.ui.view_models import TimelineSummaryViewModel
from aurora_studio.ui.actions import UISession
from aurora_studio.ui import desktop_shell


class TestTimelineSummary(unittest.TestCase):
    def setUp(self):
        self.tl_mgr = TimelineManager()
        self.shot_mgr = ShotManager()
        self.tl = self.tl_mgr.create_timeline("p1", "Main")

        # Create shots with known durations
        self.sh1 = self.shot_mgr.create_shot("s1", "Shot A")
        self.shot_mgr.update_shot_details(self.sh1.shot_id, duration_seconds=4.0)
        self.sh2 = self.shot_mgr.create_shot("s1", "Shot B")
        self.shot_mgr.update_shot_details(self.sh2.shot_id, duration_seconds=6.0)
        self.sh3 = self.shot_mgr.create_shot("s1", "Shot C")
        # sh3 has no duration (default 0.0)

    def test_total_duration_from_shot_durations(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh2.shot_id)
        summary = self.tl_mgr.get_timeline_summary(
            self.tl.timeline_id, shot_manager=self.shot_mgr
        )
        self.assertAlmostEqual(summary["total_duration_seconds"], 10.0)

    def test_missing_shot_duration_counts_as_zero(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh3.shot_id)
        summary = self.tl_mgr.get_timeline_summary(
            self.tl.timeline_id, shot_manager=self.shot_mgr
        )
        self.assertAlmostEqual(summary["total_duration_seconds"], 4.0)

    def test_scene_item_contributes_zero_duration(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "scene", "s1")
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        summary = self.tl_mgr.get_timeline_summary(
            self.tl.timeline_id, shot_manager=self.shot_mgr
        )
        self.assertAlmostEqual(summary["total_duration_seconds"], 4.0)

    def test_item_count_summary(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "scene", "s1")
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh2.shot_id)
        summary = self.tl_mgr.get_timeline_summary(self.tl.timeline_id)
        self.assertEqual(summary["item_count"], 3)

    def test_scene_shot_count_summary(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "scene", "s1")
        self.tl_mgr.add_item(self.tl.timeline_id, "scene", "s2")
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        summary = self.tl_mgr.get_timeline_summary(self.tl.timeline_id)
        self.assertEqual(summary["scene_item_count"], 2)
        self.assertEqual(summary["shot_item_count"], 1)

    def test_summary_without_shot_manager(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        summary = self.tl_mgr.get_timeline_summary(self.tl.timeline_id)
        # No shot_manager → duration is 0
        self.assertEqual(summary["total_duration_seconds"], 0.0)
        self.assertEqual(summary["shot_item_count"], 1)

    def test_summary_is_json_serializable(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        summary = self.tl_mgr.get_timeline_summary(
            self.tl.timeline_id, shot_manager=self.shot_mgr
        )
        json.dumps(summary)

    def test_ordered_items_in_summary(self):
        self.tl_mgr.add_item(self.tl.timeline_id, "scene", "s1")
        self.tl_mgr.add_item(self.tl.timeline_id, "shot", self.sh1.shot_id)
        summary = self.tl_mgr.get_timeline_summary(self.tl.timeline_id)
        orders = [it["order_index"] for it in summary["ordered_items"]]
        self.assertEqual(orders, sorted(orders))
        for it in summary["ordered_items"]:
            self.assertIn("timeline_id", it)
            self.assertIn("item_id", it)


class TestTimelineNormalization(unittest.TestCase):
    def test_normalize_timeline_order(self):
        mgr = TimelineManager()
        tl = mgr.create_timeline("p1", "T")
        tl = mgr.add_item(tl.timeline_id, "scene", "s1", order_index=10)
        tl = mgr.add_item(tl.timeline_id, "shot", "sh1", order_index=20)
        tl = mgr.add_item(tl.timeline_id, "shot", "sh2", order_index=30)

        tl = mgr.normalize_timeline_order(tl.timeline_id)
        items = mgr.list_items(tl.timeline_id)
        orders = [it.order_index for it in items]
        self.assertEqual(orders, [0, 1, 2])

    def test_repair_duplicate_order_indexes(self):
        from aurora_studio.contracts.timeline import TimelineItem, TimelineRecord, utc_now_iso
        mgr = TimelineManager()
        tl = mgr.create_timeline("p1", "T")
        # Manually inject duplicates via replace_timelines
        items = (
            TimelineItem(item_id="i1", item_type="scene", target_id="s1", order_index=5),
            TimelineItem(item_id="i2", item_type="shot", target_id="sh1", order_index=5),
            TimelineItem(item_id="i3", item_type="shot", target_id="sh2", order_index=7),
        )
        now = utc_now_iso()
        record = TimelineRecord(
            timeline_id=tl.timeline_id, project_id="p1", title="T",
            items=items, state="draft", created_at=now, modified_at=now,
        )
        mgr.replace_timelines([record])
        repaired = mgr.repair_duplicate_order_indexes(tl.timeline_id)
        repaired_items = mgr.list_items(tl.timeline_id)
        orders = [it.order_index for it in repaired_items]
        self.assertEqual(len(set(orders)), len(orders))  # no duplicates

    def test_repair_clean_timeline_unchanged(self):
        mgr = TimelineManager()
        tl = mgr.create_timeline("p1", "T")
        tl = mgr.add_item(tl.timeline_id, "scene", "s1", order_index=0)
        tl = mgr.add_item(tl.timeline_id, "shot", "sh1", order_index=1)
        # Already clean
        repaired = mgr.repair_duplicate_order_indexes(tl.timeline_id)
        items = mgr.list_items(repaired.timeline_id)
        orders = [it.order_index for it in items]
        self.assertEqual(sorted(orders), orders)

    def test_bundle_save_load_preserves_order(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore
        from aurora_studio.persistence.rehydration import BundleRehydrator
        from aurora_studio.modules.timeline_manager import TimelineManager

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "T")
            tl = svc.timeline_manager.create_timeline("p1", "Main")
            svc.timeline_manager.add_item(tl.timeline_id, "scene", "s1", order_index=0)
            svc.timeline_manager.add_item(tl.timeline_id, "shot", "sh1", order_index=1)
            svc.timeline_manager.add_item(tl.timeline_id, "shot", "sh2", order_index=2)

            store = LocalProjectStore()
            bundle = store.create_bundle(timeline_manager=svc.timeline_manager)
            path = store.save_bundle(tmp, bundle)

            new_mgr = TimelineManager()
            bundle2 = store.load_bundle(path)
            BundleRehydrator().rehydrate(bundle2, timeline_manager=new_mgr)
            items = new_mgr.list_items(tl.timeline_id)
            orders = [it.order_index for it in items]
            self.assertEqual(orders, sorted(orders))
            self.assertEqual(len(items), 3)


class TestTimelineSummaryViewModel(unittest.TestCase):
    def test_from_summary_all_fields(self):
        summary = {
            "timeline_id": "t1",
            "item_count": 3,
            "scene_item_count": 1,
            "shot_item_count": 2,
            "total_duration_seconds": 9.5,
            "ordered_items": [{"item_id": "i1", "timeline_id": "t1",
                               "item_type": "scene", "target_id": "s1", "order_index": 0}],
        }
        vm = TimelineSummaryViewModel.from_summary(summary)
        self.assertEqual(vm.timeline_id, "t1")
        self.assertEqual(vm.item_count, 3)
        self.assertEqual(vm.scene_item_count, 1)
        self.assertEqual(vm.shot_item_count, 2)
        self.assertAlmostEqual(vm.total_duration_seconds, 9.5)
        self.assertEqual(len(vm.ordered_items), 1)

    def test_to_dict_serializable(self):
        summary = {
            "timeline_id": "t1", "item_count": 2, "scene_item_count": 1,
            "shot_item_count": 1, "total_duration_seconds": 5.0, "ordered_items": [],
        }
        vm = TimelineSummaryViewModel.from_summary(summary)
        d = vm.to_dict()
        json.dumps(d)
        self.assertIn("timeline_id", d)
        self.assertIn("total_duration_seconds", d)
        self.assertIn("ordered_items", d)
        self.assertIsInstance(d["ordered_items"], list)


class TestUISessionTimelineSummary(unittest.TestCase):
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
        self.session.update_shot_detail(self.shot_id, {"duration_seconds": 5.0})

    def test_get_timeline_summary_ok(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        r = self.session.get_timeline_summary(self.timeline_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["item_count"], 2)
        self.assertAlmostEqual(r.payload["total_duration_seconds"], 5.0)
        self.assertEqual(r.payload["scene_item_count"], 1)
        self.assertEqual(r.payload["shot_item_count"], 1)

    def test_get_timeline_summary_serializable(self):
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        r = self.session.get_timeline_summary(self.timeline_id)
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_normalize_timeline_order(self):
        self.session.add_scene_to_timeline(self.timeline_id, self.scene_id)
        self.session.add_shot_to_timeline(self.timeline_id, self.shot_id)
        r = self.session.normalize_timeline_order(self.timeline_id)
        self.assertTrue(r.ok)


class TestDesktopShellTimelineSummary(unittest.TestCase):
    def test_refresh_timeline_summary_method_exists(self):
        self.assertIn("refresh_timeline_summary", dir(desktop_shell.DesktopShell))

    def test_headless_smoke_still_works(self):
        result = desktop_shell.headless_smoke()
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
