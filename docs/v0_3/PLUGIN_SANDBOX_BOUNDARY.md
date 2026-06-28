# Plugin Sandbox Boundary — Aurora Studio v0.3

## Status

TASK-000088 implements sandbox policy metadata only.
No plugin execution is enabled.
Plugin runtime is disabled by default.

---

## What Is Allowed

- Manifest validation (metadata)
- Permission evaluation (metadata)
- Sandbox policy queries (policy metadata only)
- Disabled runtime stub — always returns blocked

---

## What Is Forbidden in v0.3

- Executing plugin code
- Dynamically importing plugin modules
- Running subprocess for plugin code
- Network access for plugins
- Secret/API key access for plugins
- File system write from plugins (without explicit approval and future implementation)
- Provider execution from plugins
- Plugin-level threading or background workers

---

## Sandbox Policy Decision

`is_execution_allowed()` returns `False` for all plugins in v0.3.

This is enforced by `PluginSandbox` and `PluginRuntimeStub`.

---

## Future Sandbox Implementation

Future tasks may implement:
- Restricted subprocess sandbox
- Permission-gated capability execution
- User-approved network access
- Auditable plugin execution log

All future execution must remain gated behind explicit user approval.

---

## Architecture Boundary Statement

Plugin execution is DISABLED in v0.3.
All plugin methods return a "blocked/disabled" result.
No code from any plugin entry_point is loaded or run.
