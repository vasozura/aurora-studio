"""Tests for TASK-000086: Plugin Manifest Validation."""

import json
import unittest

_VALID_MANIFEST = {
    "plugin_id": "my-plugin-1",
    "name": "My Plugin",
    "version": "1.0.0",
    "manifest_version": "1.0",
    "capabilities": ["read_scenes"],
    "permissions": ["read_project_metadata"],
    "entry_point": "my_plugin.main",
    "author": "Test Author",
}


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _validate(data):
    from aurora_studio.modules.plugin_manifest_validator import PluginManifestValidator
    return PluginManifestValidator().validate_manifest_dict(data)


class TestValidManifest(unittest.TestCase):
    def test_valid_manifest_passes(self):
        report = _validate(_VALID_MANIFEST)
        self.assertEqual(report.status, "pass")

    def test_valid_manifest_zero_errors(self):
        report = _validate(_VALID_MANIFEST)
        errors = [i for i in report.issues if i.level == "ERROR"]
        self.assertEqual(len(errors), 0)

    def test_valid_manifest_has_normalized(self):
        report = _validate(_VALID_MANIFEST)
        self.assertIsNotNone(report.normalized_manifest)
        self.assertEqual(report.normalized_manifest.plugin_id, "my-plugin-1")

    def test_report_json_serializable(self):
        report = _validate(_VALID_MANIFEST)
        json.dumps(report.to_dict())


class TestRequiredFieldValidation(unittest.TestCase):
    def test_missing_plugin_id_fails(self):
        data = {**_VALID_MANIFEST}
        del data["plugin_id"]
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_missing_name_fails(self):
        data = {**_VALID_MANIFEST}
        del data["name"]
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_missing_version_fails(self):
        data = {**_VALID_MANIFEST}
        del data["version"]
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_missing_manifest_version_fails(self):
        data = {**_VALID_MANIFEST}
        del data["manifest_version"]
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_empty_plugin_id_fails(self):
        data = {**_VALID_MANIFEST, "plugin_id": ""}
        report = _validate(data)
        self.assertEqual(report.status, "fail")


class TestCapabilitiesAndPermissions(unittest.TestCase):
    def test_capabilities_list_ok(self):
        data = {**_VALID_MANIFEST, "capabilities": ["read_scenes", "read_assets"]}
        report = _validate(data)
        self.assertEqual(report.status, "pass")

    def test_capabilities_not_list_fails(self):
        data = {**_VALID_MANIFEST, "capabilities": "read_scenes"}
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_permissions_list_ok(self):
        data = {**_VALID_MANIFEST, "permissions": ["read_project_metadata"]}
        report = _validate(data)
        self.assertEqual(report.status, "pass")

    def test_permissions_not_list_fails(self):
        data = {**_VALID_MANIFEST, "permissions": {"key": "val"}}
        report = _validate(data)
        self.assertEqual(report.status, "fail")


class TestEntryPointIsMetadataOnly(unittest.TestCase):
    def test_entry_point_produces_info_not_error(self):
        data = {**_VALID_MANIFEST, "entry_point": "my_plugin.main"}
        report = _validate(data)
        # entry_point presence must not cause ERROR or WARN
        errors = [i for i in report.issues if i.level in ("ERROR", "WARN")]
        self.assertEqual(errors, [])

    def test_entry_point_stored_as_string(self):
        data = {**_VALID_MANIFEST, "entry_point": "some.module.path"}
        report = _validate(data)
        if report.normalized_manifest:
            self.assertEqual(report.normalized_manifest.entry_point, "some.module.path")

    def test_entry_point_never_imported(self):
        """Validator must never import any module from entry_point."""
        import sys
        data = {**_VALID_MANIFEST, "entry_point": "nonexistent_plugin_module.main"}
        _validate(data)
        self.assertNotIn("nonexistent_plugin_module", sys.modules)


