#!/usr/bin/env python3
"""Bounded external-review dry run for offline Parva proof artifacts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from node_runtime import build_npm_command, resolve_node_runtime  # noqa: E402


def _env() -> dict[str, str]:
    env = os.environ.copy()
    parts = [str(PROJECT_ROOT), str(PROJECT_ROOT / "backend"), str(PROJECT_ROOT / "packages" / "parva-python")]
    if env.get("PYTHONPATH"):
        parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _run(label: str, command: list[str], env: dict[str, str]) -> dict[str, object]:
    result = subprocess.run(command, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True, check=False)
    return {
        "label": label,
        "command": " ".join(command),
        "exit_code": result.returncode,
        "status": "pass" if result.returncode == 0 else "fail",
        "summary": (result.stdout or result.stderr).strip().splitlines()[-1:] or [""],
    }


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# Project Parva Reviewer Dry Run",
        "",
        "This is a local/offline review dry run. It does not prove external validation, adoption, registry acceptance, package publication, or official authority.",
        "",
        f"- Status: {payload['status']}",
        f"- Commands: {len(payload['commands'])}",
        "",
        "| Check | Status | Exit |",
        "| --- | --- | ---: |",
    ]
    for item in payload["commands"]:  # type: ignore[index]
        lines.append(f"| {item['label']} | {item['status']} | {item['exit_code']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Skip npm install and run bounded proof/security checks.")
    parser.add_argument("--json-out", default="reports/external_reviewer_dry_run/review_report.json")
    parser.add_argument("--md-out", default="reports/external_reviewer_dry_run/review_report.md")
    args = parser.parse_args()

    env = _env()
    node_runtime = resolve_node_runtime()
    commands: list[tuple[str, list[str]]] = [
        ("environment", [sys.executable, "scripts/verify_environment.py"]),
        (
            "civil proofpack",
            [
                sys.executable,
                "-m",
                "parva.cli",
                "verify-proofpack",
                "examples/external/proofpacks/civil-conversion.proofpack.json",
            ],
        ),
        (
            "panchanga proofpack",
            [
                sys.executable,
                "-m",
                "parva.cli",
                "verify-proofpack",
                "examples/external/proofpacks/panchanga-summary.proofpack.json",
            ],
        ),
        (
            "payroll timepack",
            [
                sys.executable,
                "-m",
                "parva.cli",
                "verify-timepack",
                "examples/external/timepacks/payroll-date-risk.timepack.json",
            ],
        ),
        ("public claims", [sys.executable, "scripts/release/check_public_claims.py"]),
        ("public surface security", [sys.executable, "scripts/release/check_public_surface_security.py"]),
    ]
    if not args.quick:
        commands.insert(1, ("local-kernel package", [sys.executable, "scripts/release/check_local_kernel_package.py"]))
    else:
        commands.insert(
            1,
            (
                "local-kernel tests",
                build_npm_command(["--prefix", "packages/parva-local-kernel", "test"], node_runtime),
            ),
        )

    results = [_run(label, command, env) for label, command in commands]
    status = "pass" if all(item["status"] == "pass" for item in results) else "fail"
    payload = {
        "schema": "parva-reviewer-dry-run-v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "external_validation_claimed": False,
        "jpl_lane": "skipped unless PARVA_JPL_KERNEL_PATH is configured",
        "commands": results,
    }
    json_out = PROJECT_ROOT / args.json_out
    md_out = PROJECT_ROOT / args.md_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(md_out, payload)
    print(json.dumps({"status": status, "json": args.json_out, "markdown": args.md_out}, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
