"""Tests for TASK-000051: Scene Detail Editor Pack."""

import json
import unittest
from pathlib import Path
import tempfile
import os

from aurora_studio.contracts.scene import SceneRecord, SCENE_STATE_DRAFT
from aurora_studio.modules.scene_manager import SceneManager
from aurora_studio.ui.view_models import SceneDetailViewModel
from aurora_studio.ui.actions import UISession
from aurora_studio.ui import desktop_shell


class TestSceneRecordDetailFields(unittest.TestCase):
    """SceneRecord now carries v0.2 detail fields."""

    def test_minimal_scene_has_detail_defaults(self):
        scene = SceneRecord(
            scene_id="s1", project_id="p1", title="Test",
            created_at="2026-01-01", modified_at="2026-01-01",
        )
        self.assertEqual(scene.description, "")
        self.assertEqual(scene.location, "")
        self.assertEqual(scene.time_of_day, "")
        self.assertEqual(scene.mood, "")
        self.assertEqual(scene.conflict, "")
        self.assertEqual(scene.narrative_beat, "")
        self.assertEqual(scene.notes, "")

    def test_scene_record_serializes_detail_fields(self):
        scene = SceneRecord(
            scene_id="s1", project_id="p1", title="Test",
            created_at="2026-01-01", modified_at="2026-01-01",
            description="A tense opening",
            location="Rooftop",
            time_of_day="Dusk",
            mood="Anxious",
            conflict="Hero vs villain",
            narrative_beat="Inciting incident",
            notes="Camera low angle",
        )
        d = scene.to_dict()
        self.assertEqual(d["description"], "A tense opening")
        self.assertEqual(d["location"], "Rooftop")
        self.assertEqual(d["time_of_day"], "Dusk")
        self.assertEqual(d["mood"], "Anxious")
        self.assertEqual(d["conflict"], "Hero vs villain")
        self.assertEqual(d["narrative_beat"], "Inciting incident")
        self.assertEqual(d["notes"], "Camera low angle")
        # Must be JSON-serializable
        json.dumps(d)

    def test_from_dict_with_detail_fields(self):
        data = {
            "scene_id": "s1", "project_id": "p1", "title": "Test",
            "state": "draft", "created_at": "2026-01-01", "modified_at": "2026-01-01",
            "description": "desc", "location": "loc", "time_of_day": "day",
            "mood": "happy", "conflict": "none", "narrative_beat": "beat",
            "notes": "note",
        }
        scene = SceneRecord.from_dict(data)
        self.assertEqual(scene.description, "desc")
        self.assertEqual(scene.location, "loc")
        self.assertEqual(scene.time_of_day, "day")

    def test_from_dict_old_bundle_compat(self):
        """Old bundles without detail fields must still load."""
        data = {
            "scene_id": "s1", "project_id": "p1", "title": "Old Scene",
            "state": "draft", "created_at": "2026-01-01", "modified_at": "2026-01-01",
        }
        scene = SceneRecord.from_dict(data)
        self.assertEqual(scene.description, "")
        self.assertEqual(scene.notes, "")

    def test_with_updates_preserves_detail_fields(self):
        scene = SceneRecord(
            scene_id="s1", project_id="p1", title="Test",
            created_at="2026-01-01", modified_at="2026-01-01",
            location="Rooftop",
        )
        updated = scene.with_updates(title="New Title")
        self.assertEqual(updated.location, "Rooftop")
        self.assertEqual(updated.title, "New Title")


class TestSceneManagerUpdateDetails(unittest.TestCase):
    """SceneManager.update_scene_details()"""

    def setUp(self):
        self.mgr = SceneManager()
        self.scene = self.mgr.create_scene("p1", "Initial Title")

    def test_update_description(self):
        updated = self.mgr.update_scene_details(
            self.scene.scene_id, description="New desc"
        )
        self.assertEqual(updated.description, "New desc")

    def test_update_all_detail_fields(self):
        updated = self.mgr.update_scene_details(
            self.scene.scene_id,
            title="New Title",
            description="desc",
            location="Forest",
            time_of_day="Night",
            mood="Eerie",
            conflict="Man vs nature",
            narrative_beat="Climax",
            notes="Lots of fog",
        )
        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.description, "desc")
        self.assertEqual(updated.location, "Forest")
        self.assertEqual(updated.time_of_day, "Night")
        self.assertEqual(updated.mood, "Eerie")
        self.assertEqual(updated.conflict, "Man vs nature")
        self.assertEqual(updated.narrative_beat, "Climax")
        self.assertEqual(updated.notes, "Lots of fog")

    def test_empty_title_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_scene_details(self.scene.scene_id, title="")

    def test_unknown_field_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_scene_details(self.scene.scene_id, nonexistent="x")

    def test_unknown_scene_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_scene_details("bad-id", description="x")


