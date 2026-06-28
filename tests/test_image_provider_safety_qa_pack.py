"""TASK-000115: Image Provider Safety QA Pack.

Source-level and behavioral safety checks for the v0.4 image provider stack.
No network calls. No image files. Standard library only.
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
AURORA_SRC = SRC / "aurora_studio"


class TestImageProviderNoForbiddenImportsInSource(unittest.TestCase):
    """Scan src/aurora_studio/**/*.py for forbidden imports."""

    FORBIDDEN_IMPORTS = {"PIL", "cv2", "moviepy", "requests", "httpx", "aiohttp"}

    def _get_source_files(self):
        return list(AURORA_SRC.rglob("*.py"))

    def test_no_pil_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import PIL", src, f"PIL import found in {f}")
            self.assertNotIn("from PIL", src, f"PIL import found in {f}")

    def test_no_cv2_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import cv2", src, f"cv2 import found in {f}")

    def test_no_moviepy_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import moviepy", src, f"moviepy import found in {f}")
            self.assertNotIn("from moviepy", src, f"moviepy import found in {f}")

    def test_no_requests_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import requests", src, f"requests import found in {f}")

    def test_no_httpx_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import httpx", src, f"httpx import found in {f}")

    def test_no_aiohttp_import(self):
        for f in self._get_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import aiohttp", src, f"aiohttp import found in {f}")

    def test_no_image_provider_sdk_imported_at_runtime(self):
        sys.path.insert(0, str(SRC))
        import aurora_studio.modules.mock_image_provider_adapter as m  # noqa: F401
        top_level = {mod.split(".")[0] for mod in sys.modules}
        for forbidden in {"PIL", "cv2", "moviepy", "requests", "httpx", "aiohttp", "openai", "anthropic"}:
            self.assertNotIn(forbidden, top_level,
                             f"Forbidden module '{forbidden}' found in sys.modules")


class TestImageExecutionGateSafety(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import ImageProviderExecutionGate
        self.gate = ImageProviderExecutionGate()

    def test_real_image_never_allowed(self):
        decision = self.gate.evaluate_real_image("any-provider")
        self.assertFalse(decision.allowed)

    def test_real_image_blocked_reason(self):
        decision = self.gate.evaluate_real_image("any-provider")
        self.assertFalse(decision.allowed)
        self.assertIn("block", decision.reason.lower())

    def test_is_real_execution_allowed_false(self):
        from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
        gate = ProviderExecutionGate()
        self.assertFalse(gate.is_real_execution_allowed("any-provider"))

    def test_mock_image_always_allowed(self):
        decision = self.gate.evaluate_mock_image("mock-image")
        self.assertTrue(decision.allowed)

    def test_real_image_prerequisites_present(self):
        prereqs = self.gate.list_real_image_prerequisites()
        self.assertGreater(len(prereqs), 0)

    def test_real_image_gate_json_serializable(self):
        decision = self.gate.evaluate_real_image("mock-image")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])


class TestImageContractFrozen(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.image_provider import (
            ImageProviderRequest, ImageProviderResponse, FORBIDDEN_PARAMETER_KEYS
        )
        self.Request = ImageProviderRequest
        self.Response = ImageProviderResponse
        self.forbidden = FORBIDDEN_PARAMETER_KEYS

    def test_request_frozen(self):
        req = self.Request(
            request_id="r1", provider_id="mock-image",
            mode="mock_image", prompt_text="Test"
        )
        with self.assertRaises(AttributeError):
            req.prompt_text = "changed"

    def test_response_frozen(self):
        resp = self.Response(
            response_id="resp1", request_id="r1",
            provider_id="mock-image", mode="mock_image", status="mock"
        )
        with self.assertRaises(AttributeError):
            resp.status = "changed"

    def test_forbidden_keys_present(self):
        self.assertIn("image_bytes", self.forbidden)
        self.assertIn("image_base64", self.forbidden)
        self.assertIn("api_key", self.forbidden)
        self.assertIn("secret", self.forbidden)

    def test_request_no_binary_fields(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(self.Request)}
        for bad in {"image_bytes", "image_base64", "mask_base64"}:
            self.assertNotIn(bad, field_names)

    def test_response_no_binary_fields(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(self.Response)}
        for bad in {"image_bytes", "image_base64", "raw_image_data"}:
            self.assertNotIn(bad, field_names)

    def test_request_to_dict_no_secret_keys(self):
        req = self.Request(
            request_id="r1", provider_id="mock-image",
            mode="mock_image", prompt_text="Test"
        )
        d = req.to_dict()
        self.assertNotIn("api_key", d)
        self.assertNotIn("secret", d)

    def test_response_to_dict_no_secret_keys(self):
        resp = self.Response(
            response_id="resp1", request_id="r1",
            provider_id="mock-image", mode="mock_image", status="mock"
        )
        d = resp.to_dict()
        self.assertNotIn("api_key", d)
        self.assertNotIn("secret", d)


class TestMockAdapterSafetyBehavior(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.mock_image_provider_adapter import MockImageProviderAdapter
        from aurora_studio.contracts.image_provider import ImageProviderRequest
        self.adapter = MockImageProviderAdapter()
        self.Request = ImageProviderRequest

    def _req(self, mode="mock_image", prompt="Test"):
        return self.Request(
            request_id="r1", provider_id="mock-image",
            mode=mode, prompt_text=prompt
        )

    def test_mock_sets_network_call_false(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertFalse(resp.network_call)

    def test_mock_sets_mock_response_true(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.mock_response)

    def test_execute_real_returns_blocked(self):
        resp = self.adapter.execute(self._req(mode="real_image"), secret_value="fake")
        self.assertEqual(resp.status, "blocked")

    def test_no_image_file_written(self):
        before = set(os.listdir(tempfile.gettempdir()))
        self.adapter.execute_mock(self._req())
        after = set(os.listdir(tempfile.gettempdir()))
        for fname in (after - before):
            for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                self.assertFalse(fname.endswith(ext))

    def test_uri_scheme_is_mock(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.image_uri.startswith("mock://"))

    def test_response_json_serializable(self):
        resp = self.adapter.execute_mock(self._req())
        serialized = json.dumps(resp.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")


class TestCLISmokeImageProvider(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
        )

    def test_image_provider_mock_cli_exits_zero(self):
        r = self._run("image-provider-mock", "--provider", "mock-image",
                      "--prompt", "QA test prompt")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_provider_mock_cli_status_mock(self):
        r = self._run("image-provider-mock", "--provider", "mock-image",
                      "--prompt", "QA test prompt")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["status"], "mock")

    def test_image_provider_mock_cli_no_secret_in_stdout(self):
        r = self._run("image-provider-mock", "--provider", "mock-image",
                      "--prompt", "QA test prompt")
        self.assertNotIn("api_key", r.stdout)
        self.assertNotIn("sk-", r.stdout)

    def test_image_provider_readiness_cli_exits_zero(self):
        r = self._run("image-provider-readiness", "--provider", "mock-image")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_provider_readiness_cli_always_blocked(self):
        r = self._run("image-provider-readiness", "--provider", "mock-image")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["real_image_execution_ready"])

    def test_smoke_command_still_passes(self):
        r = self._run("smoke")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestDocsSafetyFilesExist(unittest.TestCase):

    BASE = Path(__file__).parent.parent / "docs" / "v0_4"

    def test_image_provider_safety_boundary_exists(self):
        self.assertTrue((self.BASE / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").exists())

    def test_image_provider_escalation_rules_exists(self):
        self.assertTrue((self.BASE / "IMAGE_PROVIDER_ESCALATION_RULES.md").exists())

    def test_image_provider_qa_checklist_exists(self):
        self.assertTrue((self.BASE / "IMAGE_PROVIDER_ADAPTER_QA_CHECKLIST.md").exists())

    def test_image_provider_security_review_exists(self):
        self.assertTrue((self.BASE / "IMAGE_PROVIDER_SECURITY_REVIEW.md").exists())

    def test_real_image_provider_user_warning_exists(self):
        self.assertTrue((self.BASE / "REAL_IMAGE_PROVIDER_USER_WARNING.md").exists())


if __name__ == "__main__":
    unittest.main()