class TestUnsafePluginId(unittest.TestCase):
    def test_unsafe_plugin_id_with_spaces_fails(self):
        data = {**_VALID_MANIFEST, "plugin_id": "my plugin with spaces"}
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_unsafe_plugin_id_with_slash_fails(self):
        data = {**_VALID_MANIFEST, "plugin_id": "my/plugin"}
        report = _validate(data)
        self.assertEqual(report.status, "fail")

    def test_safe_plugin_id_with_hyphens_passes(self):
        data = {**_VALID_MANIFEST, "plugin_id": "my-safe-plugin-v2"}
        report = _validate(data)
        self.assertEqual(report.status, "pass")


class TestUnknownFields(unittest.TestCase):
    def test_unknown_fields_do_not_crash(self):
        data = {**_VALID_MANIFEST, "unknown_field_xyz": "value", "future_flag": True}
        report = _validate(data)
        self.assertIsNotNone(report)  # must not raise

    def test_non_dict_input_fails(self):
        report = _validate("not a dict")
        self.assertEqual(report.status, "fail")


class TestPluginManagerManifest(unittest.TestCase):
    def test_register_manifest_dict(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        manifest = mgr.register_manifest_dict(_VALID_MANIFEST)
        self.assertEqual(manifest.plugin_id, "my-plugin-1")

    def test_list_plugin_manifests(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        mgr.register_manifest_dict(_VALID_MANIFEST)
        manifests = mgr.list_plugin_manifests()
        self.assertEqual(len(manifests), 1)

    def test_get_plugin_manifest(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        mgr.register_manifest_dict(_VALID_MANIFEST)
        m = mgr.get_plugin_manifest("my-plugin-1")
        self.assertEqual(m.name, "My Plugin")

    def test_invalid_manifest_raises(self):
        from aurora_studio.modules.plugin_manager import PluginManager
        from aurora_studio.core.errors import ValidationError
        mgr = PluginManager()
        with self.assertRaises(ValidationError):
            mgr.register_manifest_dict({"name": "No ID"})

    def test_register_does_not_import_code(self):
        import sys
        from aurora_studio.modules.plugin_manager import PluginManager
        mgr = PluginManager()
        data = {**_VALID_MANIFEST, "entry_point": "nonexistent_xyz.main"}
        mgr.register_manifest_dict(data)
        self.assertNotIn("nonexistent_xyz", sys.modules)


class TestUISessionManifest(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_validate_manifest_ok(self):
        r = self.sess.validate_plugin_manifest(json.dumps(_VALID_MANIFEST))
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["status"], "pass")

    def test_validate_manifest_invalid_json(self):
        r = self.sess.validate_plugin_manifest("not json {{{")
        self.assertFalse(r.ok)

    def test_validate_manifest_missing_fields(self):
        r = self.sess.validate_plugin_manifest(json.dumps({"name": "only name"}))
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["status"], "fail")

    def test_register_manifest_ok(self):
        r = self.sess.register_plugin_manifest(json.dumps(_VALID_MANIFEST))
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["plugin_id"], "my-plugin-1")

    def test_register_manifest_invalid_json(self):
        r = self.sess.register_plugin_manifest("{bad}")
        self.assertFalse(r.ok)

    def test_list_manifests_initially_empty(self):
        r = self.sess.list_plugin_manifests()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 0)

    def test_list_manifests_after_register(self):
        self.sess.register_plugin_manifest(json.dumps(_VALID_MANIFEST))
        r = self.sess.list_plugin_manifests()
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["count"], 1)

    def test_validate_payload_json_serializable(self):
        r = self.sess.validate_plugin_manifest(json.dumps(_VALID_MANIFEST))
        self.assertTrue(r.ok)
        json.dumps(r.payload)


class TestDesktopManifestMethods(unittest.TestCase):
    def test_validate_manifest_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "validate_plugin_manifest"))

    def test_register_manifest_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "register_plugin_manifest"))

    def test_list_manifests_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "list_plugin_manifests"))


if __name__ == "__main__":
    unittest.main()
