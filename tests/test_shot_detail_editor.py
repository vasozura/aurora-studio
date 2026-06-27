"""Tests for TASK-000052: Shot Detail Editor Pack."""

import json
import tempfile
import unittest

from aurora_studio.contracts.shot import ShotRecord, SHOT_STATE_DRAFT
from aurora_studio.modules.shot_manager import ShotManager
from aurora_studio.ui.view_models import ShotDetailViewModel
from aurora_studio.ui.actions import UISession
from aurora_studio.ui import desktop_shell


class TestShotRecordDetailFields(unittest.TestCase):
    def test_minimal_shot_has_detail_defaults(self):
        shot = ShotRecord(
            shot_id="sh1", scene_id="s1", title="Test",
            created_at="2026-01-01", modified_at="2026-01-01",
        )
        self.assertEqual(shot.description, "")
        self.assertEqual(shot.shot_type, "")
        self.assertEqual(shot.camera_angle, "")
        self.assertEqual(shot.camera_movement, "")
        self.assertEqual(shot.framing, "")
        self.assertEqual(shot.lens, "")
        self.assertEqual(shot.duration_seconds, 0.0)
        self.assertEqual(shot.emotion_target, "")
        self.assertEqual(shot.visual_focus, "")
        self.assertEqual(shot.notes, "")
        self.assertEqual(shot.project_id, "")

    def test_shot_record_serializes_detail_fields(self):
        shot = ShotRecord(
            shot_id="sh1", scene_id="s1", title="Test",
            created_at="2026-01-01", modified_at="2026-01-01",
            description="Wide establishing",
            shot_type="WS",
            camera_angle="eye-level",
            camera_movement="static",
            framing="rule-of-thirds",
            lens="35mm",
            duration_seconds=5.5,
            emotion_target="tension",
            visual_focus="protagonist",
            notes="Use blue filter",
            project_id="p1",
        )
        d = shot.to_dict()
        self.assertEqual(d["description"], "Wide establishing")
        self.assertEqual(d["shot_type"], "WS")
        self.assertEqual(d["duration_seconds"], 5.5)
        self.assertEqual(d["project_id"], "p1")
        json.dumps(d)  # must be serializable

    def test_from_dict_with_detail_fields(self):
        data = {
            "shot_id": "sh1", "scene_id": "s1", "title": "T",
            "order_index": 0, "state": "draft",
            "created_at": "2026-01-01", "modified_at": "2026-01-01",
            "shot_type": "CU", "duration_seconds": 3.0, "project_id": "p1",
        }
        shot = ShotRecord.from_dict(data)
        self.assertEqual(shot.shot_type, "CU")
        self.assertEqual(shot.duration_seconds, 3.0)
        self.assertEqual(shot.project_id, "p1")

    def test_from_dict_old_bundle_compat(self):
        data = {
            "shot_id": "sh1", "scene_id": "s1", "title": "Old Shot",
            "order_index": 0, "state": "draft",
            "created_at": "2026-01-01", "modified_at": "2026-01-01",
        }
        shot = ShotRecord.from_dict(data)
        self.assertEqual(shot.description, "")
        self.assertEqual(shot.duration_seconds, 0.0)
        self.assertEqual(shot.project_id, "")

    def test_from_dict_invalid_duration_defaults_to_zero(self):
        data = {
            "shot_id": "sh1", "scene_id": "s1", "title": "T",
            "order_index": 0, "state": "draft",
            "created_at": "2026-01-01", "modified_at": "2026-01-01",
            "duration_seconds": "not-a-number",
        }
        shot = ShotRecord.from_dict(data)
        self.assertEqual(shot.duration_seconds, 0.0)


class TestShotManagerUpdateDetails(unittest.TestCase):
    def setUp(self):
        self.mgr = ShotManager()
        self.shot = self.mgr.create_shot("s1", "Initial Shot")

    def test_update_shot_type(self):
        updated = self.mgr.update_shot_details(self.shot.shot_id, shot_type="CU")
        self.assertEqual(updated.shot_type, "CU")

    def test_update_duration_valid(self):
        updated = self.mgr.update_shot_details(self.shot.shot_id, duration_seconds=4.5)
        self.assertEqual(updated.duration_seconds, 4.5)

    def test_update_duration_zero(self):
        updated = self.mgr.update_shot_details(self.shot.shot_id, duration_seconds=0)
        self.assertEqual(updated.duration_seconds, 0.0)

    def test_update_duration_negative_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_shot_details(self.shot.shot_id, duration_seconds=-1)

    def test_update_duration_non_numeric_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_shot_details(self.shot.shot_id, duration_seconds="abc")

    def test_update_empty_title_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_shot_details(self.shot.shot_id, title="")

    def test_update_unknown_field_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_shot_details(self.shot.shot_id, bogus="x")

    def test_update_unknown_shot_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_shot_details("no-such", shot_type="WS")

    def test_list_shots_by_project_id(self):
        mgr = ShotManager()
        mgr.create_shot("scene-a", "Shot A", project_id="proj-1")
        mgr.create_shot("scene-b", "Shot B", project_id="proj-2")
        mgr.create_shot("scene-a", "Shot C", project_id="proj-1")

        proj1 = mgr.list_shots(project_id="proj-1")
        self.assertEqual(len(proj1), 2)
        proj2 = mgr.list_shots(project_id="proj-2")
        self.assertEqual(len(proj2), 1)


