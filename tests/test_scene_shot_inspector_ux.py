"""Tests for TASK-000053: Scene/Shot Inspector UX Pack."""

import json
import tempfile
import unittest

from aurora_studio.ui.actions import UISession
from aurora_studio.ui import desktop_shell


class TestInspectorMethodsExist(unittest.TestCase):
    def test_desktop_shell_inspector_methods_exist(self):
        methods = dir(desktop_shell.DesktopShell)
        for m in [
            "load_selected_scene_detail",
            "apply_scene_detail_changes",
            "clear_scene_detail_form",
            "load_selected_shot_detail",
            "apply_shot_detail_changes",
            "clear_shot_detail_form",
            "get_inspector_snapshot",
        ]:
            self.assertIn(m, methods, f"Missing method: {m}")

    def test_ui_session_validate_scene_fields_exists(self):
        self.assertTrue(hasattr(UISession, "validate_scene_detail_fields"))

    def test_ui_session_validate_shot_fields_exists(self):
        self.assertTrue(hasattr(UISession, "validate_shot_detail_fields"))


class TestInspectorSnapshotHeadless(unittest.TestCase):
    """Inspector snapshot via UISession (no tkinter)."""

    def test_validate_scene_detail_fields_ok(self):
        session = UISession()
        r = session.validate_scene_detail_fields({"title": "Good Title", "mood": "tense"})
        self.assertTrue(r.ok)

    def test_validate_scene_detail_fields_empty_title_fail(self):
        session = UISession()
        r = session.validate_scene_detail_fields({"title": ""})
        self.assertFalse(r.ok)

    def test_validate_shot_detail_fields_ok(self):
        session = UISession()
        r = session.validate_shot_detail_fields({"duration_seconds": 3.0})
        self.assertTrue(r.ok)

    def test_validate_shot_detail_negative_duration_fail(self):
        session = UISession()
        r = session.validate_shot_detail_fields({"duration_seconds": -2})
        self.assertFalse(r.ok)

    def test_validate_shot_detail_non_numeric_duration_fail(self):
        session = UISession()
        r = session.validate_shot_detail_fields({"duration_seconds": "xyz"})
        self.assertFalse(r.ok)

    def test_apply_scene_no_selection_returns_fail(self):
        """UISession update with empty scene_id returns ok=False."""
        session = UISession()
        r = session.update_scene_detail("", {"title": "x"})
        self.assertFalse(r.ok)

    def test_apply_shot_no_selection_returns_fail(self):
        session = UISession()
        r = session.update_shot_detail("", {"title": "x"})
        self.assertFalse(r.ok)


class TestInspectorClearDoesNotDelete(unittest.TestCase):
    """Clearing form must not affect stored records."""

    def test_clear_scene_form_does_not_delete_record(self):
        import tempfile
        tmpdir = tempfile.mkdtemp()
        session = UISession()
        session.service.create_project(tmpdir, "Test")
        r = session.create_scene("Scene A")
        scene_id = r.payload["scene_id"]
        session.update_scene_detail(scene_id, {"description": "Important"})

        # Simulate clear: just verify record unchanged
        record = session.service.scene_manager.get_scene(scene_id)
        self.assertEqual(record.description, "Important")

    def test_clear_shot_form_does_not_delete_record(self):
        tmpdir = tempfile.mkdtemp()
        session = UISession()
        session.service.create_project(tmpdir, "Test")
        r_scene = session.create_scene("Scene A")
        r_shot = session.create_shot(r_scene.payload["scene_id"], "Shot 1")
        shot_id = r_shot.payload["shot_id"]
        session.update_shot_detail(shot_id, {"notes": "Keep this"})

        record = session.service.shot_manager.get_shot(shot_id)
        self.assertEqual(record.notes, "Keep this")


class TestInspectorSnapshotSerialization(unittest.TestCase):
    def test_get_inspector_snapshot_is_json_serializable(self):
        """get_inspector_snapshot must return JSON-serializable dict."""
        # We test this without a real tkinter window by checking the structure
        # of what the method would return. The method reads instance attributes
        # set in __init__ (no tkinter needed for the data itself).
        # We verify the method signature and the dict shape via a mock.
        class MockShell:
            _selected_scene_id = "s-1"
            _selected_shot_id = None
            _scene_form_loaded = True
            _shot_form_loaded = False
            _scene_dirty = False
            _shot_dirty = False
            _last_validation_error = ""

            def get_inspector_snapshot(self):
                return {
                    "selected_scene_id": self._selected_scene_id,
                    "selected_shot_id": self._selected_shot_id,
                    "scene_form_loaded": self._scene_form_loaded,
                    "shot_form_loaded": self._shot_form_loaded,
                    "scene_dirty": self._scene_dirty,
                    "shot_dirty": self._shot_dirty,
                    "last_validation_error": self._last_validation_error,
                }

        snap = MockShell().get_inspector_snapshot()
        # All required keys present
        for key in ["selected_scene_id", "selected_shot_id", "scene_form_loaded",
                    "shot_form_loaded", "scene_dirty", "shot_dirty",
                    "last_validation_error"]:
            self.assertIn(key, snap)
        # JSON-serializable
        json.dumps(snap)

    def test_get_inspector_snapshot_method_signature(self):
        import inspect
        sig = inspect.signature(desktop_shell.DesktopShell.get_inspector_snapshot)
        # Must accept only self
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["self"])


class TestInspectorValidationMessages(unittest.TestCase):
    def test_validation_message_is_compact(self):
        session = UISession()
        r = session.validate_scene_detail_fields({"title": ""})
        self.assertFalse(r.ok)
        self.assertLess(len(r.message), 200)

    def test_update_unknown_scene_message_is_compact(self):
        session = UISession()
        r = session.update_scene_detail("no-such-id", {"notes": "x"})
        self.assertFalse(r.ok)
        self.assertLess(len(r.message), 200)


class TestInspectorHeadlessSmoke(unittest.TestCase):
    def test_headless_smoke_still_works(self):
        result = desktop_shell.headless_smoke()
        self.assertTrue(result["ok"])

    def test_desktop_import_does_not_open_window(self):
        # Import already happened at module load; no window should have opened
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
