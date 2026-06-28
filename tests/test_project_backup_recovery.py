"""Tests for TASK-000093: Project Backup / Recovery."""

import json
import os
import shutil
import tempfile
import unittest

BUNDLE_FILE = "aurora_project.json"
BACKUP_DIR = ".backups"

SAMPLE_BUNDLE = json.dumps({"schema_version": "0.3", "project": {"project_id": "p1", "title": "Test"}})


def _write_bundle(path):
    with open(os.path.join(path, BUNDLE_FILE), "w") as f:
        f.write(SAMPLE_BUNDLE)


def _make_backup_mgr():
    from aurora_studio.modules.project_backup import ProjectBackupManager
    return ProjectBackupManager()


def _make_recovery_mgr():
    from aurora_studio.modules.project_recovery import ProjectRecoveryManager
    return ProjectRecoveryManager()


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


class TestBackupContracts(unittest.TestCase):
    def test_backup_record_serializes(self):
        from aurora_studio.contracts.recovery import ProjectBackupRecord
        r = ProjectBackupRecord(
            backup_id="abc", project_id="p1", source_path="/p/bundle.json",
            backup_path="/p/.backups/bundle.json", reason="manual",
            created_at="2026-01-01T00:00:00+00:00", size_bytes=100,
        )
        json.dumps(r.to_dict())

    def test_recovery_candidate_serializes(self):
        from aurora_studio.contracts.recovery import ProjectRecoveryCandidate
        c = ProjectRecoveryCandidate(
            candidate_id="x1", project_id="p1",
            candidate_path="/p/.backups/b.json", candidate_type="backup",
            is_valid_json=True, validation_message="Valid JSON.",
        )
        json.dumps(c.to_dict())

    def test_recovery_report_serializes(self):
        from aurora_studio.contracts.recovery import ProjectRecoveryReport, ProjectRecoveryCandidate
        r = ProjectRecoveryReport(status="candidates_available", candidate_count=0, candidates=())
        json.dumps(r.to_dict())


class TestCreateBackup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_backup_returns_record(self):
        mgr = _make_backup_mgr()
        record = mgr.create_backup(self.tmp)
        self.assertIsNotNone(record.backup_id)
        self.assertTrue(os.path.exists(record.backup_path))

    def test_backup_stored_in_backups_dir(self):
        mgr = _make_backup_mgr()
        record = mgr.create_backup(self.tmp)
        self.assertIn(BACKUP_DIR, record.backup_path)

    def test_backup_does_not_delete_source(self):
        mgr = _make_backup_mgr()
        mgr.create_backup(self.tmp)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, BUNDLE_FILE)))

    def test_backup_size_recorded(self):
        mgr = _make_backup_mgr()
        record = mgr.create_backup(self.tmp)
        self.assertGreater(record.size_bytes, 0)

    def test_create_backup_no_bundle_raises(self):
        empty = tempfile.mkdtemp()
        try:
            with self.assertRaises(FileNotFoundError):
                _make_backup_mgr().create_backup(empty)
        finally:
            shutil.rmtree(empty, ignore_errors=True)


