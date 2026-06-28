"""Tests for TASK-000062: Prompt Export Preview."""

import tempfile
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    svc = ApplicationService()
    return UISession(svc)


def _make_session_with_project(tmp):
    sess = _make_session()
    sess.create_project(tmp, "Preview Project")
    return sess


class TestRenderPromptPreviewFromScene(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session_with_project(self.tmp)
        r = self.sess.create_scene("Opening Scene", "dawn")
        self.scene_id = r.payload["scene_id"]

    def test_render_preview_from_scene(self):
        # Get a default template id for scene
        r = self.sess.list_prompt_templates(target_type="scene")
        self.assertTrue(r.ok)
        templates = r.payload["templates"]
        self.assertTrue(len(templates) > 0)
        tmpl_id = templates[0]["template_id"]

        r2 = self.sess.render_prompt_preview(tmpl_id, "scene", self.scene_id)
        self.assertTrue(r2.ok, r2.message)
        self.assertIn("rendered_text", r2.payload)
        self.assertIsInstance(r2.payload["rendered_text"], str)
        self.assertGreater(len(r2.payload["rendered_text"]), 0)

    def test_render_preview_records_source_info(self):
        r = self.sess.list_prompt_templates(target_type="scene")
        tmpl_id = r.payload["templates"][0]["template_id"]
        r2 = self.sess.render_prompt_preview(tmpl_id, "scene", self.scene_id)
        self.assertTrue(r2.ok)
        self.assertEqual(r2.payload["template_id"], tmpl_id)
        self.assertEqual(r2.payload["source_type"], "scene")
        self.assertEqual(r2.payload["source_id"], self.scene_id)


class TestRenderPromptPreviewFromShot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session_with_project(self.tmp)
        rs = self.sess.create_scene("Shot Scene", "dusk")
        self.scene_id = rs.payload["scene_id"]
        rsh = self.sess.create_shot(self.scene_id, "Close-Up")
        self.shot_id = rsh.payload["shot_id"]

    def test_render_preview_from_shot(self):
        r = self.sess.list_prompt_templates(target_type="shot")
        self.assertTrue(r.ok)
        tmpl_id = r.payload["templates"][0]["template_id"]
        r2 = self.sess.render_prompt_preview(tmpl_id, "shot", self.shot_id)
        self.assertTrue(r2.ok, r2.message)
        self.assertIn("rendered_text", r2.payload)


class TestInvalidTemplateReturnsFailure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session_with_project(self.tmp)
        rs = self.sess.create_scene("S", "x")
        self.scene_id = rs.payload["scene_id"]

    def test_invalid_template_returns_fail(self):
        r = self.sess.render_prompt_preview("tmpl-nonexistent-id", "scene", self.scene_id)
        self.assertFalse(r.ok)

    def test_invalid_source_type_returns_fail(self):
        r2 = self.sess.list_prompt_templates(target_type="scene")
        tmpl_id = r2.payload["templates"][0]["template_id"]
        r = self.sess.render_prompt_preview(tmpl_id, "galaxy", self.scene_id)
        self.assertFalse(r.ok)

    def test_invalid_source_id_returns_fail(self):
        r2 = self.sess.list_prompt_templates(target_type="scene")
        tmpl_id = r2.payload["templates"][0]["template_id"]
        r = self.sess.render_prompt_preview(tmpl_id, "scene", "no-such-scene")
        self.assertFalse(r.ok)


class TestSavePreviewAsExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session_with_project(self.tmp)
        rs = self.sess.create_scene("Export Scene", "noon")
        self.scene_id = rs.payload["scene_id"]
        r_t = self.sess.list_prompt_templates(target_type="scene")
        self.tmpl_id = r_t.payload["templates"][0]["template_id"]

    def test_save_preview_creates_artifact(self):
        r = self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        self.assertTrue(r.ok, r.message)
        artifact = r.payload["artifact"]
        self.assertIn("artifact_id", artifact)
        self.assertIsInstance(artifact["artifact_id"], str)

    def test_artifact_contains_rendered_content(self):
        r = self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        self.assertTrue(r.ok)
        rendered = r.payload["rendered_text"]
        artifact_content = r.payload["artifact"]["content"]
        self.assertEqual(rendered, artifact_content)
        self.assertGreater(len(artifact_content), 0)

    def test_artifact_records_source_type(self):
        r = self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        self.assertTrue(r.ok)
        artifact = r.payload["artifact"]
        self.assertEqual(artifact["source_id"], self.scene_id)
        self.assertEqual(artifact["source_type"], "scene")

    def test_artifact_records_template_id(self):
        r = self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["artifact"]["template_id"], self.tmpl_id)

    def test_artifact_artifact_type_default_is_prompt(self):
        r = self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["artifact"]["artifact_type"], "prompt")

    def test_artifact_appears_in_list(self):
        self.sess.save_prompt_preview_as_export(
            self.tmpl_id, "scene", self.scene_id
        )
        r = self.sess.list_export_artifacts()
        self.assertTrue(r.ok)
        artifacts = r.payload["artifacts"]
        self.assertGreater(len(artifacts), 0)


class TestNoProviderExecution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.sess = _make_session_with_project(self.tmp)
        rs = self.sess.create_scene("NP Scene", "eve")
        self.scene_id = rs.payload["scene_id"]

    def test_no_provider_attribute(self):
        # save_prompt_preview_as_export must not touch any provider-execution method
        r_t = self.sess.list_prompt_templates(target_type="scene")
        tmpl_id = r_t.payload["templates"][0]["template_id"]
        r = self.sess.save_prompt_preview_as_export(tmpl_id, "scene", self.scene_id)
        self.assertTrue(r.ok)
        # Artifact status must be draft (not sent to any provider)
        from aurora_studio.contracts.export import EXPORT_STATUS_DRAFT
        self.assertEqual(r.payload["artifact"]["status"], EXPORT_STATUS_DRAFT)


class TestDesktopMethodsExist(unittest.TestCase):
    def test_render_prompt_preview_method_exists(self):
        from aurora_studio.ui.actions import UISession
        self.assertTrue(hasattr(UISession, "render_prompt_preview"))

    def test_save_prompt_preview_as_export_method_exists(self):
        from aurora_studio.ui.actions import UISession
        self.assertTrue(hasattr(UISession, "save_prompt_preview_as_export"))

    def test_desktop_shell_has_render_method(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "render_prompt_preview"))

    def test_desktop_shell_has_save_method(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "save_prompt_preview_as_export"))

    def test_existing_export_methods_still_present(self):
        from aurora_studio.ui.actions import UISession
        for method in ("create_export_artifact", "mark_export_ready",
                       "mark_export_failed", "list_export_artifacts"):
            self.assertTrue(hasattr(UISession, method), f"Missing: {method}")


if __name__ == "__main__":
    unittest.main()
