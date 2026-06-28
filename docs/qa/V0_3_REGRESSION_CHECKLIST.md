# Aurora Studio v0.3 Regression Checklist

## Automated Tests

- [ ] `python -m unittest` — all tests PASS
- [ ] `python -m aurora_studio.ui.desktop_shell --headless-smoke` — ok=true
- [ ] `python -m aurora_studio.cli smoke` — ok=true
- [ ] `python -m aurora_studio.cli provider-smoke` — ok=true
- [ ] `python -m aurora_studio.cli plugin-smoke` — ok=true, sandbox_allowed=false, stub_status=blocked

## Project Persistence

- [ ] Create demo project
- [ ] Validate bundle
- [ ] Rehydrate bundle

## Scene / Shot / Timeline Workflow

- [ ] Create scene
- [ ] Create shot
- [ ] Timeline workflow

## Asset Metadata Workflow

- [ ] Register asset
- [ ] Update asset metadata
- [ ] Update media metadata (media_kind, mime_hint, extension_hint)
- [ ] Set preview_status

## Character Workflow

- [ ] Create character
- [ ] Link character to scene

## AFL Validation

- [ ] AFL validation runs on project

## Prompt Template Workflow

- [ ] Create prompt template
- [ ] Render prompt preview

## Prompt Export

- [ ] Export prompt preview
- [ ] Export profile render

## Provider Registry

- [ ] List providers (dry-run included)
- [ ] Enable / disable provider

## Provider Dry-Run

- [ ] Execute provider dry-run
- [ ] Log entry created
- [ ] History entry created

## Provider Logs / History

- [ ] List provider logs
- [ ] Clear provider logs
- [ ] List prompt run history

## Prompt Execution Queue

- [ ] Enqueue prompt execution
- [ ] Run next dry-run
- [ ] Cancel queue item

## Batch Prompt Export

- [ ] Create batch prompt export

## Plugin Manifest Validation

- [ ] Validate valid manifest → pass
- [ ] Validate manifest missing plugin_id → fail
- [ ] Register manifest

## Plugin Permission Evaluation

- [ ] List permissions (13 total)
- [ ] evaluate read_scenes → allowed
- [ ] evaluate secret_access → denied
- [ ] evaluate execute_code → denied

## Plugin Runtime

- [ ] Plugin sandbox policy → allowed=false
- [ ] Execute plugin stub → status=blocked

## Backup Creation

- [ ] Create backup (bundle exists)
- [ ] Backup stored in .backups/
- [ ] List backups

## Recovery Report

- [ ] Scan recovery candidates
- [ ] Build recovery report

## Explicit Autosave

- [ ] Enable autosave
- [ ] Mark dirty
- [ ] Write autosave
- [ ] Has recovery → True
- [ ] Discard autosave

## Undo/Redo Safe Action

- [ ] Push update_scene_detail command
- [ ] Undo → ok=true, before_state applied
- [ ] Redo → ok=true, after_state applied
- [ ] Stack cleared → undo_count=0

## Portable Staging

- [ ] Portable staging docs exist

## Portable ZIP RC

- [ ] RC scripts exist
- [ ] RC process doc exists
- [ ] Release notes exist (PENDING status)

## SHA256 Validation

- [ ] RC smoke script validates SHA256
