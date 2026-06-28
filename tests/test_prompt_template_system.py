"""TASK-000061: Prompt Template System tests."""

import json
import tempfile
import unittest


class TestPromptTemplateRecord(unittest.TestCase):
    def _make(self, **kw):
        from aurora_studio.contracts.prompt_template import PromptTemplateRecord
        return PromptTemplateRecord(
            template_id="t1", project_id="p1", name="test",
            target_type="scene", template_text="Hello {{scene.title}}",
            **kw
        )

    def test_defaults(self):
        r = self._make()
        self.assertEqual(r.description, "")
        self.assertEqual(r.state, "active")

    def test_to_dict_json_serializable(self):
        r = self._make()
        json.dumps(r.to_dict())

    def test_from_dict_roundtrip(self):
        from aurora_studio.contracts.prompt_template import PromptTemplateRecord
        r = self._make(description="desc")
        r2 = PromptTemplateRecord.from_dict(r.to_dict())
        self.assertEqual(r2.template_id, "t1")
        self.assertEqual(r2.description, "desc")

    def test_from_dict_missing_fields_use_defaults(self):
        from aurora_studio.contracts.prompt_template import PromptTemplateRecord
        r = PromptTemplateRecord.from_dict({"template_id": "x", "project_id": "p",
                                            "name": "n", "target_type": "scene",
                                            "template_text": "T"})
        self.assertEqual(r.state, "active")
        self.assertEqual(r.description, "")


