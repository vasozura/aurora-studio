# v0.2 Regression Checklist — Aurora Studio

Run all checks before signing off on the release candidate.

---

## Automated Tests

- [ ] `python -m unittest` — all tests pass, zero failures
- [ ] No unexpected skips

---

## Desktop Headless Smoke

- [ ] `python -m aurora_studio.ui.desktop_shell --headless-smoke` returns ok: true

---

## CLI Smoke

- [ ] `python -m aurora_studio.cli smoke` returns ok: true

---

## Project Create / Open / Save / Load

- [ ] Create new project via CLI: `create-demo`
- [ ] Save project bundle
- [ ] Load project bundle
- [ ] Verify project metadata persists
- [ ] Verify schema_version present in saved file

---

## Scene Detail Workflow

- [ ] Create scene
- [ ] Edit scene detail (location, mood, time of day, description)
- [ ] Verify scene persists after save/load
- [ ] Search scenes by title

---

## Shot Detail Workflow

- [ ] Create shot under scene
- [ ] Edit shot detail (camera, framing, emotion target)
- [ ] Verify shot persists after save/load
- [ ] Search shots by title
- [ ] Filter shots by scene ID

---

## Timeline Workflow

- [ ] Create timeline
- [ ] Add timeline items
- [ ] View timeline summary with duration
- [ ] Verify timeline persists after save/load

---

## Asset Browser Workflow

- [ ] Import asset
- [ ] View asset list
- [ ] Edit asset metadata
- [ ] Search/filter assets by type, state, tag
- [ ] Verify asset persists after save/load

---

## Asset Linking Workflow

- [ ] Link asset to scene
- [ ] Link asset to shot
- [ ] Link asset to character
- [ ] List asset links
- [ ] Verify links persist after save/load

---

## Character Detail Workflow

- [ ] Create character
- [ ] Edit character detail (visual description, role, personality)
- [ ] Verify character persists after save/load
- [ ] Search characters by name

---

## Character Reference Workflow

- [ ] Add character reference asset
- [ ] View character reference list
- [ ] Remove character reference
- [ ] Verify references persist after save/load

---

## AFL Validation Workflow

- [ ] Run AFL validation on scene
- [ ] Run AFL validation on shot
- [ ] View validation report
- [ ] Check issue counts

---

## Prompt Template Workflow

- [ ] List default templates
- [ ] Create custom template
- [ ] Render template for scene
- [ ] Render template for shot
- [ ] Render template for character
- [ ] Verify custom template persists after save/load

---

## Prompt Preview Workflow

- [ ] Render prompt preview from scene
- [ ] Render prompt preview from shot
- [ ] Save preview as export artifact
- [ ] Verify artifact status is draft

---

## Export Profile Workflow

- [ ] List default profiles
- [ ] Create custom profile
- [ ] Render with profile for scene
- [ ] Save profile render as export artifact
- [ ] Verify artifact records profile_id
- [ ] Verify custom profile persists after save/load

---

## Search/Filter Workflow

- [ ] Search scenes — empty query returns all
- [ ] Search scenes — query matches by title
- [ ] Search shots — filter by scene_id
- [ ] Search assets — filter by type
- [ ] Search characters — filter by status
- [ ] Search exports — filter by artifact type

---

## JSON Hardening Workflow

- [ ] Save bundle — schema_version present
- [ ] Save again — backup created in .backups/
- [ ] Load corrupt JSON — friendly error
- [ ] Load missing project_metadata — validation error
- [ ] export_bundle_copy — creates valid file
- [ ] import_bundle_copy — loads bundle
- [ ] validate_bundle_file — reports ok

---

## Packaging Scripts Still Inspectable

- [ ] Packaging scripts exist and are readable
- [ ] No API keys in packaging scripts
- [ ] No provider SDK in packaging scripts
