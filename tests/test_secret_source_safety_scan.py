"""TASK-000122: Secret / Source Safety Scan tests.

Verifies the safety_scan module, doc, and CLI command.
No network calls. Standard library only.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs" / "v0_4"


class TestSafetyScanModuleImports(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_safety_scan_importable(self):
        import aurora_studio.modules.safety_scan as ss  # noqa: F401
        self.assertTrue(True)

    def test_scan_text_for_secret_fields_exists(self):
        from aurora_studio.modules.safety_scan import scan_text_for_secret_fields
        self.assertTrue(callable(scan_text_for_secret_fields))

    def test_scan_source_for_forbidden_imports_exists(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_imports
        self.assertTrue(callable(scan_source_for_forbidden_imports))

    def test_scan_source_for_forbidden_network_usage_exists(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_network_usage
        self.assertTrue(callable(scan_source_for_forbidden_network_usage))

    def test_scan_source_for_forbidden_media_usage_exists(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_media_usage
        self.assertTrue(callable(scan_source_for_forbidden_media_usage))

    def test_scan_packaging_for_secret_risks_exists(self):
        from aurora_studio.modules.safety_scan import scan_packaging_for_secret_risks
        self.assertTrue(callable(scan_packaging_for_secret_risks))

    def test_run_v0_4_safety_scan_exists(self):
        from aurora_studio.modules.safety_scan import run_v0_4_safety_scan
        self.assertTrue(callable(run_v0_4_safety_scan))


class TestSecretFieldScanner(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.safety_scan import scan_text_for_secret_fields
        self.scan = scan_text_for_secret_fields

    def test_detects_api_key_assignment(self):
        text = 'config["api_key"] = "sk-12345"'
        result = self.scan(text, "test.py")
        self.assertGreater(result["total_findings"], 0)

    def test_detects_token_assignment(self):
        text = "token = user_input_token"
        result = self.scan(text, "test.py")
        self.assertGreater(result["total_findings"], 0)

    def test_detects_password_assignment(self):
        text = "password = get_password()"
        result = self.scan(text, "test.py")
        self.assertGreater(result["total_findings"], 0)

    def test_result_json_serializable(self):
        text = 'data = {"secret": "value"}'
        result = self.scan(text, "test.py")
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertIn("total_findings", parsed)

    def test_skips_comment_lines(self):
        text = "# api_key is not stored here"
        result = self.scan(text, "test.py")
        self.assertEqual(result["total_findings"], 0)

    def test_result_has_required_keys(self):
        result = self.scan("x = 1", "test.py")
        for key in ("path", "total_findings", "errors", "warnings", "findings"):
            self.assertIn(key, result)


class TestForbiddenSDKScannerOnSampleText(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.safety_scan import FORBIDDEN_SDK_COMPILED
        self.patterns = FORBIDDEN_SDK_COMPILED

    def _matches_any(self, line: str) -> bool:
        return any(p.search(line) for p in self.patterns)

    def test_openai_import_detected(self):
        self.assertTrue(self._matches_any("import openai"))

    def test_from_openai_detected(self):
        self.assertTrue(self._matches_any("from openai import ChatCompletion"))

    def test_anthropic_import_detected(self):
        self.assertTrue(self._matches_any("import anthropic"))

    def test_requests_import_detected(self):
        self.assertTrue(self._matches_any("import requests"))

    def test_httpx_import_detected(self):
        self.assertTrue(self._matches_any("import httpx"))

    def test_aiohttp_import_detected(self):
        self.assertTrue(self._matches_any("import aiohttp"))

    def test_pil_import_detected(self):
        self.assertTrue(self._matches_any("import PIL"))

    def test_from_pil_detected(self):
        self.assertTrue(self._matches_any("from PIL import Image"))

    def test_cv2_import_detected(self):
        self.assertTrue(self._matches_any("import cv2"))

    def test_moviepy_import_detected(self):
        self.assertTrue(self._matches_any("import moviepy"))

    def test_urllib_not_detected(self):
        self.assertFalse(self._matches_any("import urllib.request"))

    def test_urllib_error_not_detected(self):
        self.assertFalse(self._matches_any("from urllib.error import URLError"))


class TestRepoSourceScanPasses(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_forbidden_imports_scan_passes(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_imports
        result = scan_source_for_forbidden_imports(str(ROOT))
        self.assertEqual(result["status"], "PASS",
                         f"Forbidden import errors: {result['findings']}")

    def test_forbidden_network_scan_passes(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_network_usage
        result = scan_source_for_forbidden_network_usage(str(ROOT))
        self.assertEqual(result["status"], "PASS",
                         f"Network usage errors: {result['findings']}")

    def test_forbidden_media_scan_passes(self):
        from aurora_studio.modules.safety_scan import scan_source_for_forbidden_media_usage
        result = scan_source_for_forbidden_media_usage(str(ROOT))
        self.assertEqual(result["status"], "PASS",
                         f"Media usage errors: {result['findings']}")

    def test_full_scan_result_json_serializable(self):
        from aurora_studio.modules.safety_scan import run_v0_4_safety_scan
        result = run_v0_4_safety_scan(str(ROOT))
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertIn("overall_status", parsed)

    def test_full_scan_overall_pass(self):
        from aurora_studio.modules.safety_scan import run_v0_4_safety_scan
        result = run_v0_4_safety_scan(str(ROOT))
        self.assertEqual(result["overall_status"], "PASS",
                         f"Safety scan failed: {result}")

    def test_packaging_scan_json_serializable(self):
        from aurora_studio.modules.safety_scan import scan_packaging_for_secret_risks
        result = scan_packaging_for_secret_risks(str(ROOT))
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertIn("status", parsed)

    def test_packaging_scan_passes(self):
        from aurora_studio.modules.safety_scan import scan_packaging_for_secret_risks
        result = scan_packaging_for_secret_risks(str(ROOT))
        self.assertEqual(result["errors"], 0)


class TestSafetyDocExists(unittest.TestCase):

    def test_safety_scan_doc_exists(self):
        self.assertTrue((DOCS / "SECRET_SOURCE_SAFETY_SCAN.md").exists())

    def test_doc_mentions_forbidden_imports(self):
        text = (DOCS / "SECRET_SOURCE_SAFETY_SCAN.md").read_text(encoding="utf-8")
        self.assertIn("import openai", text)
        self.assertIn("import requests", text)

    def test_doc_mentions_secret_fields(self):
        text = (DOCS / "SECRET_SOURCE_SAFETY_SCAN.md").read_text(encoding="utf-8")
        self.assertIn("api_key", text)
        self.assertIn("token", text)


class TestCLISafetyScan(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
            cwd=str(ROOT),
        )

    def test_safety_scan_exits_zero(self):
        r = self._run("safety-scan", "--root", str(ROOT))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_safety_scan_outputs_json(self):
        r = self._run("safety-scan", "--root", str(ROOT))
        parsed = json.loads(r.stdout)
        self.assertIn("overall_status", parsed)

    def test_safety_scan_reports_pass(self):
        r = self._run("safety-scan", "--root", str(ROOT))
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["overall_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
