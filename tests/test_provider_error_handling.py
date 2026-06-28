"""Tests for TASK-000084: Provider Error Handling."""

import json
import unittest


def _norm(msg, **kw):
    from aurora_studio.modules.provider_error_handling import normalize_error
    return normalize_error(msg, **kw)


class TestNormalizeError(unittest.TestCase):
    def test_normalize_validation_error(self):
        err = _norm("source_type must not be empty.", provider_id="dry-run-local")
        self.assertEqual(err.error_type, "validation_error")

    def test_normalize_provider_disabled(self):
        err = _norm("Provider dry-run-local is disabled.")
        self.assertEqual(err.error_type, "provider_disabled")

    def test_normalize_provider_not_configured(self):
        err = _norm("Provider not found: unknown-provider", provider_id="unknown-provider")
        self.assertEqual(err.error_type, "provider_not_configured")

    def test_normalize_unknown_fallback(self):
        err = _norm("Something completely unrecognized happened.")
        self.assertEqual(err.error_type, "unknown")

    def test_normalize_from_exception(self):
        from aurora_studio.modules.provider_error_handling import normalize_error
        exc = ValueError("must not be empty.")
        err = normalize_error(exc, provider_id="p1")
        self.assertEqual(err.error_type, "validation_error")

    def test_error_has_id(self):
        err = _norm("Test error.")
        self.assertTrue(err.error_id.startswith("err-"))

    def test_error_to_dict_json_serializable(self):
        err = _norm("Test error.", provider_id="p1")
        json.dumps(err.to_dict())

    def test_explicit_error_type_respected(self):
        from aurora_studio.modules.provider_error_handling import normalize_error
        err = normalize_error("Timeout occurred.", error_type="timeout")
        self.assertEqual(err.error_type, "timeout")

    def test_invalid_error_type_becomes_unknown(self):
        from aurora_studio.modules.provider_error_handling import normalize_error
        err = normalize_error("Some error.", error_type="quantum_failure")
        self.assertEqual(err.error_type, "unknown")


class TestRetryableMapping(unittest.TestCase):
    def test_network_error_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertTrue(is_retryable("network_error"))

    def test_timeout_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertTrue(is_retryable("timeout"))

    def test_rate_limited_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertTrue(is_retryable("rate_limited"))

    def test_validation_error_not_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertFalse(is_retryable("validation_error"))

    def test_provider_disabled_not_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertFalse(is_retryable("provider_disabled"))

    def test_blocked_not_retryable(self):
        from aurora_studio.modules.provider_error_handling import is_retryable
        self.assertFalse(is_retryable("blocked"))


class TestToUserMessage(unittest.TestCase):
    def test_user_message_no_traceback(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_user_message
        err = normalize_error("source_type must not be empty.")
        msg = to_user_message(err)
        self.assertNotIn("Traceback", msg)
        self.assertNotIn("File ", msg)

    def test_user_message_compact(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_user_message
        err = normalize_error("Provider is disabled.")
        msg = to_user_message(err)
        self.assertLessEqual(len(msg), 300)

    def test_user_message_readable(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_user_message
        err = normalize_error("Provider not found: p1", provider_id="p1")
        msg = to_user_message(err)
        self.assertTrue(msg.strip())


class TestSecretSanitization(unittest.TestCase):
    def test_api_key_redacted(self):
        from aurora_studio.modules.provider_error_handling import normalize_error
        err = normalize_error("api_key=sk-secret123 was invalid.")
        self.assertNotIn("sk-secret123", err.message)

    def test_bearer_token_redacted(self):
        from aurora_studio.modules.provider_error_handling import normalize_error
        err = normalize_error("bearer: myBearerTokenHere")
        self.assertNotIn("myBearerTokenHere", err.message)


class TestToLogPayload(unittest.TestCase):
    def test_log_payload_json_serializable(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_log_payload
        err = normalize_error("Something failed.", provider_id="p1", source_type="scene")
        payload = to_log_payload(err)
        json.dumps(payload)

    def test_log_payload_has_required_keys(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_log_payload
        err = normalize_error("Error.", provider_id="p1")
        payload = to_log_payload(err)
        for key in ("error_id", "provider_id", "error_type", "message", "is_retryable"):
            self.assertIn(key, payload)

    def test_log_payload_no_traceback(self):
        from aurora_studio.modules.provider_error_handling import normalize_error, to_log_payload
        err = normalize_error("Error without traceback.")
        payload = to_log_payload(err)
        self.assertNotIn("Traceback", str(payload))


class TestUISessionCompactErrors(unittest.TestCase):
    def setUp(self):
        from aurora_studio.services.application_service import ApplicationService
        from aurora_studio.ui.actions import UISession
        self.sess = UISession(ApplicationService())

    def test_invalid_provider_returns_compact_error(self):
        r = self.sess.get_provider("nonexistent-xyz")
        self.assertFalse(r.ok)
        self.assertIsInstance(r.message, str)
        self.assertTrue(r.message.strip())

    def test_disabled_provider_dry_run_returns_compact_error(self):
        self.sess.disable_provider("dry-run-local")
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="Should be blocked.",
        )
        self.assertFalse(r.ok)
        self.assertNotIn("Traceback", r.message)

    def test_empty_prompt_dry_run_compact_error(self):
        r = self.sess.execute_provider_dry_run(
            provider_id="dry-run-local",
            source_type="",
            source_id="",
            prompt_text="",
        )
        self.assertFalse(r.ok)
        self.assertIsInstance(r.message, str)


if __name__ == "__main__":
    unittest.main()