class TestShotDetailViewModel(unittest.TestCase):
    def test_from_record_all_fields(self):
        shot = ShotRecord(
            shot_id="sh1", scene_id="s1", title="T",
            created_at="2026-01-01", modified_at="2026-01-02",
            shot_type="MCU", duration_seconds=3.5,
            state=SHOT_STATE_DRAFT, project_id="p1",
        )
        vm = ShotDetailViewModel.from_record(shot)
        self.assertEqual(vm.shot_id, "sh1")
        self.assertEqual(vm.shot_type, "MCU")
        self.assertEqual(vm.duration_seconds, 3.5)
        self.assertEqual(vm.status, SHOT_STATE_DRAFT)
        self.assertEqual(vm.updated_at, "2026-01-02")
        self.assertEqual(vm.project_id, "p1")

    def test_to_dict_serializable(self):
        shot = ShotRecord(
            shot_id="sh1", scene_id="s1", title="T",
            created_at="2026-01-01", modified_at="2026-01-02",
        )
        vm = ShotDetailViewModel.from_record(shot)
        d = vm.to_dict()
        json.dumps(d)
        self.assertIn("shot_id", d)
        self.assertIn("duration_seconds", d)
        self.assertIn("status", d)


class TestUISessionShotDetail(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self.session = UISession()
        self.session.service.create_project(self._tmpdir, "Test")
        r_scene = self.session.create_scene("Scene A")
        self.scene_id = r_scene.payload["scene_id"]
        r_shot = self.session.create_shot(self.scene_id, "Shot 1")
        self.shot_id = r_shot.payload["shot_id"]

    def test_get_shot_detail_ok(self):
        r = self.session.get_shot_detail(self.shot_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["shot_id"], self.shot_id)
        self.assertIn("duration_seconds", r.payload)

    def test_get_shot_detail_unknown(self):
        r = self.session.get_shot_detail("no-such")
        self.assertFalse(r.ok)

    def test_update_shot_detail_ok(self):
        r = self.session.update_shot_detail(self.shot_id, {
            "shot_type": "CU",
            "camera_angle": "low",
            "duration_seconds": 2.5,
        })
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["shot_type"], "CU")
        self.assertEqual(r.payload["duration_seconds"], 2.5)

    def test_duration_accepts_numeric_string(self):
        r = self.session.update_shot_detail(self.shot_id, {"duration_seconds": "3.0"})
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["duration_seconds"], 3.0)

    def test_duration_rejects_non_numeric(self):
        r = self.session.update_shot_detail(self.shot_id, {"duration_seconds": "abc"})
        self.assertFalse(r.ok)

    def test_duration_rejects_negative(self):
        r = self.session.update_shot_detail(self.shot_id, {"duration_seconds": -1})
        self.assertFalse(r.ok)

    def test_update_empty_title_returns_fail(self):
        r = self.session.update_shot_detail(self.shot_id, {"title": ""})
        self.assertFalse(r.ok)

    def test_payload_is_serializable(self):
        r = self.session.update_shot_detail(self.shot_id, {"notes": "test"})
        self.assertTrue(r.ok)
        json.dumps(r.payload)


class TestShotDetailBundlePersistence(unittest.TestCase):
    def test_bundle_roundtrip_preserves_shot_detail(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "Test")
            scene = svc.create_scene("Scene A")
            shot = svc.shot_manager.create_shot(scene.scene_id, "Shot 1")
            svc.shot_manager.update_shot_details(
                shot.shot_id, shot_type="WS", duration_seconds=5.0, notes="Fog"
            )
            store = LocalProjectStore()
            bundle = store.create_bundle(shot_manager=svc.shot_manager)
            path = store.save_bundle(tmp, bundle)

            bundle2 = store.load_bundle(path)
            self.assertEqual(len(bundle2.shots), 1)
            self.assertEqual(bundle2.shots[0]["shot_type"], "WS")
            self.assertEqual(bundle2.shots[0]["duration_seconds"], 5.0)

    def test_rehydration_restores_shot_detail(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore
        from aurora_studio.persistence.rehydration import BundleRehydrator

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "Test")
            scene = svc.create_scene("Scene A")
            shot = svc.shot_manager.create_shot(scene.scene_id, "Shot 1")
            svc.shot_manager.update_shot_details(
                shot.shot_id, camera_angle="dutch", duration_seconds=2.0
            )
            store = LocalProjectStore()
            bundle = store.create_bundle(shot_manager=svc.shot_manager)
            path = store.save_bundle(tmp, bundle)

            from aurora_studio.modules.shot_manager import ShotManager
            new_mgr = ShotManager()
            bundle2 = store.load_bundle(path)
            BundleRehydrator().rehydrate(bundle2, shot_manager=new_mgr)
            reloaded = new_mgr.get_shot(shot.shot_id)
            self.assertEqual(reloaded.camera_angle, "dutch")
            self.assertEqual(reloaded.duration_seconds, 2.0)


class TestDesktopShellShotDetail(unittest.TestCase):
    def test_desktop_public_shot_methods_exist(self):
        methods = dir(desktop_shell.DesktopShell)
        self.assertIn("load_selected_shot_detail", methods)
        self.assertIn("apply_shot_detail_changes", methods)
        self.assertIn("clear_shot_detail_form", methods)

    def test_headless_smoke_still_works(self):
        result = desktop_shell.headless_smoke()
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