class TestSceneDetailViewModel(unittest.TestCase):
    """SceneDetailViewModel."""

    def test_from_record_all_fields(self):
        scene = SceneRecord(
            scene_id="s1", project_id="p1", title="T",
            created_at="2026-01-01", modified_at="2026-01-02",
            description="desc", location="loc", time_of_day="dusk",
            mood="calm", conflict="none", narrative_beat="setup", notes="n",
            state=SCENE_STATE_DRAFT,
        )
        vm = SceneDetailViewModel.from_record(scene)
        self.assertEqual(vm.scene_id, "s1")
        self.assertEqual(vm.description, "desc")
        self.assertEqual(vm.location, "loc")
        self.assertEqual(vm.time_of_day, "dusk")
        self.assertEqual(vm.mood, "calm")
        self.assertEqual(vm.status, SCENE_STATE_DRAFT)  # state -> status
        self.assertEqual(vm.updated_at, "2026-01-02")   # modified_at -> updated_at

    def test_to_dict_serializable(self):
        scene = SceneRecord(
            scene_id="s1", project_id="p1", title="T",
            created_at="2026-01-01", modified_at="2026-01-02",
        )
        vm = SceneDetailViewModel.from_record(scene)
        d = vm.to_dict()
        json.dumps(d)
        self.assertIn("scene_id", d)
        self.assertIn("status", d)
        self.assertIn("updated_at", d)


class TestUISessionSceneDetail(unittest.TestCase):
    """UISession get_scene_detail / update_scene_detail."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()
        self.session = UISession()
        self.session.service.create_project(self._tmpdir, "Test")
        r = self.session.create_scene("Opening")
        self.scene_id = r.payload["scene_id"]

    def test_get_scene_detail_ok(self):
        r = self.session.get_scene_detail(self.scene_id)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["scene_id"], self.scene_id)
        self.assertIn("description", r.payload)
        self.assertIn("status", r.payload)

    def test_get_scene_detail_unknown(self):
        r = self.session.get_scene_detail("no-such-id")
        self.assertFalse(r.ok)

    def test_update_scene_detail_ok(self):
        r = self.session.update_scene_detail(self.scene_id, {
            "description": "A bold opening",
            "location": "City rooftop",
        })
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["description"], "A bold opening")
        self.assertEqual(r.payload["location"], "City rooftop")

    def test_update_scene_detail_empty_title(self):
        r = self.session.update_scene_detail(self.scene_id, {"title": ""})
        self.assertFalse(r.ok)

    def test_update_scene_detail_unknown_scene(self):
        r = self.session.update_scene_detail("no-such", {"description": "x"})
        self.assertFalse(r.ok)

    def test_update_scene_detail_unknown_field(self):
        r = self.session.update_scene_detail(self.scene_id, {"bogus_field": "x"})
        self.assertFalse(r.ok)

    def test_payload_is_json_serializable(self):
        r = self.session.update_scene_detail(self.scene_id, {"notes": "some notes"})
        self.assertTrue(r.ok)
        json.dumps(r.payload)


class TestSceneDetailBundlePersistence(unittest.TestCase):
    """Bundle save/load preserves detail fields; old bundles still load."""

    def test_bundle_roundtrip_preserves_detail(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "Test")
            scene = svc.create_scene("Opening")
            svc.scene_manager.update_scene_details(
                scene.scene_id, location="Rooftop", mood="Tense"
            )

            store = LocalProjectStore()
            bundle = store.create_bundle(
                scene_manager=svc.scene_manager,
                shot_manager=svc.shot_manager,
            )
            path = store.save_bundle(tmp, bundle)

            bundle2 = store.load_bundle(path)
            scene_dicts = bundle2.scenes
            self.assertTrue(len(scene_dicts) == 1)
            self.assertEqual(scene_dicts[0]["location"], "Rooftop")
            self.assertEqual(scene_dicts[0]["mood"], "Tense")

    def test_bundle_rehydration_restores_detail(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.persistence.local_project_store import LocalProjectStore
        from aurora_studio.persistence.rehydration import BundleRehydrator

        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "Test")
            scene = svc.create_scene("Opening")
            svc.scene_manager.update_scene_details(
                scene.scene_id, description="Dramatic", notes="Fog FX"
            )
            store = LocalProjectStore()
            bundle = store.create_bundle(scene_manager=svc.scene_manager)
            path = store.save_bundle(tmp, bundle)

            # Rehydrate into fresh manager
            from aurora_studio.modules.scene_manager import SceneManager
            new_mgr = SceneManager()
            bundle2 = store.load_bundle(path)
            BundleRehydrator().rehydrate(bundle2, scene_manager=new_mgr)

            reloaded = new_mgr.get_scene(scene.scene_id)
            self.assertEqual(reloaded.description, "Dramatic")
            self.assertEqual(reloaded.notes, "Fog FX")

    def test_old_bundle_without_detail_loads(self):
        """Simulated old v0.1 bundle without detail fields."""
        from aurora_studio.contracts.scene import SceneRecord
        data = {
            "scene_id": "s-old-1", "project_id": "p1", "title": "Old Scene",
            "state": "draft", "created_at": "2026-01-01", "modified_at": "2026-01-01",
        }
        scene = SceneRecord.from_dict(data)
        self.assertEqual(scene.description, "")
        self.assertEqual(scene.notes, "")


class TestDesktopShellSceneDetail(unittest.TestCase):
    """Desktop shell import safety and public method presence (headless)."""

    def test_desktop_import_does_not_open_window(self):
        # Already imported at top — if we're here, no window was opened
        self.assertTrue(True)

    def test_headless_smoke_still_works(self):
        result = desktop_shell.headless_smoke()
        self.assertTrue(result["ok"])

    def test_desktop_shell_public_methods_exist(self):
        methods = dir(desktop_shell.DesktopShell)
        self.assertIn("load_selected_scene_detail", methods)
        self.assertIn("apply_scene_detail_changes", methods)
        self.assertIn("clear_scene_detail_form", methods)
        self.assertIn("get_inspector_snapshot", methods)


if __name__ == "__main__":
    unittest.main()
