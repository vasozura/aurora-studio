"""Tests for TASK-000094: Autosave Implementation Pack."""

import json
import os
import shutil
import tempfile
import threading
import unittest


def _mgr():
    from aurora_studio.modules.autosave_manager import AutosaveManager
    return AutosaveManager()


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


BUNDLE = {"schema_version": "0.3", "test": True}


class TestAutosaveContracts(unittest.TestCase):
    def test_state_json_serializable(self):
        from aurora_studio.contracts.autosave import AutosaveState
        json.dumps(AutosaveState().to_dict())

    def test_record_json_serializable(self):
        from aurora_studio.contracts.autosave import AutosaveRecord
        r = AutosaveRecord(autosave_id="x", project_id="p", autosave_path="/p/.autosave/a.json")
        json.dumps(r.to_dict())

    def test_recovery_report_json_serializable(self):
        from aurora_studio.contracts.autosave import AutosaveRecoveryReport
        r = AutosaveRecoveryReport(has_recovery=False, autosave_path="", is_valid_json=False, message="")
        json.dumps(r.to_dict())


class TestAutosaveDisabledByDefault(unittest.TestCase):
    def test_disabled_by_default(self):
        mgr = _mgr()
        self.assertFalse(mgr.get_state().enabled)

    def test_status_disabled_by_default(self):
        mgr = _mgr()
        self.assertEqual(mgr.get_state().status, "disabled")

    def test_not_dirty_by_default(self):
        mgr = _mgr()
        self.assertFalse(mgr.get_state().dirty)


class TestEnableDisableAutosave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_enable_autosave(self):
        mgr = _mgr()
        state = mgr.enable_autosave(self.tmp)
        self.assertTrue(state.enabled)

    def test_disable_autosave(self):
        mgr = _mgr()
        mgr.enable_autosave(self.tmp)
        state = mgr.disable_autosave()
        self.assertFalse(state.enabled)

    def test_enable_status_idle(self):
        mgr = _mgr()
        state = mgr.enable_autosave(self.tmp)
        self.assertEqual(state.status, "idle")

    def test_disable_status_disabled(self):
        mgr = _mgr()
        mgr.enable_autosave(self.tmp)
        state = mgr.disable_autosave()
        self.assertEqual(state.status, "disabled")


class TestDirtyState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_mark_dirty_when_enabled(self):
        mgr = _mgr()
        mgr.enable_autosave(self.tmp)
        state = mgr.mark_dirty("test change")
        self.assertTrue(state.dirty)
        self.assertEqual(state.status, "dirty")

    def test_mark_dirty_when_disabled_noop(self):
        mgr = _mgr()
        state = mgr.mark_dirty("test change")
        self.assertFalse(state.dirty)  # disabled — no effect

    def test_clear_dirty(self):
        mgr = _mgr()
        mgr.enable_autosave(self.tmp)
        mgr.mark_dirty()
        state = mgr.clear_dirty()
        self.assertFalse(state.dirty)


