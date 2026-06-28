# Plugin Security Review Checklist — Aurora Studio v0.3

## Overview

This checklist confirms the security boundary for the v0.3 plugin sandbox foundation.

---

## Code Execution Safety

- [ ] No plugin entry_point is imported at any point
- [ ] No exec() or eval() is used with plugin data
- [ ] No subprocess.run/Popen/call is invoked for plugin code
- [ ] No importlib.import_module is called with plugin-supplied strings
- [ ] PluginRuntimeStub.execute() never delegates to actual code

---

## Data Safety

- [ ] Plugin manifests store only user-supplied string metadata
- [ ] No API keys or tokens are passed to plugin code
- [ ] No user project data is serialized into plugin execution requests
- [ ] checksum_hint is metadata string only — no file hashing

---

## Network Safety

- [ ] network_access permission is denied by default
- [ ] No HTTP requests made during manifest validation
- [ ] No HTTP requests made during permission evaluation
- [ ] No HTTP requests made during sandbox policy query
- [ ] No HTTP requests made during stub execution

---

## File System Safety

- [ ] file_system_write permission is denied by default
- [ ] No file content is read during manifest validation
- [ ] No file is opened during permission evaluation

---

## Secret Safety

- [ ] secret_access permission is always denied (critical risk)
- [ ] execute_code permission is always denied (critical risk)
- [ ] No environment variables are exposed to plugin code
- [ ] No API key lookups are performed during stub execution

---

## Manifest ID Safety

- [ ] plugin_id validated: only [a-zA-Z0-9_\-.] allowed
- [ ] Unsafe plugin IDs (spaces, slashes, etc.) are rejected with ERROR

---

## Review Sign-Off

Review status: APPROVED FOR v0.3 (metadata-only, no execution)

Note: This checklist must be re-evaluated before any future plugin execution is enabled.
