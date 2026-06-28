# v0.2 Scope Freeze Checklist — Aurora Studio

This checklist must be completed before proceeding to release candidate validation.

---

## Editor Scope

- [ ] Scene detail editor implemented and tested
- [ ] Shot detail editor implemented and tested
- [ ] Scene/Shot inspector implemented and tested
- [ ] Timeline editor implemented and tested
- [ ] Timeline duration summary implemented and tested

---

## Prompt/Export Scope

- [ ] Asset browser implemented and tested
- [ ] Asset linking implemented and tested
- [ ] Character detail editor implemented and tested
- [ ] Character reference workflow implemented and tested
- [ ] Expanded AFL validation implemented and tested
- [ ] Prompt template system implemented and tested
- [ ] Prompt export preview implemented and tested
- [ ] Export profiles implemented and tested
- [ ] Project search and filters implemented and tested

---

## Persistence Scope

- [ ] JSON import/export hardening implemented and tested
- [ ] Backup before overwrite verified
- [ ] Corrupt JSON handling verified
- [ ] schema_version present in all saved bundles
- [ ] export_bundle_copy and import_bundle_copy tested

---

## Planning Scope

- [ ] Autosave planning documentation complete (AUTOSAVE_PLAN.md)
- [ ] Undo/redo planning documentation complete (UNDO_REDO_PLAN.md)
- [ ] Provider adapter planning documentation complete (PROVIDER_ADAPTER_PLAN.md)
- [ ] Plugin sandbox planning documentation complete (PLUGIN_SANDBOX_PLAN.md)

---

## Explicit Exclusions

- [ ] Confirmed: no provider integration in this release
- [ ] Confirmed: no plugin execution in this release
- [ ] Confirmed: no database in this release
- [ ] Confirmed: no autosave implementation in this release
- [ ] Confirmed: no undo/redo implementation in this release
- [ ] Confirmed: no installer in this release
- [ ] Confirmed: no MSIX in this release
- [ ] Confirmed: no code signing in this release
- [ ] Confirmed: no production readiness claim

---

## Regression Readiness

- [ ] python -m unittest passes with zero failures
- [ ] Desktop headless smoke passes
- [ ] CLI smoke passes
- [ ] Full regression checklist reviewed (V0_2_REGRESSION_CHECKLIST.md)

---

## Packaging Readiness

- [ ] Portable ZIP packaging script is present and inspectable
- [ ] ZIP does not contain API keys
- [ ] ZIP does not contain provider SDK
- [ ] ZIP contains required source files

---

## Known Limitations

- [ ] Known limitations documented in release notes
- [ ] Known limitations accepted by reviewer
