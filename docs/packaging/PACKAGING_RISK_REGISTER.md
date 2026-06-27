# Packaging Risk Register

Document ID: PACKAGING_RISK_REGISTER
Version: 0.1.0
Status: Planning only — for TASK-000046 and later
Task: TASK-000045

---

## Purpose

Document known packaging risks for the Windows portable EXE build of Aurora Studio,
their impact, mitigations, and required future validation steps.

---

## Risk Register

---

### RISK-001: tkinter availability in frozen app

**Risk:** PyInstaller may not automatically include `tkinter` and its TCL/TK
runtime DLLs in the frozen bundle. `tkinter` is part of CPython's standard
library but is often omitted from stripped or minimal Python builds.

**Impact:** Desktop shell fails to launch on the user's machine. `ImportError:
No module named '_tkinter'` or missing TCL/TK DLLs.

**Mitigation:**
- Use a full CPython 3.11+ 64-bit Windows installer as the build Python
  (not a minimal embeddable distribution).
- Add `--collect-all tkinter` to PyInstaller spec if needed.
- Explicitly include `tcl86t.dll`, `tk86t.dll`, and the `tcl/` and `tk/`
  folders in the PyInstaller data files list.
- Test on a clean Windows VM without Python installed after each build.

**Future validation step:** Run built EXE on a clean Windows 10 VM. Confirm
window opens. Confirm `--headless-smoke` exits 0.

---

### RISK-002: Windows path handling

**Risk:** Source code uses `pathlib.Path` and `os.path` which generally handle
Windows paths correctly, but hardcoded forward-slash separators or Linux-style
paths may appear in test fixtures or CLI arguments.

**Impact:** Project bundle creation fails or saves to wrong location under
Windows portable install.

**Mitigation:**
- Use `pathlib.Path` consistently throughout source code (already done).
- Avoid hardcoded `/tmp/` paths in user-facing flows.
- Test CLI `create-demo` command with a Windows-native path at build time.

**Future validation step:** Run full CLI smoke on built Windows artifact using
a Windows-native path (`.\tmp-demo-project`).

---

### RISK-003: Current working directory differences

**Risk:** The portable EXE may set the current working directory (CWD) to the
EXE folder or to `%USERPROFILE%` depending on how it is launched. Code that
relies on relative CWD paths may behave differently.

**Impact:** Bundle JSON files or demo projects may be created in unexpected
locations.

**Mitigation:**
- CLI commands must accept explicit `--path` arguments rather than relying on CWD.
- The `run_desktop.bat` and `smoke_desktop.bat` scripts must `cd /d` to the
  portable folder before running.
- Application code must never assume CWD equals the project folder.

**Future validation step:** Launch EXE from the Start Menu (CWD = system32),
from desktop shortcut, and from the portable folder directly. Verify all paths
resolve correctly.

---

### RISK-004: PYTHONPATH differences

**Risk:** In a frozen PyInstaller app, `PYTHONPATH` is not used. Module discovery
relies entirely on what was bundled. Any module not discovered by PyInstaller's
analysis will be missing.

**Impact:** Import errors at runtime for modules not detected by PyInstaller's
static analysis (dynamic imports, `importlib`, plugin-style loading).

**Mitigation:**
- Use `--hidden-import` flags or a PyInstaller spec file to list all required
  `aurora_studio.*` modules explicitly.
- Run `pyi-makespec` once and review the generated `.spec` file before building.
- Do not use `importlib.import_module()` with variable module names in the
  critical path.

**Future validation step:** Run `pyi-archive-viewer` on built EXE to confirm
all required modules are present in the bundle.

---

### RISK-005: Hidden imports

**Risk:** PyInstaller's bytecode analysis may miss dynamically referenced modules,
especially in `aurora_studio.managers.*` if any use `__import__` or string-based
loading.

**Impact:** `ModuleNotFoundError` at runtime when a specific manager or view
model is first used.

**Mitigation:**
- Audit all `import` statements in the codebase before the build task.
- Add a comprehensive `hiddenimports` list to the PyInstaller spec covering all
  `aurora_studio.*` submodules.
- Run the full unit test suite against the built artifact using the bundled Python.

**Future validation step:** Execute all CLI smoke commands and UI smoke against
the built artifact. Run `python -m unittest` via the bundled Python inside
`_internal/`.

---

### RISK-006: CLI module entry points

**Risk:** `python -m aurora_studio.cli` relies on `__main__.py` being present in
the `aurora_studio/cli/` package. PyInstaller may not bundle `__main__.py` files
correctly if the module is only invoked via `-m`.

**Impact:** `python -m aurora_studio.cli smoke` fails inside the portable build.

**Mitigation:**
- Add an explicit `AuroraStudio-cli.exe` entry point in the PyInstaller spec
  pointing to `aurora_studio/cli/main.py`.
- Or bundle CLI commands as subcommands of the main EXE via `--cli` flag.
- Confirm `__main__.py` presence in `aurora_studio/cli/` before build.

**Future validation step:** Run `AuroraStudio.exe --cli smoke` or equivalent
from the portable folder and confirm exit code 0.

---

### RISK-007: Temporary project cleanup

**Risk:** The smoke scripts create `./tmp-demo-project` relative to the CWD.
In the portable EXE scenario, CWD may be read-only (e.g., `Program Files`).

**Impact:** `create-demo` fails with a permission error.

**Mitigation:**
- The smoke scripts already use `rmdir /s /q tmp-demo-project` before running.
- Redirect demo project creation to a user-writable path (`%TEMP%\aurora-demo`
  or adjacent `tmp/` folder) in the portable smoke scripts.
- Document this redirect in the portable smoke batch files.

**Future validation step:** Run `smoke_desktop.bat` from within the portable
folder with UAC elevated and non-elevated. Confirm no permission errors.

---

### RISK-008: Antivirus false positives

**Risk:** PyInstaller EXEs are frequently flagged as suspicious by Windows
Defender and third-party antivirus due to the generic packing format being
used by malware.

**Impact:** End user's antivirus quarantines or blocks `AuroraStudio.exe`
before it can run.

**Mitigation:**
- Use PyInstaller one-folder mode (`--onedir`) rather than one-file mode
  (`--onefile`). One-file mode is significantly more likely to trigger AV.
- Submit built EXE to `virustotal.com` after build and document results.
- Consider code signing in a later task to reduce false positive rate.
- Document known false positives in the release notes.

**Future validation step:** Scan built artifact on `virustotal.com`. Document
any flagging vendors. Test on a machine with Windows Defender enabled.

---

### RISK-009: Unsigned EXE warnings

**Risk:** Windows SmartScreen will display a warning (`Windows protected your
PC`) for unsigned EXEs from unknown publishers, especially downloaded from the
web or copied from a USB drive.

**Impact:** End user must click through a SmartScreen warning on first launch.
Some enterprise environments block unsigned EXEs entirely.

**Mitigation:**
- Document expected SmartScreen warning in user README.
- Plan code signing via an EV code signing certificate in a later task.
- Provide alternative: users can run from source using `scripts\run_desktop.bat`
  which does not trigger SmartScreen.

**Future validation step:** Test on a fresh Windows 11 machine. Document
SmartScreen behavior. Plan signing task.

---

### RISK-010: Large binary size

**Risk:** PyInstaller bundles the entire CPython runtime, stdlib, and all
imported packages. The resulting folder may be 50–150 MB even for a minimal
application.

**Impact:** Large download and disk usage. Slow first-launch if antivirus
scans the entire folder.

**Mitigation:**
- Use PyInstaller `--exclude-module` to strip unused stdlib modules
  (e.g., `test`, `distutils`, `unittest` if not needed in release build).
- Do not bundle dev dependencies.
- Target size under 80 MB for initial release.

**Future validation step:** Measure folder size after build. Document in release
notes. Identify largest contributors using `pyi-archive-viewer`.

---

### RISK-011: User data vs app bundle separation

**Risk:** If users place their project folders inside the `_internal/` or app
bundle directory, updates or reinstalls may delete user data.

**Impact:** Data loss for users who store projects inside the portable folder.

**Mitigation:**
- Document clearly that user project folders must be stored outside the
  portable app folder, or inside the `data/` subdirectory specifically.
- Default CLI `--path` suggestions should use `%USERPROFILE%\Documents\Aurora`.
- Never automatically delete or overwrite the `data/` directory during updates.

**Future validation step:** Document update procedure. Test that reinstalling
the portable app does not delete `data/`.

---

### RISK-012: No provider keys bundled

**Risk:** A future contributor may accidentally commit or bundle a provider API
key (OpenAI, Anthropic, RunwayML, etc.) inside the build artifact.

**Impact:** Credential leak. Security incident.

**Mitigation:**
- Provider keys must never be committed to the repository.
- `.gitignore` must exclude any `.env` or key files.
- The PyInstaller spec must explicitly exclude any file matching `*.env`,
  `*.key`, `*_key*`, `*secret*`.
- CI build pipeline must run a secret scanning step before packaging.

**Future validation step:** Scan built artifact contents for known key patterns
before release. Confirm `.gitignore` covers key file patterns.

---

### RISK-013: No plugin execution

**Risk:** Plugin metadata is stored but plugin code is never loaded or executed.
A future contributor may accidentally wire plugin loading into the startup path.

**Impact:** Arbitrary code execution from untrusted plugin sources.

**Mitigation:**
- Plugin manager stores metadata only. No `importlib` calls for plugin modules.
- Code review required before any plugin loading code is introduced.
- TASK-000046 boundary document explicitly forbids plugin execution.

**Future validation step:** Confirm `plugin_manager.py` contains no dynamic
import calls. Confirm no plugin `.py` files are loaded at startup.

---

### RISK-014: Headless smoke reliability

**Risk:** The headless smoke command (`--headless-smoke`) must remain safe to
run without a display, without a project, and without any external services.
Future changes to `UISession` or `DesktopShell` could accidentally introduce a
display dependency into the headless path.

**Impact:** CI/CD pipeline smoke step fails. Portable build smoke fails on
headless build servers.

**Mitigation:**
- `headless_smoke()` in `desktop_shell.py` must never import `tkinter`.
- `UISession` must remain constructable without a display.
- All new `UISession` actions must be tested headlessly.
- Add a test that calls `headless_smoke()` and confirms no `tkinter` import
  occurred.

**Future validation step:** Run `--headless-smoke` on every build. Add to CI.
Confirm no `tkinter` in `headless_smoke` call stack.