class TestWriteAutosave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _enabled_mgr(self):
        mgr = _mgr()
        mgr.enable_autosave(self.tmp)
        return mgr

    def test_write_autosave_creates_file(self):
        mgr = self._enabled_mgr()
        record = mgr.write_autosave(BUNDLE, self.tmp)
        self.assertTrue(os.path.exists(record.autosave_path))

    def test_autosave_file_in_autosave_dir(self):
        mgr = self._enabled_mgr()
        record = mgr.write_autosave(BUNDLE, self.tmp)
        self.assertIn(".autosave", record.autosave_path)

    def test_autosave_file_is_valid_json(self):
        mgr = self._enabled_mgr()
        record = mgr.write_autosave(BUNDLE, self.tmp)
        with open(record.autosave_path) as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_autosave_does_not_overwrite_manual_bundle(self):
        """The manual bundle aurora_project.json must not be touched."""
        bundle_path = os.path.join(self.tmp, "aurora_project.json")
        with open(bundle_path, "w") as f:
            f.write(json.dumps({"original": True}))
        mgr = self._enabled_mgr()
        mgr.write_autosave(BUNDLE, self.tmp)
        with open(bundle_path) as f:
            content = json.load(f)
        self.assertTrue(content.get("original"))

    def test_write_when_disabled_raises(self):
        mgr = _mgr()
        with self.assertRaises(ValueError):
            mgr.write_autosave(BUNDLE, self.tmp)

    def test_has_recovery_after_write(self):
        mgr = self._enabled_mgr()
        mgr.write_autosave(BUNDLE, self.tmp)
        self.assertTrue(mgr.has_recovery(self.tmp))

    def test_load_autosave_validates_json(self):
        mgr = self._enabled_mgr()
        mgr.write_autosave(BUNDLE, self.tmp)
        data = mgr.load_autosave(self.tmp)
        self.assertIn("schema_version", data)

    def test_discard_autosave_removes_file(self):
        mgr = self._enabled_mgr()
        record = mgr.write_autosave(BUNDLE, self.tmp)
        mgr.discard_autosave(self.tmp)
        self.assertFalse(os.path.exists(record.autosave_path))

    def test_discard_autosave_does_not_touch_bundle(self):
        bundle_path = os.path.join(self.tmp, "aurora_project.json")
        with open(bundle_path, "w") as f:
            f.write(json.dumps({"original": True}))
        mgr = self._enabled_mgr()
        mgr.write_autosave(BUNDLE, self.tmp)
        mgr.discard_autosave(self.tmp)
        self.assertTrue(os.path.exists(bundle_path))

    def test_state_after_write_is_saved(self):
        mgr = self._enabled_mgr()
        mgr.write_autosave(BUNDLE, self.tmp)
        self.assertEqual(mgr.get_state().status, "saved")


class TestNoBackgroundThread(unittest.TestCase):
    def test_no_new_thread_created(self):
        before = threading.active_count()
        mgr = _mgr()
        mgr.enable_autosave(".")
        mgr.mark_dirty()
        after = threading.active_count()
        self.assertEqual(before, after, "No new threads should be created")

    def test_autosave_source_no_thread(self):
        import aurora_studio.modules.autosave_manager as am
        src = open(am.__file__).read()
        self.assertNotIn("Thread(", src)
        self.assertNotIn("threading.Timer", src)


class TestUISessionAutosave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_autosave_state_ok(self):
        r = self.sess.get_autosave_state()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["enabled"])

    def test_enable_autosave_ok(self):
        r = self.sess.enable_autosave(project_path=self.tmp)
        self.assertTrue(r.ok)
        self.assertTrue(r.payload["enabled"])

    def test_disable_autosave_ok(self):
        self.sess.enable_autosave(project_path=self.tmp)
        r = self.sess.disable_autosave()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["enabled"])

    def test_mark_dirty_ok(self):
        self.sess.enable_autosave(project_path=self.tmp)
        r = self.sess.mark_project_dirty("user edit")
        self.assertTrue(r.ok)

    def test_write_autosave_ok(self):
        self.sess.enable_autosave(project_path=self.tmp)
        r = self.sess.write_project_autosave(project_path=self.tmp)
        self.assertTrue(r.ok, r.message)

    def test_write_autosave_disabled_fails(self):
        r = self.sess.write_project_autosave(project_path=self.tmp)
        self.assertFalse(r.ok)

    def test_check_recovery_ok(self):
        r = self.sess.check_autosave_recovery(project_path=self.tmp)
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["has_recovery"])

    def test_discard_recovery_ok(self):
        self.sess.enable_autosave(project_path=self.tmp)
        self.sess.write_project_autosave(project_path=self.tmp)
        r = self.sess.discard_autosave_recovery(project_path=self.tmp)
        self.assertTrue(r.ok)
        self.assertTrue(r.payload["discarded"])

    def test_autosave_payload_serializable(self):
        r = self.sess.get_autosave_state()
        json.dumps(r.payload)


if __name__ == "__main__":
    unittest.main()
