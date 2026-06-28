"""TASK-000124: v0.4 Packaging / Portable Secret Safety tests.

Verifies packaging safety docs and scripts exist with required content.
No network calls. Standard library only.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_PKG = ROOT / "docs" / "packaging"
SCRIPTS = ROOT / "scripts"


class TestPackagingSafetyDocExists(unittest.TestCase):

    def _doc(self):
        p = DOCS_PKG / "V0_4_PACKAGING_SECRET_SAFETY.md"
        self.assertTrue(p.exists(), "Packaging secret safety doc missing")
        return p.read_text(encoding="utf-8")

    def test_doc_exists(self):
        self.assertTrue((DOCS_PKG / "V0_4_PACKAGING_SECRET_SAFETY.md").exists())

    def test_doc_has_purpose(self):
        self.assertIn("Purpose", self._doc())

    def test_doc_has_scope(self):
        self.assertIn("## Scope", self._doc())

    def test_doc_has_portable_artifact_boundary(self):
        self.assertIn("Portable Artifact Boundary", self._doc())

    def test_doc_has_excluded_files(self):
        self.assertIn("Excluded Files", self._doc())

    def test_doc_has_excluded_secret_patterns(self):
        self.assertIn("Excluded Secret Patterns", self._doc())

    def test_doc_has_provider_key_policy(self):
        self.assertIn("Provider Key Policy", self._doc())

    def test_doc_states_no_api_keys_bundled(self):
        self.assertIn("No API keys are bundled.", self._doc())

    def test_doc_states_no_env_files_bundled(self):
        self.assertIn("No .env files are bundled.", self._doc())

    def test_doc_states_no_provider_secrets(self):
        self.assertIn("No provider secrets are bundled.", self._doc())

    def test_doc_states_no_user_secrets(self):
        self.assertIn("No user secrets are bundled.", self._doc())

    def test_doc_states_no_plugin_packages(self):
        self.assertIn("No plugin packages are bundled for execution.", self._doc())

    def test_doc_states_real_execution_opt_in(self):
        self.assertIn("Provider real execution remains opt-in and secret-safe.", self._doc())

    def test_doc_has_environment_file_policy(self):
        self.assertIn("Environment File Policy", self._doc())

    def test_doc_has_cache_policy(self):
        self.assertIn("Cache Policy", self._doc())

    def test_doc_has_logs_policy(self):
        self.assertIn("Logs Policy", self._doc())

    def test_doc_has_user_project_data_policy(self):
        self.assertIn("User Project Data Policy", self._doc())

    def test_doc_has_smoke_validation(self):
        self.assertIn("Smoke Validation", self._doc())

    def test_doc_has_known_limitations(self):
        self.assertIn("Known Limitations", self._doc())


class TestPortableProviderBoundaryDocExists(unittest.TestCase):

    def _doc(self):
        p = DOCS_PKG / "V0_4_PORTABLE_PROVIDER_BOUNDARY.md"
        self.assertTrue(p.exists(), "Portable provider boundary doc missing")
        return p.read_text(encoding="utf-8")

    def test_doc_exists(self):
        self.assertTrue((DOCS_PKG / "V0_4_PORTABLE_PROVIDER_BOUNDARY.md").exists())

    def test_doc_has_purpose(self):
        self.assertIn("Purpose", self._doc())

    def test_doc_has_provider_workflows_included(self):
        self.assertIn("Provider Workflows Included", self._doc())

    def test_doc_has_provider_workflows_excluded(self):
        self.assertIn("Provider Workflows Excluded", self._doc())

    def test_doc_has_text_provider_boundary(self):
        self.assertIn("Text Provider Boundary", self._doc())

    def test_doc_has_image_provider_boundary(self):
        self.assertIn("Image Provider Boundary", self._doc())

    def test_doc_has_video_provider_boundary(self):
        self.assertIn("Video Provider Boundary", self._doc())

    def test_doc_has_secret_handling(self):
        self.assertIn("Secret Handling", self._doc())

    def test_doc_has_logs_history(self):
        self.assertIn("Logs/History", self._doc())

    def test_doc_has_offline_behavior(self):
        self.assertIn("Offline Behavior", self._doc())

    def test_doc_has_known_limitations(self):
        self.assertIn("Known Limitations", self._doc())

    def test_doc_includes_mock_workflows(self):
        text = self._doc()
        self.assertIn("mock", text.lower())
        self.assertIn("mock_image", text)
        self.assertIn("mock_video", text)

    def test_doc_excludes_sdks(self):
        self.assertIn("Provider SDKs", self._doc())

    def test_doc_excludes_bundled_api_keys(self):
        self.assertIn("Bundled API keys", self._doc())

    def test_doc_excludes_real_image_execution(self):
        self.assertIn("Real image provider execution", self._doc())

    def test_doc_excludes_real_video_execution(self):
        self.assertIn("Real video provider execution", self._doc())

    def test_doc_excludes_plugin_execution(self):
        self.assertIn("Plugin execution", self._doc())


class TestSmokeScriptsExist(unittest.TestCase):

    def test_ps1_script_exists(self):
        self.assertTrue((SCRIPTS / "smoke_v0_4_portable_secret_safety.ps1").exists())

    def test_bat_script_exists(self):
        self.assertTrue((SCRIPTS / "smoke_v0_4_portable_secret_safety.bat").exists())

    def _ps1(self):
        return (SCRIPTS / "smoke_v0_4_portable_secret_safety.ps1").read_text(encoding="utf-8")

    def _bat(self):
        return (SCRIPTS / "smoke_v0_4_portable_secret_safety.bat").read_text(encoding="utf-8")

    def test_ps1_checks_env_files(self):
        self.assertIn(".env", self._ps1())

    def test_ps1_checks_pycache(self):
        self.assertIn("__pycache__", self._ps1())

    def test_ps1_checks_pytest_cache(self):
        self.assertIn(".pytest_cache", self._ps1())

    def test_ps1_checks_sdk_folders(self):
        self.assertIn("openai", self._ps1())

    def test_ps1_checks_readme(self):
        ps1 = self._ps1()
        self.assertIn("README", ps1)

    def test_ps1_fails_on_error(self):
        self.assertIn("exit 1", self._ps1())

    def test_ps1_has_no_network_calls(self):
        ps1 = self._ps1()
        self.assertNotIn("Invoke-WebRequest", ps1)
        self.assertNotIn("curl", ps1.lower().replace("# curl", ""))

    def test_bat_checks_env_files(self):
        self.assertIn(".env", self._bat())

    def test_bat_checks_pycache(self):
        self.assertIn("__pycache__", self._bat())

    def test_bat_checks_pytest_cache(self):
        self.assertIn(".pytest_cache", self._bat())

    def test_bat_checks_sdk_folders(self):
        self.assertIn("openai", self._bat())

    def test_bat_has_no_network_calls(self):
        bat = self._bat()
        self.assertNotIn("curl", bat.lower())
        self.assertNotIn("wget", bat.lower())


class TestSmokeScriptRunsOnCurrentDir(unittest.TestCase):
    """Verify smoke script logic on the current repo (Linux simulation via Python)."""

    def setUp(self):
        # Python-based check equivalent to what ps1/bat does
        self.root = ROOT

    def test_no_env_files_in_src(self):
        src = self.root / "src"
        env_files = list(src.rglob(".env")) + [
            f for f in src.rglob("*") if f.suffix == ".env"
        ]
        self.assertEqual(len(env_files), 0, f"Found .env files: {env_files}")

    def test_no_sdk_folders_in_src(self):
        src = self.root / "src"
        forbidden_dirs = {"openai", "anthropic", "requests", "httpx", "aiohttp"}
        found = [d for d in src.iterdir() if d.is_dir() and d.name in forbidden_dirs]
        self.assertEqual(len(found), 0, f"SDK dirs found: {found}")

    def test_no_api_key_files_in_scripts(self):
        if not SCRIPTS.exists():
            return
        for f in SCRIPTS.iterdir():
            if f.is_file() and f.suffix in (".ps1", ".bat", ".sh"):
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Scripts may mention api_key as pattern to EXCLUDE — that's fine
                # They must not hard-code a real value
                self.assertNotIn("sk-", content, f"Possible secret in {f}")


if __name__ == "__main__":
    unittest.main()
