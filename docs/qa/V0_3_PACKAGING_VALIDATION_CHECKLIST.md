# Aurora Studio v0.3 Packaging Validation Checklist

## Build

- [ ] One-folder build completes without error
- [ ] Portable staging completes without error
- [ ] Portable ZIP created

## ZIP Contents

- [ ] Portable ZIP created successfully
- [ ] SHA256 file created
- [ ] SHA256 checksum verified

## ZIP Extraction

- [ ] ZIP extracts cleanly to temp folder

## Required Top-Level Files

- [ ] run_desktop.bat exists in ZIP
- [ ] smoke_desktop.bat exists in ZIP
- [ ] README.txt exists in ZIP
- [ ] NOTICE.txt exists in ZIP

## Excluded Content Verification

- [ ] No .env files in ZIP
- [ ] No secrets in ZIP
- [ ] No API keys in ZIP
- [ ] No plugin execution packages in ZIP
- [ ] No __pycache__ directories in ZIP
- [ ] No .pytest_cache directories in ZIP
- [ ] No provider SDK packages in ZIP
- [ ] No database files in ZIP

## Smoke Test

- [ ] Portable folder smoke passes
- [ ] Portable ZIP RC smoke passes
