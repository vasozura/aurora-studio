"""Tests for TASK-000102: User API Key Entry Boundary.

No network calls. No provider SDK. Standard library only.
"""

import json
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestRedactSecret(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_secret_redaction import redact_secret
        self.redact = redact_secret

    def test_redact_empty_string(self):
        self.assertEqual(self.redact(""), "<empty>")

    def test_redact_whitespace_only(self):
        self.assertEqual(self.redact("   "), "<empty>")

    def test_redact_short_value(self):
        result = self.redact("abc")
        self.assertNotIn("abc", result)
        self.assertNotEqual(result, "abc")

    def test_redact_long_value(self):
        result = self.redact("sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456")
        self.assertEqual(result, "<redacted>")
        self.assertNotIn("sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456", result)

    def test_redact_medium_value(self):
        result = self.redact("mypassword123")
        self.assertNotIn("mypassword123", result)

    def test_redact_does_not_return_real_key(self):
        real_key = "sk-realapikeyABCDEFGH12345678"
        result = self.redact(real_key)
        self.assertNotEqual(result, real_key)


class TestLooksLikeSecret(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_secret_redaction import looks_like_secret
        self.fn = looks_like_secret

    def test_long_alphanumeric_looks_like_secret(self):
        self.assertTrue(self.fn("ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"))

    def test_openai_key_looks_like_secret(self):
        self.assertTrue(self.fn("sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678"))

    def test_bearer_token_looks_like_secret(self):
        self.assertTrue(self.fn("Bearer ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))

    def test_short_word_does_not_look_like_secret(self):
        self.assertFalse(self.fn("hello"))

    def test_empty_does_not_look_like_secret(self):
        self.assertFalse(self.fn(""))

    def test_normal_sentence_does_not_look_like_secret(self):
        self.assertFalse(self.fn("the quick brown fox"))


class TestSanitizePayload(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_secret_redaction import sanitize_provider_config_payload
        self.sanitize = sanitize_provider_config_payload

    def test_api_key_redacted(self):
        result = self.sanitize({"api_key": "real-key-value", "provider_id": "openai"})
        self.assertEqual(result["api_key"], "<redacted>")
        self.assertEqual(result["provider_id"], "openai")

    def test_token_redacted(self):
        result = self.sanitize({"token": "mytoken123"})
        self.assertEqual(result["token"], "<redacted>")

    def test_secret_redacted(self):
        result = self.sanitize({"secret": "topsecret"})
        self.assertEqual(result["secret"], "<redacted>")

    def test_password_redacted(self):
        result = self.sanitize({"password": "pass123"})
        self.assertEqual(result["password"], "<redacted>")

    def test_non_secret_fields_preserved(self):
        result = self.sanitize({"provider_id": "openai", "name": "OpenAI"})
        self.assertEqual(result["provider_id"], "openai")
        self.assertEqual(result["name"], "OpenAI")

    def test_nested_dict_sanitized(self):
        result = self.sanitize({"config": {"api_key": "secret", "name": "test"}})
        self.assertEqual(result["config"]["api_key"], "<redacted>")
        self.assertEqual(result["config"]["name"], "test")

    def test_empty_dict_returns_empty(self):
        result = self.sanitize({})
        self.assertEqual(result, {})


class TestProviderKeyEntryState(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.provider_config import ProviderKeyEntryState
        self.cls = ProviderKeyEntryState

    def test_to_dict_does_not_include_real_key(self):
        state = self.cls(
            provider_id="openai",
            has_user_input=True,
            redacted_value="<redacted>",
            status="entered_not_saved",
        )
        d = state.to_dict()
        self.assertNotIn("api_key", d)
        self.assertNotIn("secret", d)
        self.assertEqual(d["redacted_value"], "<redacted>")

    def test_to_dict_json_serializable(self):
        state = self.cls(provider_id="openai", status="empty")
        serialized = json.dumps(state.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["provider_id"], "openai")

    def test_default_status_is_empty(self):
        state = self.cls(provider_id="openai")
        self.assertEqual(state.status, "empty")

    def test_has_user_input_defaults_false(self):
        state = self.cls(provider_id="openai")
        self.assertFalse(state.has_user_input)

    def test_message_contains_not_saved(self):
        state = self.cls(provider_id="openai")
        self.assertIn("Not saved", state.message)


class TestProviderSecretPlaceholder(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.provider_config import ProviderSecretPlaceholder
        self.cls = ProviderSecretPlaceholder

    def test_to_dict_never_includes_real_key(self):
        p = self.cls(provider_id="openai", redacted_value="<redacted>", status="redacted")
        d = p.to_dict()
        self.assertNotIn("api_key", d)
        self.assertEqual(d["redacted_value"], "<redacted>")

    def test_to_dict_json_serializable(self):
        p = self.cls(provider_id="openai")
        serialized = json.dumps(p.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["provider_id"], "openai")


class TestUISessionKeyEntry(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_preview_provider_key_entry_returns_redacted(self):
        result = self.sess.preview_provider_key_entry("openai", "sk-REALKEY12345678901234567890")
        self.assertTrue(result.ok)
        self.assertNotEqual(result.payload["redacted_value"], "sk-REALKEY12345678901234567890")
        self.assertEqual(result.payload["redacted_value"], "<redacted>")

    def test_preview_provider_key_entry_empty_key(self):
        result = self.sess.preview_provider_key_entry("openai", "")
        self.assertTrue(result.ok)
        self.assertIn(result.payload["status"], ("empty", "entered_not_saved"))

    def test_preview_provider_key_entry_empty_provider_id_fails(self):
        result = self.sess.preview_provider_key_entry("", "somekey")
        self.assertFalse(result.ok)

    def test_preview_payload_json_serializable(self):
        result = self.sess.preview_provider_key_entry("openai", "mykey12345")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertNotEqual(parsed["payload"]["redacted_value"], "mykey12345")

    def test_clear_provider_key_entry_ok(self):
        result = self.sess.clear_provider_key_entry("openai")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "cleared")

    def test_clear_provider_key_entry_empty_id_fails(self):
        result = self.sess.clear_provider_key_entry("")
        self.assertFalse(result.ok)

    def test_sanitize_provider_config_payload_strips_api_key(self):
        result = self.sess.sanitize_provider_config_payload(
            {"api_key": "real-secret", "provider_id": "openai"}
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["sanitized"]["api_key"], "<redacted>")
        self.assertEqual(result.payload["sanitized"]["provider_id"], "openai")

    def test_sanitize_payload_json_serializable(self):
        result = self.sess.sanitize_provider_config_payload({"token": "abc", "name": "test"})
        serialized = json.dumps(result.to_dict())
        self.assertIn("redacted", serialized)


class TestNoRealKeyInDesktopMethods(unittest.TestCase):

    def test_desktop_shell_has_key_boundary_methods(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        sess = UISession()
        self.assertTrue(hasattr(sess, "preview_provider_key_entry"))
        self.assertTrue(hasattr(sess, "clear_provider_key_entry"))
        self.assertTrue(hasattr(sess, "sanitize_provider_config_payload"))


if __name__ == "__main__":
    unittest.main()
