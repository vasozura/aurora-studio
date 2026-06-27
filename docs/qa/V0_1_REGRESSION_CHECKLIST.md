# v0.1 Regression Checklist

Document ID: V0_1_REGRESSION_CHECKLIST
Version: 0.1.0
Status: QA checklist — fill in during QA review
Task: TASK-000049

Instructions: Tick each checkbox as PASS during QA review.
Mark any failure as FAIL and open a blocker before proceeding to go/no-go.

---

## Repository Sanity

- [ ] Repository root contains `src/`, `tests/`, `scripts/`, `docs/`, `build/`, `packaging/`, `release-notes/`.
- [ ] `pyproject.toml` exists and has not been modified for runtime dependencies.
- [ ] `build/requirements-build.txt` exists and contains `pyinstaller`.
- [ ] `build/pyinstaller/aurora_studio_desktop.spec` exists.
- [ ] `.gitignore` contains `dist/`, `build/`, `dist-portable/`, `release-candidates/`.
- [ ] No `.env` file or provider key file is committed.
- [ ] No EXE file is committed to the repository.
- [ ] No ZIP release artifact is committed to the repository.

---

## Unit Tests

- [ ] `python -m unittest` exits 0 from repository root.
- [ ] All tests pass without requiring a display.
- [ ] All tests pass without requiring PyInstaller.
- [ ] All tests pass without requiring a built EXE.
- [ ] No test requires a network connection.
- [ ] No test requires a database.
- [ ] No test calls a provider API.
- [ ] No test executes plugin code.

---

## Core Managers

- [ ] `SceneManager` creates and lists scenes.
- [ ] `ShotManager` creates shots linked to scenes.
- [ ] `TimelineManager` creates timelines and manages items.
- [ ] `AssetManager` registers, marks missing, and archives assets.
- [ ] `CharacterManager` creates characters and manages reference assets.
- [ ] `AFLManager` validates AFL structure (structural only).
- [ ] `ExportArtifactManager` creates, marks ready, and marks failed export artifacts.
- [ ] `PluginManager` registers, enables, and disables plugins (metadata only).

---

## Application Service

- [ ] `ApplicationService` initialises without errors.
- [ ] `ApplicationService.create_project()` returns a project record.
- [ ] `ApplicationService.open_project()` accepts a valid path.
- [ ] `ApplicationService.create_scene()` delegates to `SceneManager`.
- [ ] `ApplicationService.create_shot()` delegates to `ShotManager`.
- [ ] All `ApplicationService` methods return dataclass records.
- [ ] No `ApplicationService` method calls a provider.
- [ ] No `ApplicationService` method executes plugin code.

---

## Persistence

- [ ] `save_bundle()` writes `aurora_bundle.json` to the project path.
- [ ] Bundle file is valid JSON.
- [ ] Bundle file contains scenes, shots, timelines, assets, characters, AFL reports, export artifacts, plugin metadata.
- [ ] No provider keys appear in the bundle file.
- [ ] No plugin code is written to the bundle file.

---

## Rehydration

- [ ] `load_and_rehydrate_bundle()` reads and restores state from `aurora_bundle.json`.
- [ ] Scenes, shots, timelines, assets, characters are restored after rehydration.
- [ ] Active project and workspace IDs are restored.
- [ ] Rehydrated state matches pre-save state.
- [ ] `python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project` exits 0.

---

## CLI

- [ ] `python -m aurora_studio.cli smoke` exits 0 and prints valid JSON.
- [ ] `python -m aurora_studio.cli create-demo --path ./tmp-demo-project --title "Demo Project"` exits 0.
- [ ] `python -m aurora_studio.cli validate-bundle --path ./tmp-demo-project` exits 0.
- [ ] `python -m aurora_studio.cli rehydrate-bundle --path ./tmp-demo-project` exits 0.
- [ ] CLI does not require a display.
- [ ] CLI does not call providers.
- [ ] CLI does not execute plugins.

---

## Desktop Import Safety

- [ ] `import aurora_studio.ui.desktop_shell` does not open a window.
- [ ] `import aurora_studio.ui.desktop_shell` does not require a display.
- [ ] `import aurora_studio.ui.desktop_shell` does not import tkinter at module level.
- [ ] `headless_smoke()` function is callable without a display.
- [ ] `UISession()` is constructable without a display.

---

## Desktop Headless Smoke

- [ ] `python -m aurora_studio.ui.desktop_shell --headless-smoke` exits 0.
- [ ] Output is valid JSON.
- [ ] JSON contains `"ok": true`.
- [ ] JSON contains `"application": "aurora-studio"`.
- [ ] JSON contains `"shortcuts"` dict with Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+R, Ctrl+L, F5, Escape.
- [ ] JSON contains `"app_state"` with all expected collections.

---

## Desktop Manual Smoke

*(Requires display — Windows recommended)*

- [ ] Window opens with title `Aurora Studio`.
- [ ] Top project bar is visible (path, title, Create, Open, Save Bundle, Load Bundle, Refresh).
- [ ] Workspace summary panel is visible.
- [ ] All 7 tabs are visible: Scenes & Shots, Timeline, Assets, Characters, AFL, Exports, Plugins.
- [ ] Status label is visible.
- [ ] Log panel is visible.
- [ ] Clear Log button works.
- [ ] Escape clears status label.
- [ ] F5 refreshes without crash.
- [ ] Ctrl+R refreshes without crash.

