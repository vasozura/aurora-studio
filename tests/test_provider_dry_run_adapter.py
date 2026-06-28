"""Tests for TASK-000079: Provider Dry-Run Adapter."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _make_adapter():
    from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
    return ProviderDryRunAdapter()


class TestProviderRequestContract(unittest.TestCase):
    def test_build_request(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="A beautiful sunset over mountains.",
        )
        self.assertEqual(req.provider_id, "dry-run-local")
        self.assertEqual(req.source_type, "scene")
        self.assertEqual(req.prompt_text, "A beautiful sunset over mountains.")
        self.assertTrue(req.request_id.startswith("req-"))

    def test_request_to_dict_json_serializable(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            provider_id="dry-run-local",
            source_type="shot",
            source_id="sh1",
            prompt_text="Close-up of a hand.",
        )
        json.dumps(req.to_dict())


class TestDryRunAdapterExecute(unittest.TestCase):
    def test_execute_returns_dry_run_status(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="Test prompt.",
        )
        resp = adapter.execute(req)
        self.assertEqual(resp.status, "dry_run")

    def test_execute_response_references_request(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            "dry-run-local", "scene", "s2", "Another test."
        )
        resp = adapter.execute(req)
        self.assertEqual(resp.request_id, req.request_id)
        self.assertEqual(resp.provider_id, "dry-run-local")

    def test_execute_output_text_non_empty(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            "dry-run-local", "", "", "Some prompt text here."
        )
        resp = adapter.execute(req)
        self.assertTrue(resp.output_text.strip())

    def test_execute_output_contains_dry_run_label(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            "dry-run-local", "", "", "Check label."
        )
        resp = adapter.execute(req)
        self.assertIn("DRY-RUN", resp.output_text)

    def test_execute_empty_prompt_raises(self):
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        from aurora_studio.core.errors import ValidationError
        adapter = _make_adapter()
        req = ProviderDryRunAdapter.build_request("dry-run-local", "", "", "   ")
        with self.assertRaises(ValidationError):
            adapter.execute(req)

    def test_response_to_dict_json_serializable(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req = ProviderDryRunAdapter.build_request(
            "dry-run-local", "scene", "s3", "Serialization test."
        )
        resp = adapter.execute(req)
        json.dumps(resp.to_dict())

    def test_response_id_different_each_call(self):
        adapter = _make_adapter()
        from aurora_studio.modules.provider_dry_run import ProviderDryRunAdapter
        req1 = ProviderDryRunAdapter.build_request("dry-run-local", "", "", "Call 1.")
        req2 = ProviderDryRunAdapter.build_request("dry-run-local", "", "", "Call 2.")
        r1 = adapter.execute(req1)
        r2 = adapter.execute(req2)
        self.assertNotEqual(r1.response_id, r2.response_id)

    def test_no_network_call_made(self):
        """Dry-run must never make a network call — verified by import isolation."""
        import sys
        self.assertNotIn("openai", sys.modules)
        self.assertNotIn("anthropic", sys.modules)
        self.assertNotIn("requests", sys.modules)
        self.assertNotIn("httpx", sys.modules)


class TestUISessionDryRun(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_execute_dry_run_ok(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s1",
            prompt_text="A test prompt for dry-run.",
        )
        self.assertTrue(r.ok, r.message)

    def test_execute_dry_run_payload_keys(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="shot",
            source_id="sh1",
            prompt_text="Another dry-run prompt.",
        )
        self.assertTrue(r.ok)
        for key in ("request_id", "response_id", "provider_id", "status", "output_text"):
            self.assertIn(key, r.payload)

    def test_execute_dry_run_status_is_dry_run(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Status check.",
        )
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["status"], "dry_run")

    def test_execute_dry_run_empty_prompt_fails(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="   ",
        )
        self.assertFalse(r.ok)

    def test_execute_dry_run_disabled_provider_fails(self):
        self.sess.disable_provider("dry-run-local")
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Should be blocked.",
        )
        self.assertFalse(r.ok)
        self.assertIn("disabled", r.message.lower())

    def test_execute_dry_run_unknown_provider_fails(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="unknown-provider-xyz",
            source_type="",
            source_id="",
            prompt_text="Should fail.",
        )
        self.assertFalse(r.ok)

    def test_execute_dry_run_json_serializable(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="scene",
            source_id="s99",
            prompt_text="JSON test.",
        )
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_execute_dry_run_default_provider(self):
        # Empty provider_id defaults to dry-run-local
        r = self.sess.execute_provider_dry_run(
            provider_id="",
            source_type="",
            source_id="",
            prompt_text="Default provider test.",
        )
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["provider_id"], "dry-run-local")


class TestDesktopDryRunMethod(unittest.TestCase):
    def test_execute_provider_dry_run_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "execute_provider_dry_run"))


if __name__ == "__main__":
    unittest.main()
