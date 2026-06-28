# Aurora Studio v0.3 Final Release Evidence Checklist

Complete all items before changing decision from PENDING to GO.

## Automated Tests

- [ ] python -m unittest passed
- [ ] desktop headless smoke passed
- [ ] CLI smoke passed

## Project Lifecycle

- [ ] demo project created
- [ ] bundle validation passed
- [ ] bundle rehydration passed

## Provider Workflow

- [ ] provider dry-run passed

## Plugin Safety

- [ ] plugin runtime blocked passed

## Recovery / Autosave / Undo

- [ ] backup/recovery passed
- [ ] autosave explicit mode passed
- [ ] undo/redo minimal passed

## Packaging

- [ ] portable ZIP RC created
- [ ] SHA256 verified
- [ ] ZIP extracted
- [ ] manual desktop QA completed

## Security

- [ ] no secrets bundled
- [ ] no provider SDKs bundled
- [ ] no API keys bundled

## Review

- [ ] known limitations reviewed
- [ ] final decision report signed off
