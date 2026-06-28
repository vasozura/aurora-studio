"""Tests for TASK-000063: Export Profiles."""

import tempfile
import unittest


def _make_session(tmp=None):
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    svc = ApplicationService()
    sess = UISession(svc)
    if tmp is not None:
        sess.create_project(tmp, "Profile Project")
    return sess


class TestDefaultProfilesExist(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        self.mgr = ExportProfileManager()

    def test_six_default_profiles_loaded(self):
        defaults = self.mgr.list_default_profiles()
        self.assertEqual(len(defaults), 6)

    def test_generic_image_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Generic Image Prompt", names)

    def test_cinematic_shot_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Cinematic Shot Prompt", names)

    def test_video_generation_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Video Generation Prompt", names)

    def test_storyboard_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Storyboard Prompt", names)

    def test_character_reference_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Character Reference Prompt", names)

    def test_negative_prompt_exists(self):
        names = {p.name for p in self.mgr.list_default_profiles()}
        self.assertIn("Negative Prompt", names)


class TestProfileCreation(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        self.mgr = ExportProfileManager()

    def test_create_profile(self):
        p = self.mgr.create_profile("My Profile", "shot", template_text="{{shot.title}}")
        self.assertIsNotNone(p.profile_id)
        self.assertEqual(p.name, "My Profile")
        self.assertEqual(p.target_type, "shot")
        self.assertEqual(p.template_text, "{{shot.title}}")

    def test_create_profile_invalid_target_type(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.create_profile("X", "alien_planet")

    def test_create_profile_empty_name_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.create_profile("  ", "shot")

    def test_profile_json_serializable(self):
        import json
        p = self.mgr.create_profile("JSON Profile", "scene", template_text="{{scene.title}}")
        d = p.to_dict()
        json.dumps(d)  # must not raise

    def test_from_dict_roundtrip(self):
        from aurora_studio.contracts.export_profile import ExportProfileRecord
        p = self.mgr.create_profile("RT Profile", "character", template_text="text")
        restored = ExportProfileRecord.from_dict(p.to_dict())
        self.assertEqual(restored.profile_id, p.profile_id)
        self.assertEqual(restored.name, p.name)


class TestProfileListing(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        self.mgr = ExportProfileManager()
        self.mgr.create_profile("Shot Custom", "shot", template_text="{{shot.title}}")
        self.mgr.create_profile("Scene Custom", "scene", template_text="{{scene.title}}")

    def test_list_all_includes_defaults_and_custom(self):
        all_p = self.mgr.list_profiles()
        self.assertGreater(len(all_p), 6)

    def test_filter_by_target_type(self):
        shots = self.mgr.list_profiles(target_type="shot")
        for p in shots:
            self.assertEqual(p.target_type, "shot")

    def test_exclude_defaults(self):
        custom = self.mgr.list_profiles(include_defaults=False)
        for p in custom:
            self.assertFalse(p.profile_id.startswith("default-profile-"))

    def test_list_includes_custom_profiles(self):
        names = {p.name for p in self.mgr.list_profiles(include_defaults=False)}
        self.assertIn("Shot Custom", names)
        self.assertIn("Scene Custom", names)


class TestRenderWithProfile(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.tmp = tmp
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session(self.tmp)
        rs = self.sess.create_scene("Test Scene", "dusk")
        self.scene_id = rs.payload["scene_id"]
        rsh = self.sess.create_shot(self.scene_id, "Wide Shot")
        self.shot_id = rsh.payload["shot_id"]

    def test_render_default_shot_profile(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        defaults = mgr.list_profiles(target_type="shot", include_defaults=True)
        shot_defaults = [p for p in defaults if p.profile_id.startswith("default-profile-")]
        self.assertTrue(len(shot_defaults) > 0)
        pid = shot_defaults[0].profile_id
        r = self.sess.render_export_profile(pid, "shot", self.shot_id)
        self.assertTrue(r.ok, r.message)
        self.assertIn("rendered_text", r.payload)
        self.assertIsInstance(r.payload["rendered_text"], str)

    def test_render_with_invalid_profile(self):
        r = self.sess.render_export_profile("nonexistent-profile", "scene", self.scene_id)
        self.assertFalse(r.ok)

    def test_render_with_invalid_source(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        scene_profiles = [p for p in mgr.list_default_profiles() if p.target_type == "scene"]
        pid = scene_profiles[0].profile_id
        r = self.sess.render_export_profile(pid, "scene", "no-such-scene")
        self.assertFalse(r.ok)

    def test_render_returns_source_info(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        scene_profiles = [p for p in mgr.list_default_profiles() if p.target_type == "scene"]
        pid = scene_profiles[0].profile_id
        r = self.sess.render_export_profile(pid, "scene", self.scene_id)
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["profile_id"], pid)
        self.assertEqual(r.payload["source_type"], "scene")
        self.assertEqual(r.payload["source_id"], self.scene_id)


class TestSaveArtifactRecordsProfileId(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session(self.tmp)
        rs = self.sess.create_scene("Artifact Scene", "noon")
        self.scene_id = rs.payload["scene_id"]

    def test_save_artifact_records_profile_id(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        scene_profiles = [p for p in mgr.list_default_profiles() if p.target_type == "scene"]
        pid = scene_profiles[0].profile_id
        r = self.sess.save_profile_render_as_export(pid, "scene", self.scene_id)
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["artifact"]["profile_id"], pid)

    def test_artifact_content_matches_rendered(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        scene_profiles = [p for p in mgr.list_default_profiles() if p.target_type == "scene"]
        pid = scene_profiles[0].profile_id
        r = self.sess.save_profile_render_as_export(pid, "scene", self.scene_id)
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["rendered_text"], r.payload["artifact"]["content"])

    def test_artifact_appears_in_export_list(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        scene_profiles = [p for p in mgr.list_default_profiles() if p.target_type == "scene"]
        pid = scene_profiles[0].profile_id
        self.sess.save_profile_render_as_export(pid, "scene", self.scene_id)
        r = self.sess.list_export_artifacts()
        self.assertTrue(r.ok)
        self.assertGreater(len(r.payload["artifacts"]), 0)


class TestCustomProfileSurvivesSaveLoad(unittest.TestCase):
    def test_custom_profile_survives_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            from aurora_studio.services.application_service import ApplicationService
            from aurora_studio.ui.actions import UISession
            svc = ApplicationService()
            sess = UISession(svc)
            sess.create_project(tmp, "P")
            p = svc.export_profile_manager.create_profile(
                "Persist Profile", "shot", template_text="{{shot.title}} persist"
            )
            pid = p.profile_id
            sess.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            restored = svc2.export_profile_manager.get_profile(pid)
            self.assertEqual(restored.name, "Persist Profile")
            self.assertEqual(restored.template_text, "{{shot.title}} persist")


class TestNoProviderExecution(unittest.TestCase):
    def test_render_no_provider_call(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        rendered = mgr.render_profile_text("Hello {{name}}", {"name": "World"})
        self.assertEqual(rendered, "Hello World")

    def test_unresolved_placeholder_left_intact(self):
        from aurora_studio.modules.export_profile_manager import ExportProfileManager
        mgr = ExportProfileManager()
        rendered = mgr.render_profile_text("{{shot.title}} is {{shot.missing}}", {"shot.title": "CU"})
        self.assertIn("{{shot.missing}}", rendered)


class TestUISessionProfileMethods(unittest.TestCase):
    def test_list_export_profiles_method_exists(self):
        from aurora_studio.ui.actions import UISession
        self.assertTrue(hasattr(UISession, "list_export_profiles"))

    def test_render_export_profile_method_exists(self):
        from aurora_studio.ui.actions import UISession
        self.assertTrue(hasattr(UISession, "render_export_profile"))

    def test_save_profile_render_as_export_method_exists(self):
        from aurora_studio.ui.actions import UISession
        self.assertTrue(hasattr(UISession, "save_profile_render_as_export"))

    def test_list_returns_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = _make_session(tmp)
            r = sess.list_export_profiles()
            self.assertTrue(r.ok)
            self.assertIn("profiles", r.payload)
            self.assertGreater(len(r.payload["profiles"]), 0)

    def test_list_filter_by_target_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = _make_session(tmp)
            r = sess.list_export_profiles(target_type="shot")
            self.assertTrue(r.ok)
            for p in r.payload["profiles"]:
                self.assertEqual(p["target_type"], "shot")


if __name__ == "__main__":
    unittest.main()
