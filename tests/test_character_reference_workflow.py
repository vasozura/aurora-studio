"""TASK-000059: Character Reference Workflow Pack tests."""

import json
import tempfile
import unittest


class TestCharacterReferenceDataclass(unittest.TestCase):
    def test_defaults(self):
        from aurora_studio.contracts.character import CharacterReference
        r = CharacterReference(asset_id="a1")
        self.assertEqual(r.reference_type, "other")
        self.assertFalse(r.is_primary)
        self.assertEqual(r.notes, "")

    def test_to_dict_json_serializable(self):
        from aurora_studio.contracts.character import CharacterReference
        r = CharacterReference(asset_id="a1", reference_type="face", is_primary=True)
        json.dumps(r.to_dict())

    def test_from_dict(self):
        from aurora_studio.contracts.character import CharacterReference
        d = {"asset_id": "a1", "reference_type": "face", "is_primary": True, "notes": "n"}
        r = CharacterReference.from_dict(d)
        self.assertEqual(r.asset_id, "a1")
        self.assertEqual(r.reference_type, "face")
        self.assertTrue(r.is_primary)


class TestOldReferenceAssetIdsCompat(unittest.TestCase):
    def test_old_bundle_loads_correctly(self):
        from aurora_studio.contracts.character import CharacterRecord
        d = {"character_id": "c1", "project_id": "p1", "display_name": "Alice",
             "state": "active", "created_at": "t", "modified_at": "t",
             "reference_asset_ids": ["a1", "a2"]}
        r = CharacterRecord.from_dict(d)
        self.assertEqual(r.reference_asset_ids, ("a1", "a2"))
        self.assertEqual(r.reference_assets, ())

    def test_new_bundle_loads_structured_refs(self):
        from aurora_studio.contracts.character import CharacterRecord
        d = {"character_id": "c1", "project_id": "p1", "display_name": "Alice",
             "state": "active", "created_at": "t", "modified_at": "t",
             "reference_asset_ids": ["a1"],
             "reference_assets": [{"asset_id": "a1", "reference_type": "face",
                                   "is_primary": True, "notes": "", "created_at": "", "updated_at": ""}]}
        r = CharacterRecord.from_dict(d)
        self.assertEqual(len(r.reference_assets), 1)
        self.assertEqual(r.reference_assets[0].reference_type, "face")


class TestCharacterManagerStructuredReferences(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.character_manager import CharacterManager
        self.mgr = CharacterManager()
        self.c = self.mgr.create_character("p1", "Alice")

    def test_add_reference(self):
        r = self.mgr.add_reference(self.c.character_id, "a1", "face", True, "main")
        self.assertEqual(len(r.reference_assets), 1)
        self.assertEqual(r.reference_assets[0].reference_type, "face")
        self.assertTrue(r.reference_assets[0].is_primary)

    def test_add_reference_syncs_ids(self):
        r = self.mgr.add_reference(self.c.character_id, "a1", "face")
        self.assertIn("a1", r.reference_asset_ids)

    def test_remove_reference_by_type(self):
        self.mgr.add_reference(self.c.character_id, "a1", "face")
        self.mgr.add_reference(self.c.character_id, "a1", "costume")
        r = self.mgr.remove_reference(self.c.character_id, "a1", "face")
        types = [ref.reference_type for ref in r.reference_assets]
        self.assertNotIn("face", types)
        self.assertIn("costume", types)

    def test_remove_all_references_for_asset(self):
        self.mgr.add_reference(self.c.character_id, "a1", "face")
        self.mgr.add_reference(self.c.character_id, "a1", "costume")
        r = self.mgr.remove_reference(self.c.character_id, "a1", None)
        asset_ids = [ref.asset_id for ref in r.reference_assets]
        self.assertNotIn("a1", asset_ids)
        self.assertNotIn("a1", r.reference_asset_ids)

    def test_mark_primary(self):
        self.mgr.add_reference(self.c.character_id, "a1", "face", False)
        self.mgr.add_reference(self.c.character_id, "a2", "face", True)
        r = self.mgr.mark_primary_reference(self.c.character_id, "a1", "face")
        face_refs = [ref for ref in r.reference_assets if ref.reference_type == "face"]
        primary = [ref for ref in face_refs if ref.is_primary]
        self.assertEqual(len(primary), 1)
        self.assertEqual(primary[0].asset_id, "a1")

    def test_mark_primary_nonexistent_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.mark_primary_reference(self.c.character_id, "no-asset", "face")

    def test_invalid_reference_type_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.add_reference(self.c.character_id, "a1", "invalid_type")

    def test_list_references(self):
        self.mgr.add_reference(self.c.character_id, "a1", "face")
        self.mgr.add_reference(self.c.character_id, "a2", "costume")
        refs = self.mgr.list_references(self.c.character_id)
        self.assertEqual(len(refs), 2)

    def test_no_file_processing(self):
        # Just verifies no file/image inspection occurs — manager works without any files
        r = self.mgr.add_reference(self.c.character_id, "fake-asset-id", "pose")
        self.assertEqual(r.reference_assets[0].asset_id, "fake-asset-id")


class TestUISessionCharacterReference(unittest.TestCase):
    def setUp(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        svc = ApplicationService()
        self._tmpdir = tempfile.TemporaryDirectory()
        svc.create_project(self._tmpdir.name, "P")
        self.sess = UISession(svc)
        r = self.sess.create_character("Alice", "")
        self.char_id = r.payload["character_id"]


    def tearDown(self):
        if hasattr(self, '_tmpdir'):
            self._tmpdir.cleanup()

    def test_add_reference(self):
        r = self.sess.add_character_reference(self.char_id, "a1", "face", True, "main")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["reference_count"], 1)

    def test_remove_reference(self):
        self.sess.add_character_reference(self.char_id, "a1", "face")
        r = self.sess.remove_character_reference(self.char_id, "a1", "face")
        self.assertTrue(r.ok)

    def test_mark_primary(self):
        self.sess.add_character_reference(self.char_id, "a1", "face")
        r = self.sess.mark_primary_character_reference(self.char_id, "a1", "face")
        self.assertTrue(r.ok)

    def test_empty_asset_id_fails(self):
        r = self.sess.add_character_reference(self.char_id, "", "face")
        self.assertFalse(r.ok)


class TestCharacterReferencePersistence(unittest.TestCase):
    def test_save_load_preserves_references(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            sess = UISession(svc)
            r = sess.create_character("Alice", "")
            cid = r.payload["character_id"]
            sess.add_character_reference(cid, "a1", "face", True, "note")
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            c = svc2.character_manager.get_character(cid)
            self.assertEqual(len(c.reference_assets), 1)
            self.assertEqual(c.reference_assets[0].reference_type, "face")
            self.assertTrue(c.reference_assets[0].is_primary)


class TestDesktopCharacterReferenceMethods(unittest.TestCase):
    def test_methods_exist(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        for name in ("add_character_structured_reference",
                     "remove_character_structured_reference",
                     "mark_primary_character_reference"):
            self.assertTrue(hasattr(DesktopShell, name), f"Missing: {name}")


if __name__ == "__main__":
    unittest.main()
