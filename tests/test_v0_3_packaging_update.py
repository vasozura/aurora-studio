"""Tests for TASK-000097: v0.3 Packaging Update Pack."""

import os
import unittest

PKG_UPDATE = "docs/packaging/V0_3_PACKAGING_UPDATE.md"
FOLDER_LAYOUT = "docs/packaging/V0_3_PORTABLE_FOLDER_LAYOUT.md"


def _content(path):
    with open(path) as f:
        return f.read()


class TestPackagingDocsExist(unittest.TestCase):
    def test_packaging_update_exists(self):
        self.assertTrue(os.path.exists(PKG_UPDATE))

    def test_portable_layout_exists(self):
        self.assertTrue(os.path.exists(FOLDER_LAYOUT))


class TestPackagingUpdateContent(unittest.TestCase):
    def test_mentions_v030(self):
        self.assertIn("v0.3.0", _content(PKG_UPDATE))

    def test_mentions_no_provider_sdks(self):
        c = _content(PKG_UPDATE)
        self.assertIn("No provider SDKs", c)

    def test_mentions_no_api_keys(self):
        c = _content(PKG_UPDATE)
        self.assertIn("No API keys", c)

    def test_mentions_no_secrets(self):
        c = _content(PKG_UPDATE)
        self.assertIn("No bundled secrets", c)

    def test_mentions_no_plugin_execution_runtime(self):
        c = _content(PKG_UPDATE)
        self.assertIn("No plugin execution runtime", c)

    def test_has_included_components_section(self):
        self.assertIn("Included App Components", _content(PKG_UPDATE))

    def test_has_excluded_components_section(self):
        self.assertIn("Explicitly Excluded", _content(PKG_UPDATE))

    def test_has_build_command(self):
        self.assertIn("build_windows_onefolder", _content(PKG_UPDATE))

    def test_has_portable_staging_command(self):
        self.assertIn("stage_windows_portable", _content(PKG_UPDATE))

    def test_has_zip_command(self):
        self.assertIn("create_v0_3_portable_zip_rc", _content(PKG_UPDATE))

    def test_has_smoke_commands(self):
        self.assertIn("smoke_portable_folder", _content(PKG_UPDATE))

    def test_has_safety_confirmation(self):
        self.assertIn("Safety Confirmation", _content(PKG_UPDATE))


class TestPortableLayoutContent(unittest.TestCase):
    def test_layout_mentions_app_dir(self):
        self.assertIn("app/", _content(FOLDER_LAYOUT))

    def test_layout_mentions_data_dir(self):
        self.assertIn("data/", _content(FOLDER_LAYOUT))

    def test_layout_mentions_run_bat(self):
        self.assertIn("run_desktop.bat", _content(FOLDER_LAYOUT))

    def test_layout_mentions_smoke_bat(self):
        self.assertIn("smoke_desktop.bat", _content(FOLDER_LAYOUT))

    def test_layout_mentions_readme(self):
        self.assertIn("README.txt", _content(FOLDER_LAYOUT))

    def test_layout_mentions_notice(self):
        self.assertIn("NOTICE.txt", _content(FOLDER_LAYOUT))

    def test_layout_states_no_secrets(self):
        self.assertIn("No secrets are included", _content(FOLDER_LAYOUT))

    def test_layout_states_no_provider_keys(self):
        self.assertIn("No provider API keys", _content(FOLDER_LAYOUT))

    def test_layout_states_no_plugin_packages(self):
        self.assertIn("No plugin packages", _content(FOLDER_LAYOUT))

    def test_portable_templates_mention_no_bundled_secrets(self):
        c = _content(FOLDER_LAYOUT)
        self.assertIn("No secrets", c)


if __name__ == "__main__":
    unittest.main()