class TestPromptTemplateManagerDefaults(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.prompt_template_manager import PromptTemplateManager
        self.mgr = PromptTemplateManager()

    def test_default_templates_available(self):
        templates = self.mgr.list_templates()
        names = [t.name for t in templates]
        for expected in ("scene_basic", "shot_cinematic", "character_reference",
                         "timeline_summary", "asset_reference"):
            self.assertIn(expected, names, f"Missing default: {expected}")

    def test_default_templates_are_five(self):
        defaults = self.mgr.list_default_templates()
        self.assertGreaterEqual(len(defaults), 5)

    def test_filter_by_target_type(self):
        scene_tmpls = self.mgr.list_templates(target_type="scene")
        self.assertTrue(all(t.target_type == "scene" for t in scene_tmpls))

    def test_no_provider_call_attributes(self):
        # Ensure manager has no provider/AI attributes
        self.assertFalse(hasattr(self.mgr, "call_provider"))
        self.assertFalse(hasattr(self.mgr, "generate_ai"))


class TestPromptTemplateManagerCRUD(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.prompt_template_manager import PromptTemplateManager
        self.mgr = PromptTemplateManager()

    def test_create_template(self):
        r = self.mgr.create_template("my tmpl", "shot", "Shot: {{shot.title}}")
        self.assertEqual(r.name, "my tmpl")
        self.assertEqual(r.target_type, "shot")
        self.assertTrue(r.template_id.startswith("tmpl-"))

    def test_get_template(self):
        r = self.mgr.create_template("t", "scene", "text")
        r2 = self.mgr.get_template(r.template_id)
        self.assertEqual(r.template_id, r2.template_id)

    def test_get_nonexistent_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.get_template("no-such")

    def test_update_template(self):
        r = self.mgr.create_template("t", "scene", "old text")
        r2 = self.mgr.update_template(r.template_id, template_text="new text")
        self.assertEqual(r2.template_text, "new text")

    def test_archive_template(self):
        r = self.mgr.create_template("t", "scene", "text")
        r2 = self.mgr.archive_template(r.template_id)
        self.assertEqual(r2.state, "archived")
        # Should not appear in list
        active = [t for t in self.mgr.list_templates() if t.template_id == r.template_id]
        self.assertEqual(len(active), 0)

    def test_invalid_target_type_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.create_template("t", "invalid_type", "text")

    def test_empty_name_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.create_template("", "scene", "text")

    def test_empty_template_text_raises(self):
        from aurora_studio.core.errors import ValidationError
        with self.assertRaises(ValidationError):
            self.mgr.create_template("t", "scene", "")

    def test_unknown_update_field_raises(self):
        from aurora_studio.core.errors import ValidationError
        r = self.mgr.create_template("t", "scene", "text")
        with self.assertRaises(ValidationError):
            self.mgr.update_template(r.template_id, bad_field="x")


class TestTemplateRendering(unittest.TestCase):
    def setUp(self):
        from aurora_studio.modules.prompt_template_manager import PromptTemplateManager
        self.mgr = PromptTemplateManager()

    def test_render_simple(self):
        text = self.mgr.render_template_text("Hello {{scene.title}}", {"scene.title": "Forest"})
        self.assertEqual(text, "Hello Forest")

    def test_render_multiple_placeholders(self):
        text = self.mgr.render_template_text(
            "{{scene.title}} - {{scene.mood}}",
            {"scene.title": "Forest", "scene.mood": "dark"}
        )
        self.assertEqual(text, "Forest - dark")

    def test_missing_placeholder_renders_empty(self):
        text = self.mgr.render_template_text("{{scene.missing}}", {"scene.title": "X"})
        self.assertEqual(text, "{{scene.missing}}")  # unresolved placeholders left as-is

    def test_render_none_value(self):
        text = self.mgr.render_template_text("{{scene.title}}", {"scene.title": None})
        self.assertEqual(text, "")

    def test_render_template_by_id(self):
        r = self.mgr.create_template("t", "scene", "Scene: {{scene.title}}")
        text = self.mgr.render_template(r.template_id, {"scene.title": "Forest"})
        self.assertEqual(text, "Scene: Forest")

    def test_render_default_scene_template(self):
        tmpl = next(t for t in self.mgr.list_templates() if t.name == "scene_basic")
        text = self.mgr.render_template(tmpl.template_id, {
            "scene.title": "Beach", "scene.location": "Malibu",
            "scene.mood": "serene", "scene.description": "Waves.",
            "scene.time_of_day": "dawn", "scene.conflict": ""
        })
        self.assertIn("Beach", text)
        self.assertIn("Malibu", text)

    def test_render_is_deterministic(self):
        ctx = {"scene.title": "A", "scene.mood": "B"}
        t1 = self.mgr.render_template_text("{{scene.title}}{{scene.mood}}", ctx)
        t2 = self.mgr.render_template_text("{{scene.title}}{{scene.mood}}", ctx)
        self.assertEqual(t1, t2)


class TestUISessionPromptTemplate(unittest.TestCase):
    def setUp(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        self.svc = ApplicationService()
        self._tmp = tempfile.TemporaryDirectory()
        self.svc.create_project(self._tmp.name, "P")
        # Create scene/shot/character/asset for render tests
        self.scene = self.svc.scene_manager.create_scene("p1", "Forest", "")
        self.shot = self.svc.shot_manager.create_shot(self.scene.scene_id, "Wide")
        self.char = self.svc.character_manager.create_character("p1", "Alice")
        self.asset = self.svc.asset_manager.import_asset("p1", "image", "Sword")
        self.sess = UISession(self.svc)

    def tearDown(self):
        self._tmp.cleanup()

    def test_list_prompt_templates(self):
        r = self.sess.list_prompt_templates()
        self.assertTrue(r.ok)
        self.assertGreaterEqual(r.payload["count"], 5)

    def test_list_by_target_type(self):
        r = self.sess.list_prompt_templates(target_type="shot")
        self.assertTrue(r.ok)
        for t in r.payload["templates"]:
            self.assertEqual(t["target_type"], "shot")

    def test_create_prompt_template(self):
        r = self.sess.create_prompt_template("My Tmpl", "scene", "{{scene.title}}")
        self.assertTrue(r.ok)
        self.assertIn("template_id", r.payload)

    def test_render_prompt_template_scene(self):
        tmpl = next(
            t for t in self.svc.prompt_template_manager.list_templates()
            if t.name == "scene_basic"
        )
        r = self.sess.render_prompt_template(tmpl.template_id, "scene", self.scene.scene_id)
        self.assertTrue(r.ok)
        self.assertIn("rendered_text", r.payload)

    def test_render_prompt_template_shot(self):
        tmpl = next(
            t for t in self.svc.prompt_template_manager.list_templates()
            if t.name == "shot_cinematic"
        )
        r = self.sess.render_prompt_template(tmpl.template_id, "shot", self.shot.shot_id)
        self.assertTrue(r.ok)

    def test_render_prompt_template_character(self):
        tmpl = next(
            t for t in self.svc.prompt_template_manager.list_templates()
            if t.name == "character_reference"
        )
        r = self.sess.render_prompt_template(tmpl.template_id, "character", self.char.character_id)
        self.assertTrue(r.ok)
        self.assertIn("Alice", r.payload["rendered_text"])

    def test_render_missing_source_fails(self):
        r = self.sess.render_prompt_template("default-scene_basic", "scene", "no-such-id")
        self.assertFalse(r.ok)

    def test_render_unknown_source_type_fails(self):
        r = self.sess.render_prompt_template("default-scene_basic", "invalid_type", "x")
        self.assertFalse(r.ok)

    def test_render_template_text_direct(self):
        r = self.sess.render_prompt_template_text(
            "Scene: {{scene.title}}", "scene", self.scene.scene_id
        )
        self.assertTrue(r.ok)
        self.assertIn("Forest", r.payload["rendered_text"])

    def test_missing_template_id_fails(self):
        r = self.sess.render_prompt_template("no-such-template", "scene", self.scene.scene_id)
        self.assertFalse(r.ok)


class TestPromptTemplatePersistence(unittest.TestCase):
    def test_custom_template_survives_save_load(self):
        from aurora_studio.services.application_service import ApplicationService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            r = svc.prompt_template_manager.create_template(
                "custom", "shot", "{{shot.title}} custom"
            )
            tid = r.template_id
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            t2 = svc2.prompt_template_manager.get_template(tid)
            self.assertEqual(t2.name, "custom")
            self.assertEqual(t2.template_text, "{{shot.title}} custom")

    def test_defaults_still_available_after_rehydration(self):
        from aurora_studio.services.application_service import ApplicationService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ApplicationService()
            svc.create_project(tmp, "P")
            svc.save_bundle(tmp)

            svc2 = ApplicationService()
            svc2.load_and_rehydrate_bundle(tmp)
            names = [t.name for t in svc2.prompt_template_manager.list_templates()]
            self.assertIn("scene_basic", names)


if __name__ == "__main__":
    unittest.main()
