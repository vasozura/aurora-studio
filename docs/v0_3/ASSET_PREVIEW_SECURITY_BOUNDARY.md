# Asset Preview Security Boundary — Aurora Studio v0.3

## Status

TASK-000091 is planning-only.
No preview is implemented.
No media file is opened.
No image/video/audio decoding is performed.
No external preview dependency is added.
No plugin/provider execution is involved.

---

## No Media Decoding in TASK-000091

No image decoding library is called.
No video frame extraction is performed.
No audio waveform is generated.
Media bytes are never read into memory.

---

## No Thumbnail Generation in TASK-000091

No thumbnail file is created.
No image scaling or resizing is performed.
No preview cache is populated.

---

## No File Content Inspection in TASK-000091

Asset location is stored as a path string only.
No file is opened.
No file content is read.
No MIME sniffing is performed.
No file header is parsed.

---

## No Executable File Handling

Asset preview must never execute scripts, binaries, or arbitrary file content.
File type is determined from extension string metadata only, never by executing the file.

---

## No External Preview Tools

No ffmpeg, ImageMagick, Pillow, or any third-party preview tool is invoked.
No subprocess is spawned for preview generation.
No shell command executes against asset files.

---

## No Network Fetching

No asset content is fetched from a remote URL.
No CDN or cloud storage is accessed for preview generation.
No network request is made during asset metadata operations.

---

## No Plugin Preview Execution

No plugin is invoked to generate asset previews.
Plugin execution remains disabled in v0.3 (see PLUGIN_SANDBOX_BOUNDARY.md).

---

## Future Safe Preview Rules

Any future preview implementation must:
- Use only stdlib-safe image loading (e.g., tkinter.PhotoImage for PNG/GIF)
- Never execute arbitrary file content
- Never call external tools via subprocess
- Never fetch remote content
- Store cached previews locally only, under .preview/ in the project folder
- Be triggered explicitly by user action only
- Validate file extension before attempting any preview
- Never load audio or video content without a clearly scoped future task
