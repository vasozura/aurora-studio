"""TASK-000060: AFL Expanded Validation Pack tests."""

import json
import tempfile
import unittest


class TestAFLIssueV2Fields(unittest.TestCase):
    def test_defaults(self):
        from aurora_studio.contracts.afl import AFLValidationIssue
        i = AFLValidationIssue(code="X-001", message="test")
        self.assertEqual(i.level, "ERROR")
        self.assertEqual(i.target_type, "")
        self.assertEqual(i.target_id, "")

    def test_from_dict_legacy_severity(self):
        from aurora_studio.contracts.afl import AFLValidationIssue
        d = {"code": "X", "message": "m", "severity": "error", "target_ref": "t"}
        i = AFLValidationIssue.from_dict(d)
        self.assertEqual(i.level, "ERROR")

    def test_from_dict_level_field(self):
        from aurora_studio.contracts.afl import AFLValidationIssue
        d = {"code": "X", "message": "m", "level": "WARN", "target_ref": "t"}
        i = AFLValidationIssue.from_dict(d)
        self.assertEqual(i.level, "WARN")

    def test_to_dict_json_serializable(self):
        from aurora_studio.contracts.afl import AFLValidationIssue
        i = AFLValidationIssue(code="X", message="m", level="ERROR", target_type="scene", target_id="s1")
        json.dumps(i.to_dict())


class TestAFLReportStatusCalculation(unittest.TestCase):
    def test_pass_no_issues(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        eng = AFLEngine()
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="Valid", state="draft",
                        created_at="t", modified_at="t")
        r = eng.validate_scene(s)
        self.assertEqual(r.status, "pass")
        self.assertEqual(r.issue_count, 0)

    def test_fail_on_error(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        eng = AFLEngine()
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="", state="draft",
                        created_at="t", modified_at="t")
        r = eng.validate_scene(s)
        self.assertEqual(r.status, "fail")
        self.assertGreater(r.issue_count, 0)

    def test_report_issue_count_matches(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        eng = AFLEngine()
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="", state="draft",
                        created_at="t", modified_at="t")
        r = eng.validate_scene(s)
        self.assertEqual(r.issue_count, len(r.issues))


