"""TASK-000056: Asset Browser Pack tests."""

import json
import tempfile
import unittest
from pathlib import Path


class TestAssetRecordV2Fields(unittest.TestCase):
    def _make(self, **kw):
        from aurora_studio.contracts.asset import AssetRecord
        return AssetRecord(
            asset_id="a1", project_id="p1", asset_type="image",
            display_name="Hero", state="active", created_at="t", modified_at="t",
            **kw
        )

    def test_defaults(self):
        r = self._make()
        self.assertEqual(r.description, "")
        self.assertEqual(r.tags, ())
        self.assertEqual(r.usage_count, 0)
        self.assertEqual(r.notes, "")

    def test_with_metadata(self):
        r = self._make(description="A hero", tags=("hero", "main"), usage_count=3, notes="note")
        self.assertEqual(r.description, "A hero")
        self.assertEqual(r.tags, ("hero", "main"))
        self.assertEqual(r.usage_count, 3)

    def test_to_dict_tags_is_list(self):
        r = self._make(tags=("a", "b"))
        d = r.to_dict()
        self.assertIsInstance(d["tags"], list)
        self.assertEqual(d["tags"], ["a", "b"])

    def test_from_dict_backward_compat(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = {"asset_id": "a1", "project_id": "p1", "asset_type": "image",
             "display_name": "Hero", "state": "active", "created_at": "t", "modified_at": "t"}
        r = AssetRecord.from_dict(d)
        self.assertEqual(r.description, "")
        self.assertEqual(r.tags, ())
        self.assertEqual(r.usage_count, 0)

    def test_from_dict_with_new_fields(self):
        from aurora_studio.contracts.asset import AssetRecord
        d = {"asset_id": "a1", "project_id": "p1", "asset_type": "image",
             "display_name": "Hero", "state": "active", "created_at": "t", "modified_at": "t",
             "description": "desc", "tags": ["x", "y"], "usage_count": 5, "notes": "n"}
        r = AssetRecord.from_dict(d)
        self.assertEqual(r.description, "desc")
        self.assertEqual(r.tags, ("x", "y"))
        self.assertEqual(r.usage_count, 5)


class TestParseTags(unittest.TestCase):
    def test_empty(self):
        from aurora_studio.modules.asset_manager import parse_tags
        self.assertEqual(parse_tags(""), ())

    def test_comma_separated(self):
        from aurora_studio.modules.asset_manager import parse_tags
        self.assertEqual(parse_tags("hero, main, bg"), ("hero", "main", "bg"))

    def test_strips_whitespace(self):
        from aurora_studio.modules.asset_manager import parse_tags
        self.assertEqual(parse_tags("  a ,  b  "), ("a", "b"))


class TestAssetManagerUpdateMetadata(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.asset_manager import AssetManager
        self.mgr = AssetManager()
        self.a = self.mgr.import_asset("p1", "image", "Hero")

    def test_update_description(self):
        r = self.mgr.update_asset_metadata(self.a.asset_id, description="cool")
        self.assertEqual(r.description, "cool")

    def test_update_tags_string(self):
        r = self.mgr.update_asset_metadata(self.a.asset_id, tags="a,b")
        self.assertEqual(r.tags, ("a", "b"))

    def test_update_tags_list(self):
        r = self.mgr.update_asset_metadata(self.a.asset_id, tags=["x", "y"])
        self.assertEqual(r.tags, ("x", "y"))

    def test_update_notes(self):
        r = self.mgr.update_asset_metadata(self.a.asset_id, notes="note")
        self.assertEqual(r.notes, "note")

    def test_empty_display_name_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_asset_metadata(self.a.asset_id, display_name="")

    def test_empty_asset_type_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_asset_metadata(self.a.asset_id, asset_type="")

    def test_unknown_field_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_asset_metadata(self.a.asset_id, bad_field="x")

    def test_mark_missing_alias(self):
        r = self.mgr.mark_missing(self.a.asset_id)
        self.assertEqual(r.state, "missing")

    def test_archive_alias(self):
        r = self.mgr.archive(self.a.asset_id)
        self.assertEqual(r.state, "archived")

    def test_usage_count_negative_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_asset_metadata(self.a.asset_id, usage_count=-1)


class TestAssetDetailViewModel(unittest.TestCase):
    def test_from_record(self):
        from aurora_studio.modules.asset_manager import AssetManager
        from aurora_studio.ui.view_models import AssetDetailViewModel
        mgr = AssetManager()
        a = mgr.import_asset("p1", "image", "Hero")
        a2 = mgr.update_asset_metadata(a.asset_id, description="d", tags="t1,t2", notes="n")
        vm = AssetDetailViewModel.from_record(a2)
        self.assertEqual(vm.description, "d")
        self.assertEqual(vm.tags, ("t1", "t2"))
        self.assertEqual(vm.notes, "n")
        self.assertEqual(vm.status, "active")

    def test_to_dict_json_serializable(self):
        from aurora_studio.modules.asset_manager import AssetManager
        from aurora_studio.ui.view_models import AssetDetailViewModel
        mgr = AssetManager()
        a = mgr.import_asset("p1", "image", "Hero")
        a2 = mgr.update_asset_metadata(a.asset_id, tags="x,y")
        vm = AssetDetailViewModel.from_record(a2)
        d = vm.to_dict()
        json.dumps(d)  # must not raise


class TestUISessionAssetDetail(unittest.TestCase):
    def setUp(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        svc = ApplicationService()
        self._tmpdir = tempfile.TemporaryDirectory()
        svc.create_project(self._tmpdir.name, "P")
        self.sess = UISession(svc)
        r = self.sess.import_asset("image", "Hero", "")
        self.asset_id = r.payload["asset_id"]


    def tearDown(self):
        if hasattr(self, '_tmpdir'):
            self._tmpdir.cleanup()

    def test_get_asset_detail(self):
        r = self.sess.get_asset_detail(self.asset_id)
        self.assertTrue(r.ok)
        self.assertIn("asset_id", r.payload)

    def test_update_asset_metadata(self):
        r = self.sess.update_asset_metadata(self.asset_id, {"description": "cool", "tags": "a,b"})
        self.assertTrue(r.ok)

    def test_parse_asset_tags(self):
        r = self.sess.parse_asset_tags("x, y, z")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 3)

    def test_empty_display_name_returns_fail(self):
        r = self.sess.update_asset_metadata(self.asset_id, {"display_name": ""})
        self.assertFalse(r.ok)

    def test_get_unknown_asset_returns_fail(self):
        r = self.sess.get_asset_detail("no-such-id")
        self.assertFalse(r.ok)


class TestAssetBundlePersistence(unittest.TestCase):
    def test_save_load_preserves_metadata(self):
        import tempfile
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            sess = UISession(svc)
            r = sess.import_asset("image", "Hero", "")
            aid = r.payload["asset_id"]
            sess.update_asset_metadata(aid, {"description": "my desc", "tags": "a,b", "notes": "n"})
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            a = svc2.asset_manager.get_asset(aid)
            self.assertEqual(a.description, "my desc")
            self.assertEqual(a.tags, ("a", "b"))
            self.assertEqual(a.notes, "n")


class TestDesktopAssetMethods(unittest.TestCase):
    def test_methods_exist(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        for name in ("load_selected_asset_detail", "apply_asset_metadata_changes",
                     "clear_asset_detail_form"):
            self.assertTrue(hasattr(DesktopShell, name), f"Missing: {name}")

    def test_headless_smoke(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertTrue(result.get("ok"))


if __name__ == "__main__":
    unittest.main()
