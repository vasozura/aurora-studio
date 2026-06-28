"""Tests for TASK-000091: Asset Preview Planning Pack."""

import os
import unittest

PLAN_PATH = "docs/planning/ASSET_PREVIEW_PLAN.md"
BOUNDARY_PATH = "docs/v0_3/ASSET_PREVIEW_SECURITY_BOUNDARY.md"


class TestAssetPreviewPlanExists(unittest.TestCase):
    def test_plan_exists(self):
        self.assertTrue(os.path.exists(PLAN_PATH))

    def test_boundary_exists(self):
        self.assertTrue(os.path.exists(BOUNDARY_PATH))


class TestAssetPreviewPlanContent(unittest.TestCase):
    def _content(self):
        with open(PLAN_PATH) as f:
            return f.read()

    def test_plan_states_no_preview_implemented(self):
        c = self._content()
        self.assertIn("planning-only", c.lower())

    def test_plan_states_no_media_decoding(self):
        c = self._content()
        self.assertIn("no image/video/audio decoding", c.lower())

    def test_plan_states_no_file_opened(self):
        c = self._content()
        self.assertIn("no media file is opened", c.lower())

    def test_plan_has_non_goals_section(self):
        c = self._content()
        self.assertIn("Non-Goals", c)

    def test_plan_has_future_preview_types(self):
        c = self._content()
        self.assertIn("Future Preview Types", c)

    def test_plan_has_security_boundary_reference(self):
        c = self._content()
        self.assertIn("security boundary", c.lower())

    def test_plan_states_no_plugin_provider_execution(self):
        c = self._content()
        self.assertIn("no plugin/provider execution is involved", c.lower())

    def test_plan_has_acceptance_criteria(self):
        c = self._content()
        self.assertIn("Acceptance Criteria", c)


class TestAssetPreviewBoundaryContent(unittest.TestCase):
    def _content(self):
        with open(BOUNDARY_PATH) as f:
            return f.read()

    def test_boundary_states_no_file_content_inspection(self):
        c = self._content()
        self.assertIn("no file content inspection", c.lower())

    def test_boundary_states_no_external_preview_tools(self):
        c = self._content()
        self.assertIn("no external preview tools", c.lower())

    def test_boundary_states_no_plugin_preview_execution(self):
        c = self._content()
        self.assertIn("no plugin preview execution", c.lower())

    def test_boundary_states_no_network_fetching(self):
        c = self._content()
        self.assertIn("no network fetching", c.lower())

    def test_boundary_states_no_thumbnail_generation(self):
        c = self._content()
        self.assertIn("no thumbnail generation", c.lower())

    def test_boundary_states_no_media_decoding(self):
        c = self._content()
        self.assertIn("no media decoding", c.lower())

    def test_boundary_has_future_safe_rules(self):
        c = self._content()
        self.assertIn("Future Safe Preview Rules", c)


class TestNoPreviewImplementedInCode(unittest.TestCase):
    """Verify no preview/decoding code was added to production modules."""

    def test_no_thumbnail_module_created(self):
        self.assertFalse(os.path.exists("src/aurora_studio/modules/thumbnail_generator.py"))

    def test_no_media_decoder_module_created(self):
        self.assertFalse(os.path.exists("src/aurora_studio/modules/media_decoder.py"))

    def test_asset_manager_does_not_open_files(self):
        import aurora_studio.modules.asset_manager as am
        src = open(am.__file__).read()
        # Must not call open() on asset location or PIL/Pillow
        self.assertNotIn("PIL.Image", src)
        self.assertNotIn("from PIL", src)


if __name__ == "__main__":
    unittest.main()
