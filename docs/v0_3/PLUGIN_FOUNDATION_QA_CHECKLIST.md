# Plugin Foundation QA Checklist — Aurora Studio v0.3

## Scope

Covers TASK-000086 through TASK-000089 (Plugin Sandbox Foundation Pack).

---

## Manifest Validation (TASK-000086)

- [ ] contracts/plugin.py defines PluginManifest, PluginManifestValidationIssue, PluginManifestValidationReport
- [ ] validate_manifest_dict() validates required fields: plugin_id, name, version, manifest_version
- [ ] plugin_id with unsafe characters is rejected
- [ ] entry_point is metadata only — never imported
- [ ] normalized_manifest returned on pass/warn
- [ ] to_dict() produces JSON-serializable output
- [ ] UISession validate_plugin_manifest() returns UIActionResult
- [ ] UISession register_plugin_manifest() returns UIActionResult
- [ ] UISession list_plugin_manifests() returns UIActionResult

---

## Permission Model (TASK-000087)

- [ ] 13 known permissions defined
- [ ] read_* permissions allowed by default
- [ ] network_access denied by default
- [ ] file_system_write denied by default
- [ ] provider_access denied by default
- [ ] secret_access always denied (critical)
- [ ] execute_code always denied (critical)
- [ ] evaluate_requested_permissions() returns decisions per permission
- [ ] unknown permissions return not_supported
- [ ] UISession evaluate_plugin_permissions() returns UIActionResult

---

## Sandbox Boundary (TASK-000088)

- [ ] PLUGIN_SANDBOX_BOUNDARY.md exists
- [ ] PLUGIN_SECURITY_POLICY.md exists
- [ ] PluginSandbox.is_execution_allowed() returns False
- [ ] PluginSandbox.get_policy() returns SandboxPolicyResult with allowed=False
- [ ] No subprocess in plugin_sandbox.py
- [ ] No importlib.import_module in plugin_sandbox.py
- [ ] UISession get_plugin_sandbox_policy() returns UIActionResult
- [ ] UISession is_plugin_execution_allowed() returns UIActionResult with allowed=False

---

## Runtime Stub (TASK-000089)

- [ ] PluginRuntimeStub.is_runtime_enabled() returns False
- [ ] PluginRuntimeStub.execute() returns status="blocked"
- [ ] execute() message mentions "disabled"
- [ ] No subprocess in plugin_runtime_stub.py
- [ ] No importlib.import_module in plugin_runtime_stub.py
- [ ] PluginExecutionRequest serializes to dict
- [ ] PluginExecutionResult serializes to dict
- [ ] UISession execute_plugin_stub() returns UIActionResult
- [ ] PluginManager.execute_plugin_stub() returns blocked result

---

## Safety Boundary

- [ ] No plugin code is executed in v0.3
- [ ] No plugin module is dynamically imported
- [ ] No subprocess spawned for plugins
- [ ] No secrets/API keys passed to plugins
- [ ] No provider calls from plugins
- [ ] No network calls from plugins
- [ ] No database access from plugins