class TestListBackups(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_list_backups_empty(self):
        self.assertEqual(_make_backup_mgr().list_backups(self.tmp), [])

    def test_list_backups_after_create(self):
        mgr = _make_backup_mgr()
        mgr.create_backup(self.tmp)
        self.assertEqual(len(mgr.list_backups(self.tmp)), 1)

    def test_latest_backup(self):
        mgr = _make_backup_mgr()
        mgr.create_backup(self.tmp, "first")
        mgr.create_backup(self.tmp, "second")
        latest = mgr.get_latest_backup(self.tmp)
        self.assertIsNotNone(latest)

    def test_latest_backup_none_when_empty(self):
        self.assertIsNone(_make_backup_mgr().get_latest_backup(self.tmp))


class TestPruneBackups(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_prune_keeps_requested_count(self):
        mgr = _make_backup_mgr()
        import time
        for i in range(5):
            mgr.create_backup(self.tmp, reason=f"b{i}")
            time.sleep(0.01)
        deleted = mgr.prune_backups(self.tmp, keep=3)
        self.assertEqual(deleted, 2)
        self.assertEqual(len(mgr.list_backups(self.tmp)), 3)

    def test_prune_only_deletes_backup_files(self):
        mgr = _make_backup_mgr()
        mgr.create_backup(self.tmp)
        # Put a sentinel file in .backups that should not be deleted
        sentinel = os.path.join(self.tmp, BACKUP_DIR, "keep_me.txt")
        open(sentinel, "w").close()
        mgr.prune_backups(self.tmp, keep=0)
        self.assertTrue(os.path.exists(sentinel))  # txt not touched


class TestScanRecoveryCandidates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scan_empty(self):
        candidates = _make_recovery_mgr().scan_recovery_candidates(self.tmp)
        self.assertEqual(candidates, [])

    def test_scan_finds_backup(self):
        _make_backup_mgr().create_backup(self.tmp)
        candidates = _make_recovery_mgr().scan_recovery_candidates(self.tmp)
        self.assertEqual(len(candidates), 1)

    def test_validate_valid_candidate(self):
        backup = _make_backup_mgr().create_backup(self.tmp)
        valid, msg = _make_recovery_mgr().validate_recovery_candidate(backup.backup_path)
        self.assertTrue(valid)

    def test_reject_corrupt_candidate(self):
        backup_dir = os.path.join(self.tmp, BACKUP_DIR)
        os.makedirs(backup_dir, exist_ok=True)
        corrupt = os.path.join(backup_dir, "aurora_project.20260101T000000.bad.json")
        with open(corrupt, "w") as f:
            f.write("{not valid json{{{")
        valid, msg = _make_recovery_mgr().validate_recovery_candidate(corrupt)
        self.assertFalse(valid)
        self.assertIn("Invalid", msg)


class TestRestoreBackup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_restore_backup_replaces_bundle(self):
        mgr_b = _make_backup_mgr()
        record = mgr_b.create_backup(self.tmp)
        # Corrupt the main bundle
        with open(os.path.join(self.tmp, BUNDLE_FILE), "w") as f:
            f.write("CORRUPTED")
        _make_recovery_mgr().restore_backup(self.tmp, record.backup_path)
        with open(os.path.join(self.tmp, BUNDLE_FILE)) as f:
            content = json.load(f)
        self.assertIn("schema_version", content)

    def test_restore_creates_pre_restore_backup(self):
        mgr_b = _make_backup_mgr()
        record = mgr_b.create_backup(self.tmp)
        _make_recovery_mgr().restore_backup(self.tmp, record.backup_path)
        # Should now have 2 backups (original + pre-restore)
        backups = mgr_b.list_backups(self.tmp)
        self.assertGreaterEqual(len(backups), 2)

    def test_restore_refuses_path_outside_project(self):
        with tempfile.TemporaryDirectory() as outside:
            outside_bundle = os.path.join(outside, "aurora_project.json")
            with open(outside_bundle, "w") as f:
                f.write(SAMPLE_BUNDLE)
            with self.assertRaises(ValueError):
                _make_recovery_mgr().restore_backup(self.tmp, outside_bundle)

    def test_restore_corrupt_backup_raises(self):
        backup_dir = os.path.join(self.tmp, BACKUP_DIR)
        os.makedirs(backup_dir, exist_ok=True)
        corrupt = os.path.join(backup_dir, "aurora_project.20260101T000000.bad.json")
        with open(corrupt, "w") as f:
            f.write("{not valid")
        with self.assertRaises(ValueError):
            _make_recovery_mgr().restore_backup(self.tmp, corrupt)


class TestUISessionBackupRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write_bundle(self.tmp)
        self.sess = _make_session()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_backup_ok(self):
        r = self.sess.create_project_backup(project_path=self.tmp)
        self.assertTrue(r.ok, r.message)
        self.assertIn("backup_id", r.payload)

    def test_create_backup_no_path_fails(self):
        r = self.sess.create_project_backup(project_path="")
        self.assertFalse(r.ok)

    def test_list_backups_ok(self):
        self.sess.create_project_backup(project_path=self.tmp)
        r = self.sess.list_project_backups(project_path=self.tmp)
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)

    def test_scan_recovery_ok(self):
        self.sess.create_project_backup(project_path=self.tmp)
        r = self.sess.scan_project_recovery(project_path=self.tmp)
        self.assertTrue(r.ok)
        self.assertGreater(r.payload["candidate_count"], 0)

    def test_scan_recovery_no_path_fails(self):
        r = self.sess.scan_project_recovery(project_path="")
        self.assertFalse(r.ok)

    def test_backup_payload_serializable(self):
        r = self.sess.create_project_backup(project_path=self.tmp)
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_scan_payload_serializable(self):
        r = self.sess.scan_project_recovery(project_path=self.tmp)
        self.assertTrue(r.ok)
        json.dumps(r.payload)


if __name__ == "__main__":
    unittest.main()
