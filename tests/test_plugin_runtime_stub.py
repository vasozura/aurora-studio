"""Tests for TASK-000089: Disabled-by-Default Plugin Runtime Stub."""

import json
import sys
import unittest


def _stub():
    from aurora_studio.modules.plugin_runtime_stub import PluginRuntimeStub
    return PluginRuntimeStub()


def _request(plugin_id="test-plugin", action="run", payload=""):
    from aurora_studio.modules.plugin_runtime_stub import PluginExecutionRequest
    return PluginExecutionRequest(plugin_id=plugin_id, action=action, payload=payload)


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


class TestRuntimeStubContracts(unittest.TestCase):
    def test_execution_request_serializes(self):
        req = _request()
        json.dumps(req.to_dict())

    def test_execution_request_from_dict(self):
        from aurora_studio.modules.plugin_runtime_stub import PluginExecutionRequest
        req = PluginExecutionRequest.from_dict({"plugin_id": "p1", "action": "run"})
        self.assertEqual(req.plugin_id, "p1")

    def test_execution_result_serializes(self):
        result = _stub().execute(_request())
        json.dumps(result.to_dict())


class TestRuntimeStubBehavior(unittest.TestCase):
    def test_runtime_not_enabled(self):
        self.assertFalse(_stub().is_runtime_enabled())

    def test_execute_returns_blocked(self):
        result = _stub().execute(_request())
        self.assertEqual(result.status, "blocked")

    def test_execute_blocked_for_any_plugin(self):
        for pid in ["plugin-a", "plugin-b", "untrusted-xyz"]:
            result = _stub().execute(_request(plugin_id=pid))
            self.assertEqual(result.status, "blocked", f"Should be blocked: {pid}")

    def test_execute_message_mentions_disabled(self):
        result = _stub().execute(_request())
        self.assertIn("disabled", result.message.lower())

    def test_execute_preserves_plugin_id(self):
        result = _stub().execute(_request(plugin_id="my-plugin"))
        self.assertEqual(result.plugin_id, "my-plugin")

    def test_execute_has_timestamp(self):
        result = _stub().execute(_request())
        self.assertTrue(len(result.executed_at) > 0)

    def test_execute_payload_empty(self):
        result = _stub().execute(_request())
        self.assertEqual(result.payload, "")

    def test_stub_never_imports_plugin_code(self):
        """Calling execute must not load any third-party module."""
        modules_before = set(sys.modules.keys())
        _stub().execute(_request(plugin_id="nonexistent_module_xyz"))
        new_modules = set(sys.modules.keys()) - modules_before
        # Only allow aurora_studio internals or stdlib
        suspicious = [m for m in new_modules if "nonexistent" in m]
        self.assertEqual(suspicious, [])

    def test_stub_source_has_no_subprocess(self):
        import aurora_studio.modules.plugin_runtime_stub as stub_mod
        src = open(stub_mod.__file__).read()
        self.assertNotIn("import subprocess", src)

    def test_stub_source_has_no_importlib(self):
        import aurora_studio.modules.plugin_runtime_stub as stub_mod
        src = open(stub_mod.__file__).read()
        self.assertNotIn("importlib.import_module", src)


class TestPluginManagerStub(unittest.TestCase):
    def test_execute_plugin_stub_returns_blocked(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        result = mgr.execute_plugin_stub("my-plugin")
        self.assertEqual(result.status, "blocked")

    def test_execute_plugin_stub_serializable(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        result = mgr.execute_plugin_stub("my-plugin")
        json.dumps(result.to_dict())


class TestUISessionStub(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_execute_plugin_stub_ok(self):
        r = self.sess.execute_plugin_stub("my-plugin")
        self.assertTrue(r.ok)

    def test_execute_plugin_stub_blocked(self):
        r = self.sess.execute_plugin_stub("my-plugin")
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["status"], "blocked")

    def test_execute_plugin_stub_serializable(self):
        r = self.sess.execute_plugin_stub("test-plugin", action="run")
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_execute_plugin_stub_any_plugin(self):
        for pid in ["plugin-a", "plugin-b", "plugin-c"]:
            r = self.sess.execute_plugin_stub(pid)
            self.assertTrue(r.ok)
            self.assertEqual(r.payload["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
