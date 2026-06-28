# Plugin Security Policy — Aurora Studio v0.3

## Principle

Plugins in v0.3 are metadata-only entities.
No plugin code is executed.
No plugin module is imported.

---

## Manifest Security

- Manifests are validated for safe field values.
- entry_point is stored as metadata only — never imported.
- plugin_id must contain only safe characters: [a-zA-Z0-9_\-.]

---

## Permission Security

- All permissions are metadata decisions.
- secret_access: always denied
- execute_code: always denied
- network_access: denied by default, requires approval in future
- file_system_write: denied by default
- provider_access: denied by default

---

## Execution Security

- `is_execution_allowed()` returns False for all plugins.
- `PluginRuntimeStub.execute()` returns blocked status.
- No subprocess is spawned.
- No thread is started for plugin work.

---

## Data Security

- No API keys, tokens, or secrets are passed to plugin code.
- No user data is serialized into plugin calls.
- Plugin manifests store only user-supplied metadata strings.

---

## Audit Trail

Plugin registration and permission evaluations may be logged in future tasks.

---

## Compliance Statement

This policy applies to Aurora Studio v0.3 only.
Plugin execution security must be re-evaluated before any future execution is enabled.
