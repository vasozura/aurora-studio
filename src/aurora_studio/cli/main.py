"""Aurora Studio CLI smoke tool — argparse-based debug/smoke interface.

Not a final application interface.
Not a GUI, web API, or database interface.
Does not call providers.
Does not execute plugins.
Standard-library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aurora_studio.core.errors import ValidationError
from aurora_studio.services import ApplicationService


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _out(data: dict) -> None:
    """Print success JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _err(message: str, code: int = 2) -> None:
    """Print error JSON to stderr and exit."""
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2),
          file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bundle_counts(bundle) -> dict:
    """Return collection count dict from a ProjectBundle."""
    return {
        "scene_count": len(bundle.scenes),
        "shot_count": len(bundle.shots),
        "timeline_count": len(bundle.timelines),
        "asset_count": len(bundle.assets),
        "character_count": len(bundle.characters),
        "afl_report_count": len(bundle.afl_reports),
        "export_artifact_count": len(bundle.export_artifacts),
        "plugin_count": len(bundle.plugins),
    }


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _cmd_smoke(_args: argparse.Namespace) -> None:
    ApplicationService()  # instantiate to confirm no import errors
    _out({"ok": True, "application": "aurora-studio", "mode": "smoke"})


def _cmd_create_project(args: argparse.Namespace) -> None:
    svc = ApplicationService()
    metadata = svc.create_project(args.path, args.title)
    _out(metadata.to_dict())


def _cmd_create_demo(args: argparse.Namespace) -> None:
    svc = ApplicationService()
    metadata = svc.create_project(args.path, args.title)
    scene = svc.create_scene("Opening Scene")
    shot = svc.create_shot(scene.scene_id, "Opening Shot")
    bundle_path = svc.save_bundle(args.path)
    _out({
        "project_id": metadata.project_id,
        "scene_id": scene.scene_id,
        "shot_id": shot.shot_id,
        "bundle_path": str(bundle_path),
    })


def _cmd_inspect_bundle(args: argparse.Namespace) -> None:
    svc = ApplicationService()
    bundle = svc.load_bundle(args.path)
    _out({"schema_version": bundle.schema_version, **_bundle_counts(bundle)})


def _cmd_validate_bundle(args: argparse.Namespace) -> None:
    """Load bundle without rehydrating; report validity and counts."""
    svc = ApplicationService()
    bundle = svc.load_bundle(args.path)  # raises ValidationError on invalid
    _out({
        "ok": True,
        "valid": True,
        "schema_version": bundle.schema_version,
        **_bundle_counts(bundle),
    })


def _cmd_rehydrate_bundle(args: argparse.Namespace) -> None:
    """Load and rehydrate bundle into a fresh ApplicationService; report counts."""
    svc = ApplicationService()
    result = svc.load_and_rehydrate_bundle(args.path)
    bundle = result["bundle"]
    summary = result["summary"]
    state = svc.get_workspace_state()
    _out({
        "ok": True,
        "schema_version": bundle.schema_version,
        "rehydrated": True,
        "workspace_restored": summary["workspace_restored"],
        "scenes": summary["scenes"],
        "shots": summary["shots"],
        "timelines": summary["timelines"],
        "assets": summary["assets"],
        "characters": summary["characters"],
        "afl_reports": summary["afl_reports"],
        "export_artifacts": summary["export_artifacts"],
        "plugins": summary["plugins"],
        "active_project_id": state.active_project_id,
        "active_scene_id": state.active_scene_id,
        "active_shot_id": state.active_shot_id,
    })


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m aurora_studio.cli",
        description=(
            "Aurora Studio CLI smoke tool. "
            "Exercises the non-GUI core from a terminal. "
            "Not a final application interface."
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # smoke
    sub.add_parser(
        "smoke",
        help="Verify ApplicationService instantiates; print JSON health check.",
    )

    # create-project
    cp = sub.add_parser(
        "create-project",
        help="Create a local project and print metadata JSON.",
    )
    cp.add_argument("--path", required=True, help="Project directory path.")
    cp.add_argument("--title", required=True, help="Project title.")

    # create-demo
    cd = sub.add_parser(
        "create-demo",
        help="Create a project with one scene, one shot, and a local bundle.",
    )
    cd.add_argument("--path", required=True, help="Project directory path.")
    cd.add_argument("--title", required=True, help="Project title.")

    # inspect-bundle
    ib = sub.add_parser(
        "inspect-bundle",
        help="Load a local bundle and print summary counts.",
    )
    ib.add_argument("--path", required=True, help="Bundle file or project directory.")

    # validate-bundle
    vb = sub.add_parser(
        "validate-bundle",
        help="Validate a local bundle and print counts. Does not rehydrate managers.",
    )
    vb.add_argument("--path", required=True, help="Bundle file or project directory.")

    # rehydrate-bundle
    rb = sub.add_parser(
        "rehydrate-bundle",
        help="Load and rehydrate a bundle into fresh service; print restored counts.",
    )
    rb.add_argument("--path", required=True, help="Bundle file or project directory.")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_HANDLERS = {
    "smoke": _cmd_smoke,
    "create-project": _cmd_create_project,
    "create-demo": _cmd_create_demo,
    "inspect-bundle": _cmd_inspect_bundle,
    "validate-bundle": _cmd_validate_bundle,
    "rehydrate-bundle": _cmd_rehydrate_bundle,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    handler = _HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(0)

    try:
        handler(args)
    except ValidationError as exc:
        _err(str(exc), code=2)
    except Exception as exc:  # pylint: disable=broad-except
        _err(f"Unexpected error: {exc}", code=1)


if __name__ == "__main__":
    main()
