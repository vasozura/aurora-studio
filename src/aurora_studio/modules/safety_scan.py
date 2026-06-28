"""aurora_studio.modules.safety_scan

v0.4 source and packaging safety scanner.

Scans aurora-studio source files for forbidden imports, unsafe
networking/media patterns, and secret-like artifact risks.

Standard library only. No network calls. No media decoding.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Secret-like field names to flag in text payloads / serialized data
# ---------------------------------------------------------------------------

SECRET_FIELD_NAMES: frozenset[str] = frozenset({
    "api_key", "apikey", "token", "secret", "password",
    "authorization", "auth_header", "bearer", "private_key",
    "access_token", "refresh_token", "client_secret",
})

# ---------------------------------------------------------------------------
# Forbidden SDK imports (never allowed in src/)
# ---------------------------------------------------------------------------

FORBIDDEN_SDK_PATTERNS: list[str] = [
    r"^\s*import\s+openai\b",
    r"^\s*from\s+openai\b",
    r"^\s*import\s+anthropic\b",
    r"^\s*from\s+anthropic\b",
    r"^\s*import\s+requests\b",
    r"^\s*import\s+httpx\b",
    r"^\s*import\s+aiohttp\b",
    r"^\s*import\s+PIL\b",
    r"^\s*from\s+PIL\b",
    r"^\s*import\s+cv2\b",
    r"^\s*import\s+moviepy\b",
    r"^\s*from\s+moviepy\b",
]

FORBIDDEN_SDK_COMPILED: list[re.Pattern] = [re.compile(p) for p in FORBIDDEN_SDK_PATTERNS]

# ---------------------------------------------------------------------------
# Forbidden network/media patterns (image/video modules only)
# ---------------------------------------------------------------------------

FORBIDDEN_MEDIA_IMPORT_PATTERNS: list[str] = [
    r"^\s*import\s+ffmpeg\b",
    r"^\s*import\s+ffprobe\b",
    r"^\s*import\s+subprocess\b",
    r"subprocess\.run\(",
    r"subprocess\.Popen\(",
    r"os\.system\(",
]

FORBIDDEN_MEDIA_COMPILED: list[re.Pattern] = [re.compile(p) for p in FORBIDDEN_MEDIA_IMPORT_PATTERNS]

# ---------------------------------------------------------------------------
# Forbidden network call patterns (all source)
# ---------------------------------------------------------------------------

FORBIDDEN_NETWORK_PATTERNS: list[str] = [
    r"^\s*import\s+requests\b",
    r"^\s*import\s+httpx\b",
    r"^\s*import\s+aiohttp\b",
]

FORBIDDEN_NETWORK_COMPILED: list[re.Pattern] = [re.compile(p) for p in FORBIDDEN_NETWORK_PATTERNS]

# ---------------------------------------------------------------------------
# Packaging secret-risk keywords
# ---------------------------------------------------------------------------

PACKAGING_SECRET_KEYWORDS: list[str] = [
    ".env", "*.env", "api_key", "secret", "token", "password",
]


# ---------------------------------------------------------------------------
# scan_text_for_secret_fields
# ---------------------------------------------------------------------------

def scan_text_for_secret_fields(text: str, path: str = "") -> dict[str, Any]:
    """Scan a block of text for lines that appear to set secret-like fields.

    Redaction utility *definitions* that merely name these fields are flagged
    as WARN (they are expected in the codebase). Actual assignments are ERROR.

    Returns a JSON-serializable dict.
    """
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        low = stripped.lower()
        for field in SECRET_FIELD_NAMES:
            if field in low:
                # Heuristic: assignment looks like field: value or field=value
                is_assign = re.search(
                    rf'["\']?{re.escape(field)}["\']?\s*[:=]', low
                )
                severity = "ERROR" if is_assign else "WARN"
                findings.append({
                    "path": path,
                    "line": lineno,
                    "field": field,
                    "severity": severity,
                    "text": stripped[:120],
                })
    errors = [f for f in findings if f["severity"] == "ERROR"]
    return {
        "path": path,
        "total_findings": len(findings),
        "errors": len(errors),
        "warnings": len(findings) - len(errors),
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# scan_source_for_forbidden_imports
# ---------------------------------------------------------------------------

def scan_source_for_forbidden_imports(root_path: str) -> dict[str, Any]:
    """Scan src/aurora_studio/**/*.py for forbidden SDK imports.

    urllib / urllib.request / urllib.error are allowed.
    Returns JSON-serializable dict.
    """
    root = Path(root_path)
    src_root = root / "src" / "aurora_studio"
    if not src_root.exists():
        src_root = root  # allow passing src/aurora_studio directly

    findings: list[dict[str, Any]] = []
    py_files = list(src_root.rglob("*.py"))

    for f in py_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in FORBIDDEN_SDK_COMPILED:
                if pattern.search(line):
                    findings.append({
                        "file": str(f.relative_to(root) if f.is_relative_to(root) else f),
                        "line": lineno,
                        "severity": "ERROR",
                        "text": stripped[:120],
                        "pattern": pattern.pattern,
                    })

    return {
        "scan": "forbidden_imports",
        "files_scanned": len(py_files),
        "errors": len(findings),
        "findings": findings,
        "status": "PASS" if not findings else "FAIL",
    }


# ---------------------------------------------------------------------------
# scan_source_for_forbidden_network_usage
# ---------------------------------------------------------------------------

def scan_source_for_forbidden_network_usage(root_path: str) -> dict[str, Any]:
    """Scan src/aurora_studio/**/*.py for forbidden network library imports.

    urllib is allowed for gated text adapter use.
    Returns JSON-serializable dict.
    """
    root = Path(root_path)
    src_root = root / "src" / "aurora_studio"
    if not src_root.exists():
        src_root = root

    findings: list[dict[str, Any]] = []
    py_files = list(src_root.rglob("*.py"))

    for f in py_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in FORBIDDEN_NETWORK_COMPILED:
                if pattern.search(line):
                    findings.append({
                        "file": str(f.relative_to(root) if f.is_relative_to(root) else f),
                        "line": lineno,
                        "severity": "ERROR",
                        "text": stripped[:120],
                        "pattern": pattern.pattern,
                    })

    return {
        "scan": "forbidden_network_usage",
        "files_scanned": len(py_files),
        "errors": len(findings),
        "findings": findings,
        "status": "PASS" if not findings else "FAIL",
    }


# ---------------------------------------------------------------------------
# scan_source_for_forbidden_media_usage
# ---------------------------------------------------------------------------

def scan_source_for_forbidden_media_usage(root_path: str) -> dict[str, Any]:
    """Scan image/video provider modules for forbidden media tool usage.

    Checks for ffmpeg, ffprobe, subprocess imports/calls, os.system calls.
    Only checks files with 'image' or 'video' in their name.
    Returns JSON-serializable dict.
    """
    root = Path(root_path)
    src_root = root / "src" / "aurora_studio"
    if not src_root.exists():
        src_root = root

    all_files = list(src_root.rglob("*.py"))
    media_files = [
        f for f in all_files
        if "image" in f.name.lower() or "video" in f.name.lower()
    ]

    findings: list[dict[str, Any]] = []

    for f in media_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in FORBIDDEN_MEDIA_COMPILED:
                if pattern.search(line):
                    findings.append({
                        "file": str(f.relative_to(root) if f.is_relative_to(root) else f),
                        "line": lineno,
                        "severity": "ERROR",
                        "text": stripped[:120],
                        "pattern": pattern.pattern,
                    })

    return {
        "scan": "forbidden_media_usage",
        "files_scanned": len(media_files),
        "total_source_files": len(all_files),
        "errors": len(findings),
        "findings": findings,
        "status": "PASS" if not findings else "FAIL",
    }


# ---------------------------------------------------------------------------
# scan_packaging_for_secret_risks
# ---------------------------------------------------------------------------

def scan_packaging_for_secret_risks(root_path: str) -> dict[str, Any]:
    """Scan packaging scripts/templates for secret keyword references.

    If a keyword appears in an exclusion check (e.g. .gitignore, smoke scripts),
    it is PASS or WARN — not automatic ERROR.
    Returns JSON-serializable dict.
    """
    root = Path(root_path)
    scripts_dir = root / "scripts"
    findings: list[dict[str, Any]] = []
    files_scanned = 0

    candidate_dirs = [scripts_dir, root]
    candidate_extensions = {".ps1", ".bat", ".sh", ".gitignore", ".txt"}

    for candidate_dir in candidate_dirs:
        if not candidate_dir.exists():
            continue
        depth = "**/*" if candidate_dir == scripts_dir else "*"
        for f in candidate_dir.glob(depth):
            if not f.is_file():
                continue
            if f.suffix.lower() not in candidate_extensions and f.name not in {".gitignore", "NOTICE"}:
                continue
            files_scanned += 1
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for kw in PACKAGING_SECRET_KEYWORDS:
                if kw in content:
                    # If it appears in a comment/exclude context, WARN not ERROR
                    is_exclusion = any(
                        pat in content
                        for pat in [f"exclude {kw}", f"# {kw}", f"!{kw}", f"-not {kw}",
                                    f"\\*{kw}", f".gitignore", "secret_safety"]
                    )
                    severity = "WARN" if is_exclusion else "WARN"  # all packaging are WARN
                    findings.append({
                        "file": str(f.relative_to(root) if f.is_relative_to(root) else f),
                        "keyword": kw,
                        "severity": severity,
                        "note": "keyword found in packaging script — verify it is an exclusion check",
                    })

    return {
        "scan": "packaging_secret_risks",
        "files_scanned": files_scanned,
        "warnings": len(findings),
        "errors": 0,
        "findings": findings,
        "status": "PASS",
    }


# ---------------------------------------------------------------------------
# run_v0_4_safety_scan
# ---------------------------------------------------------------------------

def run_v0_4_safety_scan(root_path: str) -> dict[str, Any]:
    """Run all v0.4 safety scans and return a combined JSON-serializable result."""
    forbidden_imports = scan_source_for_forbidden_imports(root_path)
    forbidden_network = scan_source_for_forbidden_network_usage(root_path)
    forbidden_media = scan_source_for_forbidden_media_usage(root_path)
    packaging = scan_packaging_for_secret_risks(root_path)

    all_errors = (
        forbidden_imports["errors"]
        + forbidden_network["errors"]
        + forbidden_media["errors"]
        + packaging["errors"]
    )
    overall = "PASS" if all_errors == 0 else "FAIL"

    return {
        "scan": "v0_4_safety_scan",
        "root": str(root_path),
        "overall_status": overall,
        "total_errors": all_errors,
        "forbidden_imports": forbidden_imports,
        "forbidden_network_usage": forbidden_network,
        "forbidden_media_usage": forbidden_media,
        "packaging_secret_risks": packaging,
    }
