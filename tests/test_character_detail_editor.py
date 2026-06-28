"""TASK-000058: Character Detail Editor Pack tests."""

import json
import tempfile
import unittest


class TestCharacterRecordV2Fields(unittest.TestCase):
    def _make(self, **kw):
        from aurora_studio.contracts.character import CharacterRecord
        return CharacterRecord(
            character_id="c1", project_id="p1", display_name="Alice",
            state="active", created_at="t", modified_at="t", **kw
        )

    def test_detail_defaults(self):
        r = self._make()
        self.assertEqual(r.role, "")
        self.assertEqual(r.visual_description, "")
        self.assertEqual(r.personality, "")
        self.assertEqual(r.motivation, "")
        self.assertEqual(r.conflict, "")
        self.assertEqual(r.arc_notes, "")
        self.assertEqual(r.notes, "")

    def test_with_detail_fields(self):
        r = self._make(role="Hero", personality="Bold", motivation="Save world")
        self.assertEqual(r.role, "Hero")
        self.assertEqual(r.personality, "Bold")
        self.assertEqual(r.motivation, "Save world")

    def test_to_dict_json_serializable(self):
        r = self._make(role="Hero")
        json.dumps(r.to_dict())

    def test_from_dict_backward_compat(self):
        from aurora_studio.contracts.character import CharacterRecord
        d = {"character_id": "c1", "project_id": "p1", "display_name": "Alice",
             "state": "active", "created_at": "t", "modified_at": "t"}
        r = CharacterRecord.from_dict(d)
        self.assertEqual(r.role, "")
        self.assertEqual(r.notes, "")

    def test_from_dict_with_detail_fields(self):
        from aurora_studio.contracts.character import CharacterRecord
        d = {"character_id": "c1", "project_id": "p1", "display_name": "Alice",
             "state": "active", "created_at": "t", "modified_at": "t",
             "role": "Villain", "personality": "Cunning", "arc_notes": "arc"}
        r = CharacterRecord.from_dict(d)
        self.assertEqual(r.role, "Villain")
        self.assertEqual(r.personality, "Cunning")
        self.assertEqual(r.arc_notes, "arc")


class TestCharacterManagerUpdateDetails(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.character_manager import CharacterManager
        self.mgr = CharacterManager()
        self.c = self.mgr.create_character("p1", "Alice")

    def test_update_role(self):
        r = self.mgr.update_character_details(self.c.character_id, role="Hero")
        self.assertEqual(r.role, "Hero")

    def test_update_personality(self):
        r = self.mgr.update_character_details(self.c.character_id, personality="Bold")
        self.assertEqual(r.personality, "Bold")

    def test_update_multiple_fields(self):
        r = self.mgr.update_character_details(
            self.c.character_id, motivation="Save world", conflict="Inner doubt")
        self.assertEqual(r.motivation, "Save world")
        self.assertEqual(r.conflict, "Inner doubt")

    def test_empty_display_name_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_character_details(self.c.character_id, display_name="")

    def test_unknown_field_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.update_character_details(self.c.character_id, bad_field="x")

    def test_archive_still_works(self):
        r = self.mgr.archive_character(self.c.character_id)
        self.assertEqual(r.state, "archived")

    def test_reference_asset_still_works(self):
        r = self.mgr.add_reference_asset(self.c.character_id, "a1")
        self.assertIn("a1", r.reference_asset_ids)


class TestCharacterDetailViewModel(unittest.TestCase):
    def test_from_record(self):
        from aurora_studio.modules.character_manager import CharacterManager
        from aurora_studio.ui.view_models import CharacterDetailViewModel
        mgr = CharacterManager()
        c = mgr.create_character("p1", "Alice", "A hero")
        c2 = mgr.update_character_details(c.character_id, role="Protagonist", arc_notes="rises")
        vm = CharacterDetailViewModel.from_record(c2)
        self.assertEqual(vm.role, "Protagonist")
        self.assertEqual(vm.arc_notes, "rises")
        self.assertEqual(vm.status, "active")
        self.assertEqual(vm.updated_at, c2.modified_at)

    def test_to_dict_json_serializable(self):
        from aurora_studio.modules.character_manager import CharacterManager
        from aurora_studio.ui.view_models import CharacterDetailViewModel
        mgr = CharacterManager()
        c = mgr.create_character("p1", "Alice")
        vm = CharacterDetailViewModel.from_record(c)
        json.dumps(vm.to_dict())


class TestUISessionCharacterDetail(unittest.TestCase):
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

    def test_get_character_detail(self):
        r = self.sess.get_character_detail(self.char_id)
        self.assertTrue(r.ok)
        self.assertIn("character_id", r.payload)

    def test_update_character_detail(self):
        r = self.sess.update_character_detail(self.char_id, {"role": "Hero", "personality": "Bold"})
        self.assertTrue(r.ok)

    def test_empty_display_name_fails(self):
        r = self.sess.update_character_detail(self.char_id, {"display_name": ""})
        self.assertFalse(r.ok)

    def test_unknown_character_fails(self):
        r = self.sess.get_character_detail("no-such")
        self.assertFalse(r.ok)


class TestCharacterDetailPersistence(unittest.TestCase):
    def test_save_load_preserves_details(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            sess = UISession(svc)
            r = sess.create_character("Alice", "")
            cid = r.payload["character_id"]
            sess.update_character_detail(cid, {"role": "Villain", "motivation": "Power"})
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            c = svc2.character_manager.get_character(cid)
            self.assertEqual(c.role, "Villain")
            self.assertEqual(c.motivation, "Power")


class TestDesktopCharacterMethods(unittest.TestCase):
    def test_methods_exist(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        for name in ("load_selected_character_detail", "apply_character_detail_changes"):
            self.assertTrue(hasattr(DesktopShell, name), f"Missing: {name}")

    def test_headless_smoke(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        self.assertTrue(headless_smoke().get("ok"))


if __name__ == "__main__":
    unittest.main()
