"""Tests for TASK-000065: JSON Hardening."""

import json
import tempfile
import unittest
from pathlib import Path


def _make_store():
    from aurora_studio.persistence.local_project_store import LocalProjectStore
    return LocalProjectStore()


def _make_bundle(meta=None):
    from aurora_studio.contracts.project_bundle import ProjectBundle, CURRENT_BUNDLE_VERSION
    return ProjectBundle(
        schema_version=CURRENT_BUNDLE_VERSION,
        project_metadata=meta or {"project_id": "p1", "title": "T"},
    )


class TestSchemaVersionPresentOnNewSave(unittest.TestCase):
    def test_schema_version_in_saved_file(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle()
            path = store.save_bundle(tmp, bundle)
            with open(path) as f:
                data = json.load(f)
            self.assertIn("schema_version", data)
            self.assertIsNotNone(data["schema_version"])

    def test_saved_schema_version_is_supported(self):
        from aurora_studio.contracts.project_bundle import _SUPPORTED_VERSIONS
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle()
            path = store.save_bundle(tmp, bundle)
            with open(path) as f:
                data = json.load(f)
            self.assertIn(data["schema_version"], _SUPPORTED_VERSIONS)


class TestOldBundleCompatibility(unittest.TestCase):
    def test_bundle_with_known_old_version_loads(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            old_data = {
                "schema_version": "0.1.0",
                "project_metadata": {"project_id": "old", "title": "Old"},
                "scenes": [],
                "shots": [],
                "timelines": [],
                "assets": [],
                "characters": [],
                "afl_reports": [],
                "export_artifacts": [],
                "plugins": [],
                "asset_links": [],
                "created_at": "",
                "modified_at": "",
            }
            bundle_file.write_text(json.dumps(old_data))
            bundle = store.load_bundle(tmp)
            self.assertEqual(bundle.schema_version, "0.1.0")
            self.assertEqual(bundle.project_metadata["project_id"], "old")

    def test_bundle_without_prompt_templates_field_loads(self):
        """Old bundles missing new collection fields still load."""
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            old_data = {
                "schema_version": "0.1.0",
                "project_metadata": {"project_id": "legacy"},
                "scenes": [],
                "shots": [],
                "timelines": [],
                "assets": [],
                "characters": [],
                "afl_reports": [],
                "export_artifacts": [],
                "plugins": [],
                "asset_links": [],
                "created_at": "",
                "modified_at": "",
            }
            bundle_file.write_text(json.dumps(old_data))
            bundle = store.load_bundle(tmp)
            self.assertEqual(bundle.prompt_templates, ())
            self.assertEqual(bundle.export_profiles, ())


class TestBackupBeforeOverwrite(unittest.TestCase):
    def test_backup_created_on_overwrite(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle()
            store.save_bundle(tmp, bundle)
            # Save again — should create backup
            store.save_bundle(tmp, bundle)
            backup_dir = Path(tmp) / ".backups"
            self.assertTrue(backup_dir.exists())
            backups = list(backup_dir.glob("aurora_bundle.bak.*.json"))
            self.assertGreater(len(backups), 0)

    def test_no_backup_on_first_save(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = _make_bundle()
            store.save_bundle(tmp, bundle)
            backup_dir = Path(tmp) / ".backups"
            backups = list(backup_dir.glob("*.bak.*")) if backup_dir.exists() else []
            self.assertEqual(len(backups), 0)


class TestCorruptJsonHandling(unittest.TestCase):
    def test_corrupt_json_raises_validation_error(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            bundle_file.write_text("{this is not valid json !!!")
            with self.assertRaises(ValidationError):
                store.load_bundle(tmp)

    def test_corrupt_json_error_message_friendly(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            bundle_file.write_text("corrupted!")
            try:
                store.load_bundle(tmp)
                self.fail("Should have raised")
            except ValidationError as exc:
                self.assertIn("corrupt", str(exc).lower())


class TestMissingRequiredSection(unittest.TestCase):
    def test_missing_project_metadata_raises(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            bundle_file.write_text(json.dumps({"schema_version": "0.1.0"}))
            with self.assertRaises(ValidationError):
                store.load_bundle(tmp)

    def test_missing_schema_version_raises(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "aurora_bundle.json"
            bundle_file.write_text(json.dumps({"project_metadata": {}}))
            with self.assertRaises(ValidationError):
                store.load_bundle(tmp)


class TestExportBundleCopy(unittest.TestCase):
    def test_export_bundle_copy_creates_file(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as src_tmp:
            with tempfile.TemporaryDirectory() as dst_tmp:
                store.save_bundle(src_tmp, _make_bundle())
                dst_file = Path(dst_tmp) / "exported.json"
                result = store.export_bundle_copy(src_tmp, dst_file)
                self.assertTrue(result.exists())

    def test_export_bundle_copy_content_valid(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as src_tmp:
            with tempfile.TemporaryDirectory() as dst_tmp:
                store.save_bundle(src_tmp, _make_bundle())
                dst_file = Path(dst_tmp) / "exported.json"
                store.export_bundle_copy(src_tmp, dst_file)
                with open(dst_file) as f:
                    data = json.load(f)
                self.assertIn("schema_version", data)
                self.assertIn("project_metadata", data)

    def test_export_copy_source_not_found_raises(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as dst_tmp:
            with self.assertRaises(ValidationError):
                store.export_bundle_copy("/nonexistent/path", Path(dst_tmp) / "out.json")


class TestImportBundleCopy(unittest.TestCase):
    def test_import_bundle_copy_loads_bundle(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as src_tmp:
            with tempfile.TemporaryDirectory() as dst_tmp:
                bundle = _make_bundle({"project_id": "imported", "title": "Imported"})
                path = store.save_bundle(src_tmp, bundle)
                loaded = store.import_bundle_copy(path, dst_tmp)
                self.assertEqual(loaded.project_metadata["project_id"], "imported")

    def test_import_creates_backup_if_bundle_exists(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as src_tmp:
            with tempfile.TemporaryDirectory() as dst_tmp:
                bundle = _make_bundle()
                src_path = store.save_bundle(src_tmp, bundle)
                store.import_bundle_copy(src_path, dst_tmp)
                # Import again — should create backup
                store.import_bundle_copy(src_path, dst_tmp)
                backup_dir = Path(dst_tmp) / ".backups"
                self.assertTrue(backup_dir.exists())

    def test_import_corrupt_source_raises(self):
        from aurora_studio.core.errors import ValidationError
        store = _make_store()
        with tempfile.TemporaryDirectory() as src_tmp:
            with tempfile.TemporaryDirectory() as dst_tmp:
                corrupt = Path(src_tmp) / "bad.json"
                corrupt.write_text("not json")
                with self.assertRaises(ValidationError):
                    store.import_bundle_copy(corrupt, dst_tmp)


class TestValidateBundleFile(unittest.TestCase):
    def test_valid_bundle_reports_ok(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            store.save_bundle(tmp, _make_bundle())
            report = store.validate_bundle_file(tmp)
            self.assertTrue(report["ok"])
            self.assertEqual(report["errors"], [])

    def test_missing_file_reports_error(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            report = store.validate_bundle_file(tmp)
            self.assertFalse(report["ok"])
            self.assertTrue(len(report["errors"]) > 0)

    def test_corrupt_json_reports_error(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "aurora_bundle.json").write_text("{{bad json")
            report = store.validate_bundle_file(tmp)
            self.assertFalse(report["ok"])

    def test_report_includes_schema_version(self):
        store = _make_store()
        with tempfile.TemporaryDirectory() as tmp:
            store.save_bundle(tmp, _make_bundle())
            report = store.validate_bundle_file(tmp)
            self.assertIn("schema_version", report)


class TestUISessionHardeningMethods(unittest.TestCase):
    def setUp(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        self.sess = UISession(ApplicationService())
        self.tmp = tempfile.mkdtemp()
        self.sess.create_project(self.tmp, "Hardening Project")

    def test_validate_bundle_file_ok(self):
        self.sess.save_bundle(self.tmp)
        r = self.sess.validate_bundle_file(self.tmp)
        self.assertTrue(r.ok)

    def test_export_bundle_copy(self):
        self.sess.save_bundle(self.tmp)
        with tempfile.TemporaryDirectory() as dst:
            dst_file = str(Path(dst) / "export.json")
            r = self.sess.export_bundle_copy(dst_file)
            self.assertTrue(r.ok, r.message)

    def test_import_bundle_copy(self):
        self.sess.save_bundle(self.tmp)
        src_file = str(Path(self.tmp) / "aurora_bundle.json")
        with tempfile.TemporaryDirectory() as dst:
            r = self.sess.import_bundle_copy(src_file)
            self.assertTrue(r.ok, r.message)


class TestExistingBundleStillLoads(unittest.TestCase):
    def test_headless_smoke_still_works(self):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.ui.desktop_shell", "--headless-smoke"],
            capture_output=True, text=True,
            cwd="/sessions/exciting-serene-pascal/mnt/Avrora/aurora-studio",
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )
        self.assertEqual(result.returncode, 0, result.stderr[:500])


if __name__ == "__main__":
    unittest.main()
