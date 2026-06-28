# Asset Preview Plan — Aurora Studio v0.3

## Purpose

Define the future asset preview capability for Aurora Studio.
TASK-000091 is planning-only. No preview is implemented. No media file is opened.
No image/video/audio decoding is performed. No external preview dependency is added.
No plugin/provider execution is involved.

---

## Current Asset Behavior

Assets are registered as metadata records (asset_id, name, type, location, tags, state).
The location field stores a path string reference only.
No file content is read, opened, or decoded.
No thumbnail is generated.
No preview is displayed.

---

## Non-Goals for TASK-000091

- No media preview rendering.
- No thumbnail generation.
- No image/video/audio decoding.
- No file content inspection.
- No external preview tools.
- No network fetching for previews.
- No plugin/provider preview execution.

---

## Supported Future Preview Types

Future tasks may implement:
- Image preview (PNG, JPG, WEBP) — stdlib only via tkinter.PhotoImage or similar
- Text preview (plain text, markdown)
- Document preview (via text extraction only, no binary rendering)
- Reference link preview (display URL/path metadata only)

---

## Unsupported Preview Types (Require External Dependencies)

- Video thumbnail generation (requires ffmpeg or similar)
- Audio waveform preview (requires audio library)
- PDF thumbnail (requires PDF rendering library)
- 3D model preview
- Raw camera file preview

---

## Thumbnail Generation Future

Future task: generate thumbnails only from image files using stdlib tkinter.PhotoImage.
Thumbnail must be cached locally under .preview/ in the project folder.
No cloud storage of thumbnails.
No external API calls.
Thumbnail generation must be opt-in and explicit.

---

## Media Metadata Extraction Future

Future task: extract media_kind, mime_hint, extension_hint from location path string only.
No file content read.
No MIME sniffing via file open.
size_hint_bytes and checksum_hint remain user-supplied metadata.

---

## Security Boundary

See ASSET_PREVIEW_SECURITY_BOUNDARY.md.
No executable file handling.
No external preview tools.
No network fetching.

---

## Performance Boundary

Preview generation must be explicit and manual — not automatic on every asset load.
No background preview worker.
No preview on every file system change.

---

## Cache Strategy Future

Preview cache stored under .preview/ in project folder.
Cache invalidation: manual refresh only.
No background cache warmup.

---

## Desktop UI Future

Future asset panel may include:
- Preview pane (image only, tkinter.PhotoImage)
- Thumbnail strip
- Preview status indicator
- "Generate Preview" button (explicit, manual)

---

## Testing Strategy

- Tests verify no media file is opened during normal asset operations.
- Tests verify metadata serialization without file access.
- Tests verify preview_status field is stored and retrieved correctly.
- Future preview tests must mock file I/O.

---

## Future Implementation Tasks

- TASK-FUTURE-001: Image preview with tkinter.PhotoImage
- TASK-FUTURE-002: Thumbnail cache under .preview/
- TASK-FUTURE-003: Preview status indicator in desktop UI

---

## Acceptance Criteria

1. This plan document exists.
2. Security boundary document exists.
3. No preview is implemented in TASK-000091.
4. No media file is opened.
5. No image/video/audio decoding is performed.
6. No external preview dependency is added.
7. No plugin/provider execution is involved.
8. `python -m unittest` passes after TASK-000091.
