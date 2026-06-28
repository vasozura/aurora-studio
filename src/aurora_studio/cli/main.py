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
        "provider-smoke",
        help="List providers and run dry-run smoke check.",
    )
    sub.add_parser(
        "plugin-smoke",
        help="Plugin foundation smoke: manifest, permissions, sandbox, stub.",
    )

    # provider-test
    pt = sub.add_parser(
        "provider-test",
        help="Test provider connection — dry/mock only. No network.",
    )
    pt.add_argument("--provider", default="dry-run-local", help="Provider ID to test")
    pt.add_argument("--mode", default="dry_run", choices=["dry_run","mock","blocked_real"], help="Test mode")
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


    # text-provider-mock
    p_text_mock = sub.add_parser(
        "text-provider-mock",
        help="Execute text provider in mock mode — no network, no secret.",
    )
    p_text_mock.add_argument("--provider", default="openai-compatible",
                             help="Provider ID (default: openai-compatible)")
    p_text_mock.add_argument("--prompt", default="Test prompt",
                             help="Prompt text")
    p_text_mock.add_argument("--model", default="",
                             help="Model ID (optional)")

    # text-provider-readiness
    p_text_ready = sub.add_parser(
        "text-provider-readiness",
        help="Report real text provider prerequisites — never executes real calls.",
    )
    p_text_ready.add_argument("--provider", default="openai-compatible",
                              help="Provider ID (default: openai-compatible)")

    return parser



def _cmd_plugin_smoke(_args: argparse.Namespace) -> None:
    """Plugin foundation smoke: manifest validation + permission eval + sandbox + stub."""
    import json
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    from aurora_studio.modules.plugin_sandbox import PluginSandbox
    from aurora_studio.modules.plugin_runtime_stub import PluginRuntimeStub, PluginExecutionRequest

    svc = ApplicationService()
    sess = UISession(svc)

    # Manifest validation
    manifest_data = json.dumps({
        "plugin_id": "smoke-plugin-1",
        "name": "Smoke Plugin",
        "version": "1.0.0",
        "manifest_version": "1.0",
    })
    r_validate = sess.validate_plugin_manifest(manifest_data)
    r_register = sess.register_plugin_manifest(manifest_data)

    # Permission eval
    r_perms = sess.evaluate_plugin_permissions(["read_scenes", "secret_access", "execute_code"])

    # Sandbox policy
    r_sandbox = sess.get_plugin_sandbox_policy("smoke-plugin-1")

    # Stub execution
    r_stub = sess.execute_plugin_stub("smoke-plugin-1", action="run")

    result = {
        "ok": all([r_validate.ok, r_register.ok, r_perms.ok, r_sandbox.ok, r_stub.ok]),
        "mode": "plugin-smoke",
        "manifest_validation_status": (r_validate.payload or {}).get("status"),
        "manifest_registered": (r_register.payload or {}).get("plugin_id"),
        "permissions_evaluated": (r_perms.payload or {}).get("count", 0),
        "sandbox_allowed": (r_sandbox.payload or {}).get("allowed"),
        "stub_status": (r_stub.payload or {}).get("status"),
    }
    print(json.dumps(result, indent=2))

def _cmd_provider_test(args: "argparse.Namespace") -> None:
    """Provider test connection — dry/mock only. No network. No real API key."""
    import json
    from aurora_studio.ui.actions import UISession
    provider_id = getattr(args, "provider", "dry-run-local") or "dry-run-local"
    mode = getattr(args, "mode", "dry_run") or "dry_run"
    sess = UISession()
    result = sess.test_provider_connection(provider_id, mode)
    # Build output: start with payload, then set top-level keys (avoids key collision)
    output: dict = {}
    if result.payload:
        output.update(result.payload)
    output["ok"] = result.ok
    output["command"] = "provider-test"
    output["requested_provider_id"] = provider_id
    output["requested_mode"] = mode
    if not result.ok:
        output["message"] = result.message
    print(json.dumps(output, indent=2))



def _cmd_provider_smoke(_args: argparse.Namespace) -> None:
    """List providers and execute a dry-run — no network, no SDK, no secrets."""
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    sess = UISession(ApplicationService())

    # List providers
    r_list = sess.list_providers()
    providers = r_list.payload.get("providers", []) if r_list.ok else []

    # Dry-run execution
    r_run = sess.execute_provider_dry_run(
        provider_id="dry-run-local",
        source_type="cli-smoke",
        source_id="provider-smoke",
        prompt_text="Provider smoke test: local dry-run only. No network. No SDK.",
    )

    # List logs
    r_logs = sess.list_provider_logs()
    logs = r_logs.payload.get("logs", []) if r_logs.ok else []

    _out({
        "ok": r_run.ok,
        "mode": "provider-smoke",
        "providers": [{"provider_id": p["provider_id"], "state": p["state"]} for p in providers],
        "dry_run": r_run.payload if r_run.ok else {"error": r_run.message},
        "log_count": len(logs),
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _cmd_text_provider_mock(args: "argparse.Namespace") -> None:
    """Mock text provider execution — no network, no secret."""
    import json
    from aurora_studio.ui.actions import UISession
    provider_id = getattr(args, "provider", "openai-compatible") or "openai-compatible"
    prompt = getattr(args, "prompt", "Test prompt") or "Test prompt"
    model_id = getattr(args, "model", "") or ""
    sess = UISession()
    result = sess.execute_text_provider_mock(provider_id, prompt, model_id=model_id)
    output: dict = {}
    if result.payload:
        output.update(result.payload)
    output["ok"] = result.ok
    output["command"] = "text-provider-mock"
    if not result.ok:
        output["message"] = result.message
    print(json.dumps(output, indent=2))


def _cmd_text_provider_readiness(args: "argparse.Namespace") -> None:
    """Evaluate real text provider readiness — reports prerequisites, never executes."""
    import json
    from aurora_studio.ui.actions import UISession
    provider_id = getattr(args, "provider", "openai-compatible") or "openai-compatible"
    sess = UISession()
    result = sess.evaluate_text_provider_real_readiness(provider_id)
    output: dict = {}
    if result.payload:
        output.update(result.payload)
    output["ok"] = result.ok
    output["command"] = "text-provider-readiness"
    if not result.ok:
        output["message"] = result.message
    print(json.dumps(output, indent=2))


_HANDLERS = {
    "smoke": _cmd_smoke,
    "provider-smoke": _cmd_provider_smoke,
    "plugin-smoke": _cmd_plugin_smoke,
    "provider-test": _cmd_provider_test,
    "text-provider-mock": _cmd_text_provider_mock,
    "text-provider-readiness": _cmd_text_provider_readiness,
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
