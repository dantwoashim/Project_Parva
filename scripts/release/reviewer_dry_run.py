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


DETERMINISTIC_TIMESTAMP = "2026-01-01T00:00:00+00:00"

SAFE_CLAIMS = [
    "Local/offline proof packs can be verified from committed artifacts.",
    "The reviewer dry run exercises civil, Panchanga, and payroll/date-risk examples without live API access.",
    "Panchanga results are computed/method-backed decision support with explicit non-authority boundaries.",
]

FORBIDDEN_CLAIMS = [
    "No government authority.",
    "No legal, tax, payroll, or banking authority.",
    "No official future-date authority.",
    "No official Panchanga or ritual authority.",
    "No external certification, registry acceptance, package publication, adoption, or customer proof unless real evidence exists.",
    "No real JPL-kernel execution is claimed unless PARVA_JPL_KERNEL_PATH is configured and verified.",
]


def _run(label: str, command: list[str], env: dict[str, str], *, expected_status: str = "pass") -> dict[str, object]:
    result = subprocess.run(command, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True, check=False)
    status = "pass" if result.returncode == 0 else "fail"
    if expected_status == "skip":
        status = "skip" if result.returncode == 0 else "fail"
    summary_lines = (result.stdout or result.stderr).strip().splitlines()
    return {
        "label": label,
        "command": " ".join(command),
        "exit_code": result.returncode,
        "status": status,
        "expected_status": expected_status,
        "summary": summary_lines[-3:] if summary_lines else [""],
    }


def _jpl_status(env: dict[str, str]) -> dict[str, object]:
    kernel = env.get("PARVA_JPL_KERNEL_PATH", "").strip()
    if not kernel:
        return {
            "label": "optional JPL kernel lane",
            "command": "PARVA_JPL_KERNEL_PATH not configured",
            "exit_code": 0,
            "status": "skip",
            "expected_status": "skip",
            "summary": [
                "Skipped honestly: configure PARVA_JPL_KERNEL_PATH and expected hash to run the real JPL lane.",
                "Default Panchanga proof fixtures remain pinned-fixture/method-backed, not real JPL-kernel output.",
            ],
        }
    return _run(
        "optional JPL kernel lane",
        [sys.executable, "-m", "pytest", "tests/integration/test_jpl_provider_optional.py", "-q"],
        env,
    )


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
    lines.extend(["", "## Safe Claims", ""])
    lines.extend(f"- {claim}" for claim in payload["safe_claims"])  # type: ignore[index]
    lines.extend(["", "## Forbidden Claims", ""])
    lines.extend(f"- {claim}" for claim in payload["forbidden_claims"])  # type: ignore[index]
    lines.extend(["", "## Expected Outputs", ""])
    for key, value in payload["expected_outputs"].items():  # type: ignore[index]
        lines.append(f"- {key}: `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Skip npm install and run bounded proof/security checks.")
    parser.add_argument("--deterministic", action="store_true", help="Use pinned timestamps for snapshot/reviewer checks.")
    parser.add_argument("--skip-local-kernel", action="store_true", help="Diagnostic mode for negative-path tests only.")
    parser.add_argument("--civil-proofpack", default="examples/external/proofpacks/civil-conversion.proofpack.json")
    parser.add_argument("--panchanga-proofpack", default="examples/external/proofpacks/panchanga-summary.proofpack.json")
    parser.add_argument("--payroll-timepack", default="examples/external/timepacks/payroll-date-risk.timepack.json")
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
                args.civil_proofpack,
            ],
        ),
        (
            "panchanga proofpack",
            [
                sys.executable,
                "-m",
                "parva.cli",
                "verify-proofpack",
                args.panchanga_proofpack,
            ],
        ),
        (
            "payroll timepack",
            [
                sys.executable,
                "-m",
                "parva.cli",
                "verify-timepack",
                args.payroll_timepack,
            ],
        ),
        ("public claims", [sys.executable, "scripts/release/check_public_claims.py"]),
        ("public surface security", [sys.executable, "scripts/release/check_public_surface_security.py"]),
    ]
    if args.skip_local_kernel:
        commands.insert(1, ("local-kernel package", [sys.executable, "-c", "print('skipped by explicit diagnostic flag')"]))
    elif not args.quick:
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
    results.append(_jpl_status(env))
    status = "pass" if all(item["status"] == "pass" for item in results) else "fail"
    if all(item["status"] in {"pass", "skip"} for item in results) and any(item["status"] == "skip" for item in results):
        status = "pass"
    payload = {
        "schema": "parva-reviewer-dry-run-v1",
        "generated_at": DETERMINISTIC_TIMESTAMP
        if args.deterministic
        else datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "external_validation_claimed": False,
        "live_api_required": False,
        "jpl_lane": results[-1],
        "safe_claims": SAFE_CLAIMS,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "expected_outputs": {
            "json_report": args.json_out,
            "markdown_report": args.md_out,
            "civil_proofpack": args.civil_proofpack,
            "panchanga_proofpack": args.panchanga_proofpack,
            "payroll_timepack": args.payroll_timepack,
        },
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
