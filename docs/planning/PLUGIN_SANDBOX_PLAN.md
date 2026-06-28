# Plugin Sandbox Plan — Aurora Studio

## Purpose

This document describes the planned plugin sandbox system for Aurora Studio.
Plugin execution is not implemented in TASK-000069.
This document is planning only.

## Current Plugin Metadata Behavior

Plugins are stored as PluginMetadata records in memory.
Plugin registration, enable, and disable are supported.
No plugin modules are loaded.
No arbitrary plugin code is executed.
Plugins remain metadata-only.

## Non-goals

- Plugin execution is not implemented in TASK-000069.
- No plugin modules are loaded.
- No arbitrary plugin code is executed.
- No dynamic import of plugin code is performed.
- No subprocess is spawned for plugin execution.

## Plugin Manifest Concept (Future)

Each plugin should declare a manifest:

```json
{
  "plugin_id": "...",
  "name": "...",
  "version": "...",
  "capabilities": ["read_project_metadata", "write_export_artifact"],
  "permissions": [],
  "entry_point": "myplugin.main",
  "disabled_by_default": true
}
```

## Allowed Capabilities (Future)

Future capability examples:

- `read_project_metadata` — read project title, ID, version
- `read_assets` — read asset list and metadata
- `write_export_artifact` — write export artifact to memory
- `read_prompt_templates` — read prompt templates
- `network_access` — make outbound network requests
- `file_system_access` — read/write files within allowed directories
- `provider_access` — call a registered provider adapter

Risky capabilities require explicit permission.
`network_access`, `file_system_access`, and `provider_access` are high-risk.
High-risk capabilities require explicit user confirmation before granting.

## Permission Model (Future)

- All capabilities are denied by default.
- The user grants capabilities at install time.
- Grants are stored per plugin in user config.
- Grants are revocable at any time.
- The plugin manifest must declare required capabilities.
- Undeclared capabilities cannot be granted.

## Disabled by Default Rule

All future plugins must be disabled by default.
Enabling a plugin requires explicit user action.
Plugin execution requires a later sandbox task.

## No Arbitrary Code Execution Rule

No arbitrary plugin code is executed in the current implementation.
Plugin execution must be confined to a sandbox boundary.
Sandbox must prevent access to unauthorized capabilities.
Sandbox design must be reviewed before implementation.

## Trusted Plugin (Future)

A trusted plugin is one that has been reviewed and explicitly authorized.
Trusted plugins may be granted additional capabilities.
Trust is never implicit.
Trust must be documented and auditable.

## Sandbox Boundary (Future)

The sandbox boundary defines what a plugin can and cannot access:

- Allowed: declared capabilities only.
- Denied: file system outside allowed paths.
- Denied: network access unless granted.
- Denied: direct access to manager internals.
- Denied: modification of project metadata without `write_project_metadata` capability.
- Denied: execution of subprocesses.

## Audit Logging (Future)

- Log all capability access by plugins.
- Log plugin enable/disable events.
- Log permission grant/revoke events.
- Logs must not contain user data or secrets.

## Packaging Implications

- Plugin code is not bundled with the base application.
- Plugin installation is a separate user-driven step.
- Base application ships with zero plugins enabled.
- Plugin discovery directory is configurable.

## Failure Handling

- If a plugin fails to load, log the error and continue.
- If a plugin exceeds its declared capabilities, terminate and log.
- Sandbox violations are reported to the user.
- Plugin failures must not crash the application.

## Testing Strategy

- Plugin metadata CRUD is tested (existing tests cover this).
- Sandbox capability model is tested via unit tests (future).
- No live plugin execution in the test suite.
- Capability grant/revoke logic is tested independently.

## Future Implementation Tasks

- TASK-PLUGIN-001: Define plugin manifest schema.
- TASK-PLUGIN-002: Implement capability grant/revoke storage.
- TASK-PLUGIN-003: Implement sandbox boundary enforcement.
- TASK-PLUGIN-004: Implement audit logging for capability access.
- TASK-PLUGIN-005: Implement trusted plugin review workflow.
- TASK-PLUGIN-006: Write sandbox unit tests.

## Risks

- Dynamic code loading is inherently risky.
- Capability model must be exhaustive to prevent bypass.
- Plugin isolation requires OS-level or interpreter-level sandbox.
- Third-party plugins may attempt privilege escalation.

## Acceptance Criteria (Future)

- Plugin manifest schema is defined and validated.
- All capabilities are denied by default.
- User must explicitly grant capabilities.
- Sandbox boundary prevents unauthorized access.
- All sandbox logic is covered by unit tests.
- No live plugin execution in the test suite.