class TestValidateScene(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        self.eng = AFLEngine()

    def test_valid_scene_passes(self):
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="Good Scene",
                        state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_scene(s)
        self.assertEqual(r.status, "pass")

    def test_scene_without_title_fails(self):
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="",
                        state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_scene(s)
        self.assertEqual(r.status, "fail")
        codes = [i.code for i in r.issues]
        self.assertIn("S-001", codes)

    def test_scene_as_dict(self):
        r = self.eng.validate_scene({"scene_id": "s1", "title": "Good"})
        self.assertEqual(r.status, "pass")

    def test_scene_dict_no_title_fails(self):
        r = self.eng.validate_scene({"scene_id": "s1", "title": ""})
        self.assertEqual(r.status, "fail")


class TestValidateShot(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        self.eng = AFLEngine()

    def test_valid_shot_passes(self):
        from aurora_studio.contracts.shot import ShotRecord
        s = ShotRecord(shot_id="sh1", scene_id="s1", title="Good",
                       state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_shot(s, known_scene_ids={"s1"})
        self.assertEqual(r.status, "pass")

    def test_shot_without_title_fails(self):
        from aurora_studio.contracts.shot import ShotRecord
        s = ShotRecord(shot_id="sh1", scene_id="s1", title="",
                       state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_shot(s)
        codes = [i.code for i in r.issues]
        self.assertIn("SH-001", codes)

    def test_shot_missing_scene_fails(self):
        from aurora_studio.contracts.shot import ShotRecord
        s = ShotRecord(shot_id="sh1", scene_id="", title="Good",
                       state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_shot(s)
        codes = [i.code for i in r.issues]
        self.assertIn("SH-002", codes)

    def test_shot_referencing_nonexistent_scene_fails(self):
        from aurora_studio.contracts.shot import ShotRecord
        s = ShotRecord(shot_id="sh1", scene_id="no-such-scene", title="Good",
                       state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_shot(s, known_scene_ids={"s1"})
        codes = [i.code for i in r.issues]
        self.assertIn("SH-003", codes)


class TestValidateCharacter(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        self.eng = AFLEngine()

    def test_valid_character_passes(self):
        from aurora_studio.contracts.character import CharacterRecord
        c = CharacterRecord(character_id="c1", project_id="p1", display_name="Alice",
                            state="active", created_at="t", modified_at="t")
        r = self.eng.validate_character(c, known_asset_ids=set())
        self.assertEqual(r.status, "pass")

    def test_character_missing_ref_asset_warns(self):
        from aurora_studio.contracts.character import CharacterRecord
        c = CharacterRecord(character_id="c1", project_id="p1", display_name="Alice",
                            state="active", created_at="t", modified_at="t",
                            reference_asset_ids=("missing-asset",))
        r = self.eng.validate_character(c, known_asset_ids=set())
        levels = [i.level for i in r.issues]
        self.assertIn("WARN", levels)


class TestValidateProjectStructure(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        self.eng = AFLEngine()

    def test_empty_project_passes(self):
        r = self.eng.validate_project_structure({
            "scenes": [], "shots": [], "timelines": [],
            "characters": [], "assets": [], "project_id": "p1"
        })
        self.assertEqual(r.status, "pass")
        self.assertEqual(r.issue_count, 0)

    def test_project_with_good_data_passes(self):
        from aurora_studio.contracts.scene import SceneRecord
        from aurora_studio.contracts.shot import ShotRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="Intro",
                        state="draft", created_at="t", modified_at="t")
        sh = ShotRecord(shot_id="sh1", scene_id="s1", title="Wide",
                        state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_project_structure({
            "scenes": [s], "shots": [sh], "timelines": [],
            "characters": [], "assets": [], "project_id": "p1"
        })
        self.assertEqual(r.status, "pass")

    def test_project_with_bad_scene_fails(self):
        from aurora_studio.contracts.scene import SceneRecord
        s = SceneRecord(scene_id="s1", project_id="p1", title="",
                        state="draft", created_at="t", modified_at="t")
        r = self.eng.validate_project_structure({
            "scenes": [s], "shots": [], "timelines": [],
            "characters": [], "assets": [], "project_id": "p1"
        })
        self.assertEqual(r.status, "fail")

    def test_report_is_json_serializable(self):
        r = self.eng.validate_project_structure({
            "scenes": [], "shots": [], "timelines": [],
            "characters": [], "assets": [], "project_id": "p1"
        })
        json.dumps(r.to_dict())


class TestLegacyAFLValidationStillWorks(unittest.TestCase):
    def test_validate_structure_smoke(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        eng = AFLEngine()
        r = eng.validate_structure("project:p1", {"kind": "smoke"})
        self.assertEqual(r.status, "valid")

    def test_validate_structure_empty_fails(self):
        from aurora_studio.modules.afl_engine import AFLEngine
        eng = AFLEngine()
        r = eng.validate_structure("project:p1", {})
        self.assertEqual(r.status, "invalid")


class TestUISessionValidateProject(unittest.TestCase):
    def test_validate_current_project_structure(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        svc = ApplicationService()
        self._tmpdir = tempfile.TemporaryDirectory()
        svc.create_project(self._tmpdir.name, "P")
        sess = UISession(svc)
        r = sess.validate_current_project_structure()
        self.assertTrue(r.ok)
        self.assertIn("status", r.payload)
        self.assertIn("issue_count", r.payload)


class TestDesktopAFLMethods(unittest.TestCase):
    def test_validate_project_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "validate_current_project_structure"))

    def test_headless_smoke(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        self.assertTrue(headless_smoke().get("ok"))


if __name__ == "__main__":
    unittest.main()