---

## Project Workflow

- [ ] Create project with valid path and title: status shows success.
- [ ] Save Bundle with active project: `aurora_bundle.json` is written.
- [ ] Load Bundle (Load Bundle button): state is restored.
- [ ] Open project: status shows success.
- [ ] Empty project path: shows user-friendly error, does not crash.
- [ ] Empty project title: shows user-friendly error, does not crash.

---

## Scene Workflow

- [ ] Create Scene with title: scene appears in scene list.
- [ ] Scene list updates after Refresh.
- [ ] Selecting a scene in the list updates selected Scene ID.
- [ ] Scene count in workspace summary updates.

---

## Shot Workflow

- [ ] Create Shot with title using selected scene: shot appears in shot list.
- [ ] Create Shot with no scene selected: shows user-friendly error, does not crash.
- [ ] Shot list updates after Refresh.
- [ ] Shot count in workspace summary updates.

---

## Timeline Workflow

- [ ] Create Timeline: timeline appears in timeline list.
- [ ] Add Timeline Item with type and target: item appears when timeline selected.
- [ ] Remove Timeline Item: item removed.
- [ ] Move Timeline Item: order updated.
- [ ] Timeline count in workspace summary updates.
- [ ] Timeline item action with no timeline selected: shows user-friendly error.

---

## Asset Workflow

- [ ] Import/Register Asset: asset appears in asset list.
- [ ] Mark Asset Missing: status updates.
- [ ] Archive Asset: asset status updates.
- [ ] Asset count in workspace summary updates.
- [ ] Asset action with no asset selected: shows user-friendly error.

---

## Character Workflow

- [ ] Create Character: character appears in character list.
- [ ] Add Reference Asset to character: reference added.
- [ ] Remove Reference Asset: reference removed.
- [ ] Archive Character: character status updates.
- [ ] Character count in workspace summary updates.
- [ ] Character action with no character selected: shows user-friendly error.

---

## AFL Smoke Workflow

- [ ] Validate AFL structure: AFL report appears in AFL report list.
- [ ] AFL validation is structural only — no semantic model is called.
- [ ] AFL report count in workspace summary updates.
- [ ] AFL action with no target ref: shows user-friendly error.

---

## Export Smoke Workflow

- [ ] Create Export Artifact: artifact appears in export list.
- [ ] Mark Export Ready: status updates.
- [ ] Mark Export Failed: status updates.
- [ ] Export artifact count in workspace summary updates.
- [ ] Export action with no artifact selected: shows user-friendly error.

---

## Plugin Metadata Smoke Workflow

- [ ] Register Plugin: plugin appears in plugin list.
- [ ] Enable Plugin: plugin status updates (metadata only).
- [ ] Disable Plugin: plugin status updates (metadata only).
- [ ] Plugin panel does not execute plugin code.
- [ ] Plugin panel does not load plugin modules.
- [ ] Plugin count in workspace summary updates.
- [ ] Plugin action with no plugin selected: shows user-friendly error.

---

## Status / Log Workflow

- [ ] Successful actions append log entry with INFO marker.
- [ ] Validation failures append log entry with ERROR or WARN marker.
- [ ] Clear Log clears only the log panel, not app state.
- [ ] Status label shows latest action result.
- [ ] No console output during GUI actions.

---

## Packaging Smoke

- [ ] `scripts\build_windows_onefolder.bat` exits 0.
- [ ] `dist\AuroraStudio\AuroraStudio.exe` exists after build.
- [ ] `dist\AuroraStudio\AuroraStudio.exe --headless-smoke` exits 0.
- [ ] `scripts\smoke_built_app.bat` exits 0.

---

## Portable Folder Smoke

- [ ] `scripts\stage_windows_portable.bat` exits 0.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\app\AuroraStudio\AuroraStudio.exe` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\run_desktop.bat` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\smoke_desktop.bat` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\README.txt` exists.
- [ ] `dist-portable\AuroraStudio-v0.1.0-windows-portable\NOTICE.txt` exists.
- [ ] `scripts\smoke_portable_folder.bat` exits 0.

---

## Portable ZIP Smoke

- [ ] `scripts\create_portable_zip.bat` exits 0.
- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.zip` exists.
- [ ] `release-candidates\AuroraStudio-v0.1.0-rc1-windows-portable.sha256` exists.
- [ ] SHA-256 checksum matches ZIP.
- [ ] `scripts\smoke_portable_zip.bat` exits 0.
- [ ] ZIP extraction smoke passes.
- [ ] ZIP does not contain `.git`.
- [ ] ZIP does not contain `tests/`.
- [ ] ZIP does not contain `release-candidates/` nested inside itself.
- [ ] ZIP does not contain provider keys.
- [ ] ZIP does not contain `pyproject.toml` or source Python files.

---

## Known Limitations

- [ ] Reviewer has acknowledged: no installer included.
- [ ] Reviewer has acknowledged: no code signing applied.
- [ ] Reviewer has acknowledged: no database included.
- [ ] Reviewer has acknowledged: no provider integration included.
- [ ] Reviewer has acknowledged: no plugin execution enabled.
- [ ] Reviewer has acknowledged: AFL validation is structural only.
- [ ] Reviewer has acknowledged: prompt generation is not implemented.
- [ ] Reviewer has acknowledged: this is not a production-ready release.
