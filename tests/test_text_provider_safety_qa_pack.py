"""Tests for TASK-000110: Text Provider Safety QA Pack.

Source scan tests — verify no forbidden SDK or HTTP library imports exist
in src/aurora_studio/**/*.py. No network calls. Standard library only.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
AURORA_SRC = SRC / "aurora_studio"
DOCS_V0_4 = Path(__file__).parent.parent / "docs" / "v0_4"


def _all_source_files() -> list[Path]:
    return list(AURORA_SRC.rglob("*.py"))


def _file_contains(path: Path, pattern: str) -> bool:
    return pattern in path.read_text()


class TestForbiddenSDKImports(unittest.TestCase):
    """Source scan: no forbidden SDK or HTTP library imports in aurora_studio source."""

    def test_no_import_openai(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "import openai"),
                    f"{f} contains 'import openai'",
                )

    def test_no_from_openai(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "from openai"),
                    f"{f} contains 'from openai'",
                )

    def test_no_import_anthropic(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "import anthropic"),
                    f"{f} contains 'import anthropic'",
                )

    def test_no_from_anthropic(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "from anthropic"),
                    f"{f} contains 'from anthropic'",
                )

    def test_no_import_requests(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "import requests"),
                    f"{f} contains 'import requests'",
                )

    def test_no_import_httpx(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "import httpx"),
                    f"{f} contains 'import httpx'",
                )

    def test_no_import_aiohttp(self):
        for f in _all_source_files():
            with self.subTest(file=f.name):
                self.assertFalse(
                    _file_contains(f, "import aiohttp"),
                    f"{f} contains 'import aiohttp'",
                )

    def test_source_files_found(self):
        files = _all_source_files()
        self.assertGreater(len(files), 5, "Expected multiple source files")


class TestNoSecretStorageInSource(unittest.TestCase):
    """Source scan: no secret persistence patterns in aurora_studio source."""

    def test_adapter_does_not_store_secret_on_self(self):
        adapter_path = AURORA_SRC / "modules" / "openai_compatible_text_adapter.py"
        content = adapter_path.read_text()
        self.assertNotIn("self.secret", content)
        self.assertNotIn("self.api_key", content)
        self.assertNotIn("self.token", content)
        self.assertNotIn("self._secret", content)

    def test_no_secret_written_to_json_in_source(self):
        # Check that no source file contains patterns for writing secrets to json files
        for f in _all_source_files():
            content = f.read_text()
            # No file should write 'api_key' to a JSON dump in a way that persists it
            if "json.dump" in content and "api_key" in content:
                # This is only a concern if they appear in the same line
                for line in content.split('\n'):
                    if "json.dump" in line and "api_key" in line:
                        self.fail(
                            f"{f.name} line writes api_key to json: {line.strip()}"
                        )


class TestDocsExist(unittest.TestCase):
    """Required safety documentation must be present."""

    def test_qa_checklist_exists(self):
        path = DOCS_V0_4 / "TEXT_PROVIDER_ADAPTER_QA_CHECKLIST.md"
        self.assertTrue(path.exists(), f"Missing: {path}")

    def test_security_review_exists(self):
        path = DOCS_V0_4 / "TEXT_PROVIDER_SECURITY_REVIEW.md"
        self.assertTrue(path.exists(), f"Missing: {path}")

    def test_user_warning_exists(self):
        path = DOCS_V0_4 / "REAL_PROVIDER_USER_WARNING.md"
        self.assertTrue(path.exists(), f"Missing: {path}")

    def test_security_review_warns_about_cli_args(self):
        path = DOCS_V0_4 / "TEXT_PROVIDER_SECURITY_REVIEW.md"
        content = path.read_text()
        self.assertIn("command-line argument", content.lower().replace("-", " ")
                      if "command-line argument" not in content else content)

    def test_user_warning_mentions_prompt_sent_outside_machine(self):
        path = DOCS_V0_4 / "REAL_PROVIDER_USER_WARNING.md"
        content = path.read_text()
        self.assertIn("outside this machine", content)

    def test_user_warning_warns_about_shell_history(self):
        path = DOCS_V0_4 / "REAL_PROVIDER_USER_WARNING.md"
        content = path.read_text()
        self.assertIn("shell history", content)

    def test_qa_checklist_has_forbidden_sdk_section(self):
        path = DOCS_V0_4 / "TEXT_PROVIDER_ADAPTER_QA_CHECKLIST.md"
        content = path.read_text()
        self.assertIn("import openai", content)
        self.assertIn("import anthropic", content)


class TestCLIIntegration110(unittest.TestCase):
    """Full integration: CLI commands pass and output is safe."""

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        )

    def test_text_provider_mock_cli_passes(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai",
                          "--prompt", "Safety QA test")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_text_provider_mock_output_no_secret_pattern(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai",
                          "--prompt", "Safety QA test")
        parsed = json.loads(r.stdout)
        self.assertNotIn("api_key", parsed)
        self.assertNotIn("secret", parsed)
        self.assertNotIn("token", parsed)

    def test_text_provider_mock_network_call_false(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai",
                          "--prompt", "Safety QA test")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["network_call"])

    def test_text_provider_readiness_cli_passes(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_text_provider_readiness_not_ready(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["real_execution_ready"])

    def test_text_provider_readiness_no_secret_in_output(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        self.assertNotIn("sk-", r.stdout)
        self.assertNotIn("api_key", r.stdout)


class TestContractSafety110(unittest.TestCase):
    """Contract-level safety checks."""

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_request_to_json_does_not_expose_secret_ref(self):
        from aurora_studio.contracts.text_provider import TextProviderRequest
        r = TextProviderRequest(
            provider_id="openai", prompt="test",
            ephemeral_secret_ref="sk-abc-123456789",
        )
        j = r.to_json()
        self.assertNotIn("sk-abc-123456789", j)

    def test_response_to_dict_has_no_secret_fields(self):
        from aurora_studio.contracts.text_provider import TextProviderResponse
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        r = TextProviderResponse(
            provider_id="openai", request_id="r1", status="mock"
        )
        d = r.to_dict()
        for key in SECRET_FIELD_NAMES:
            self.assertNotIn(key, d)

    def test_gate_decision_to_dict_has_no_secret_fields(self):
        from aurora_studio.contracts.provider_security import (
            ProviderExecutionGateDecision, SECRET_FIELD_NAMES
        )
        d_obj = ProviderExecutionGateDecision(
            provider_id="openai", requested_action="run",
            allowed=False, reason="blocked"
        )
        d = d_obj.to_dict()
        for key in SECRET_FIELD_NAMES:
            self.assertNotIn(key, d)


if __name__ == "__main__":
    unittest.main()
