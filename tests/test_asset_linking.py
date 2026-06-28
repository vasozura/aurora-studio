"""TASK-000057: Asset Linking Pack tests."""

import json
import tempfile
import unittest


class TestAssetLinkManager(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.asset_link_manager import AssetLinkManager
        self.mgr = AssetLinkManager()

    def test_link_scene(self):
        lnk = self.mgr.link("p1", "a1", "scene", "s1")
        self.assertEqual(lnk.asset_id, "a1")
        self.assertEqual(lnk.target_type, "scene")
        self.assertEqual(lnk.target_id, "s1")

    def test_link_shot(self):
        lnk = self.mgr.link("p1", "a1", "shot", "sh1")
        self.assertEqual(lnk.target_type, "shot")

    def test_link_character(self):
        lnk = self.mgr.link("p1", "a1", "character", "c1")
        self.assertEqual(lnk.target_type, "character")

    def test_no_duplicate_links(self):
        self.mgr.link("p1", "a1", "scene", "s1")
        self.mgr.link("p1", "a1", "scene", "s1")
        links = self.mgr.list_links_for_target("scene", "s1")
        self.assertEqual(len(links), 1)

    def test_unlink(self):
        self.mgr.link("p1", "a1", "scene", "s1")
        removed = self.mgr.unlink("a1", "scene", "s1")
        self.assertTrue(removed)
        self.assertEqual(len(self.mgr.list_links_for_target("scene", "s1")), 0)

    def test_unlink_nonexistent(self):
        removed = self.mgr.unlink("no-asset", "scene", "no-scene")
        self.assertFalse(removed)

    def test_list_links_for_target(self):
        self.mgr.link("p1", "a1", "scene", "s1")
        self.mgr.link("p1", "a2", "scene", "s1")
        links = self.mgr.list_links_for_target("scene", "s1")
        self.assertEqual(len(links), 2)

    def test_list_links_for_asset(self):
        self.mgr.link("p1", "a1", "scene", "s1")
        self.mgr.link("p1", "a1", "shot", "sh1")
        links = self.mgr.list_links_for_asset("a1")
        self.assertEqual(len(links), 2)

    def test_invalid_target_type_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.link("p1", "a1", "invalid", "x1")

    def test_empty_asset_id_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.link("p1", "", "scene", "s1")

    def test_empty_target_id_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.link("p1", "a1", "scene", "")

    def test_serialization(self):
        lnk = self.mgr.link("p1", "a1", "scene", "s1")
        d = lnk.to_dict()
        json.dumps(d)  # must not raise
        self.assertIn("link_id", d)

    def test_from_dict_roundtrip(self):
        from aurora_studio.modules.asset_link_manager import AssetLink
        lnk = self.mgr.link("p1", "a1", "scene", "s1", notes="note")
        restored = AssetLink.from_dict(lnk.to_dict())
        self.assertEqual(restored.link_id, lnk.link_id)
        self.assertEqual(restored.notes, "note")

    def test_replace_links(self):
        from aurora_studio.modules.asset_link_manager import AssetLink
        lnk = self.mgr.link("p1", "a1", "scene", "s1")
        mgr2 = type(self.mgr)()
        mgr2.replace_links([AssetLink.from_dict(lnk.to_dict())])
        self.assertEqual(len(mgr2.list_all()), 1)


class TestUISessionAssetLinking(unittest.TestCase):
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

    def test_link_to_scene(self):
        r = self.sess.link_asset_to_scene(self.asset_id, "scene-abc")
        self.assertTrue(r.ok)

    def test_link_to_shot(self):
        r = self.sess.link_asset_to_shot(self.asset_id, "shot-abc")
        self.assertTrue(r.ok)

    def test_link_to_character(self):
        r = self.sess.link_asset_to_character(self.asset_id, "char-abc")
        self.assertTrue(r.ok)

    def test_unlink_from_scene(self):
        self.sess.link_asset_to_scene(self.asset_id, "scene-abc")
        r = self.sess.unlink_asset_from_scene(self.asset_id, "scene-abc")
        self.assertTrue(r.ok)
        self.assertTrue(r.payload["removed"])

    def test_unlink_from_shot(self):
        self.sess.link_asset_to_shot(self.asset_id, "shot-abc")
        r = self.sess.unlink_asset_from_shot(self.asset_id, "shot-abc")
        self.assertTrue(r.ok)

    def test_unlink_from_character(self):
        self.sess.link_asset_to_character(self.asset_id, "char-abc")
        r = self.sess.unlink_asset_from_character(self.asset_id, "char-abc")
        self.assertTrue(r.ok)

    def test_get_linked_assets(self):
        self.sess.link_asset_to_scene(self.asset_id, "scene-x")
        r = self.sess.get_linked_assets("scene", "scene-x")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)

    def test_empty_asset_id_returns_fail(self):
        r = self.sess.link_asset_to_scene("", "scene-x")
        self.assertFalse(r.ok)

    def test_empty_target_id_returns_fail(self):
        r = self.sess.link_asset_to_scene(self.asset_id, "")
        self.assertFalse(r.ok)


class TestAssetLinksPersistence(unittest.TestCase):
    def test_links_survive_save_load(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            sess = UISession(svc)
            r = sess.import_asset("image", "Hero", "")
            aid = r.payload["asset_id"]
            sess.link_asset_to_scene(aid, "scene-123")
            sess.link_asset_to_shot(aid, "shot-456")
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            links = svc2.asset_link_manager.list_links_for_asset(aid)
            self.assertEqual(len(links), 2)


class TestDesktopLinkMethods(unittest.TestCase):
    def test_methods_exist(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        for name in ("link_asset_to_scene", "link_asset_to_shot",
                     "link_asset_to_character", "unlink_asset_from_scene"):
            self.assertTrue(hasattr(DesktopShell, name), f"Missing: {name}")


if __name__ == "__main__":
    unittest.main()
