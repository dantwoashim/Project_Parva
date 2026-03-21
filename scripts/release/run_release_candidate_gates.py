#!/usr/bin/env python3
"""Run the release-candidate gate sequence from a clean checkout."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from node_runtime import resolve_node_runtime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
LOCAL_SIGNING_DIR = PROJECT_ROOT / ".verify" / "release"
LOCAL_SIGNING_KEY = LOCAL_SIGNING_DIR / "provenance_attestation.key"
LOCAL_SIGNING_KEY_ID = LOCAL_SIGNING_DIR / "provenance_attestation.key_id"
BROWSER_SMOKE_REPORT = PROJECT_ROOT / "reports" / "release" / "browser_smoke.json"
GOLDEN_JOURNEYS_REPORT = PROJECT_ROOT / "reports" / "release" / "golden_journeys.json"
BUNDLE_BUDGET_REPORT = PROJECT_ROOT / "reports" / "release" / "frontend_bundle_budget.json"
SECURITY_AUDIT_REPORT = PROJECT_ROOT / "reports" / "security_audit.json"
LAUNCH_SIGNOFF_DOCUMENT = PROJECT_ROOT / "docs" / "LAUNCH_SIGNOFF.md"


def _run_step(index: int, total: int, label: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"[RC {index}/{total}] {label}")
    resolved_command = list(command)
    resolved_executable = shutil.which(command[0], path=(env or os.environ).get("PATH"))
    if resolved_executable:
        resolved_command[0] = resolved_executable
    subprocess.run(resolved_command, cwd=PROJECT_ROOT, check=True, env=env)


def _default_local_key_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"local-release-{stamp}"


def _ensure_signed_provenance_env(env: dict[str, str]) -> dict[str, str]:
    if env.get("PARVA_PROVENANCE_ATTESTATION_KEY") or env.get("PARVA_PROVENANCE_ATTESTATION_KEY_FILE"):
        return env

    LOCAL_SIGNING_DIR.mkdir(parents=True, exist_ok=True)
    if not LOCAL_SIGNING_KEY.exists():
        LOCAL_SIGNING_KEY.write_text(secrets.token_hex(32), encoding="utf-8")
    if not LOCAL_SIGNING_KEY_ID.exists():
        LOCAL_SIGNING_KEY_ID.write_text(_default_local_key_id(), encoding="utf-8")

    env["PARVA_PROVENANCE_ATTESTATION_KEY_FILE"] = str(LOCAL_SIGNING_KEY)
    env.setdefault(
        "PARVA_PROVENANCE_ATTESTATION_KEY_ID",
        LOCAL_SIGNING_KEY_ID.read_text(encoding="utf-8").strip(),
    )
    print(
        "[RC] Using provisioned local provenance signing profile "
        f"({LOCAL_SIGNING_KEY_ID.read_text(encoding='utf-8').strip()})."
    )
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frontend-clean-install",
        action="store_true",
        help="Run npm ci before frontend validation. Recommended for CI and clean checkouts.",
    )
    parser.add_argument(
        "--allow-dirty-archive",
        action="store_true",
        help="Pass --allow-dirty to the source archive step for local debugging only.",
    )
    parser.add_argument(
        "--skip-browser-smoke",
        action="store_true",
        help="Skip the browser smoke step when a browser runtime is unavailable.",
    )
    parser.add_argument(
        "--require-signed-provenance",
        action="store_true",
        help="Require signed provenance attestation for the provenance readiness step.",
    )
    args = parser.parse_args(argv)

    python = sys.executable
    node_runtime = resolve_node_runtime()
    shared_env = node_runtime.build_env() if node_runtime else dict(os.environ)

    if node_runtime and node_runtime.managed:
        print(f"[RC] Using {node_runtime.describe()} for Node/NPM steps.")
    if args.require_signed_provenance:
        shared_env = _ensure_signed_provenance_env(shared_env)

    archive_command = [python, "scripts/release/package_source_archive.py"]
    if args.allow_dirty_archive:
        archive_command.append("--allow-dirty")

    provenance_command = [python, "scripts/release/check_provenance_readiness.py"]
    if args.require_signed_provenance:
        provenance_command.append("--require-signed")

    steps: list[tuple[str, list[str]]] = [
        ("Verify toolchain", [python, "scripts/verify_environment.py"]),
        ("Repository hygiene", [python, "scripts/release/check_repo_hygiene.py"]),
        ("Render blueprint", [python, "scripts/release/check_render_blueprint.py"]),
        ("SDK install surface", [python, "scripts/release/check_sdk_install.py"]),
        ("Contract freeze", [python, "scripts/release/check_contract_freeze.py"]),
        ("Provenance readiness", provenance_command),
        ("Backend test suite", [python, "-m", "pytest", "-q"]),
        ("Spec conformance", [python, "scripts/spec/run_conformance_tests.py"]),
    ]

    if args.frontend_clean_install:
        steps.append(("Frontend clean install", ["npm", "ci", "--prefix", str(FRONTEND_DIR)]))

    steps.extend(
        [
            ("Frontend lint", ["npm", "--prefix", str(FRONTEND_DIR), "run", "lint"]),
            ("Frontend tests", ["npm", "--prefix", str(FRONTEND_DIR), "run", "test"]),
            ("Frontend build", ["npm", "--prefix", str(FRONTEND_DIR), "run", "build"]),
            (
                "Frontend bundle budget",
                [
                    python,
                    "scripts/release/check_frontend_bundle_budget.py",
                    "--report-path",
                    str(BUNDLE_BUDGET_REPORT),
                ],
            ),
            (
                "Public beta artifacts",
                [
                    python,
                    "scripts/release/generate_public_beta_artifacts.py",
                    "--target",
                    "300",
                    "--computed-target",
                    "300",
                ],
            ),
            ("Security audit", [python, "scripts/security/run_audit.py"]),
        ]
    )

    if not args.skip_browser_smoke:
        steps.append(
            (
                "Browser smoke",
                [python, "scripts/run_browser_smoke.py", "--report-path", str(BROWSER_SMOKE_REPORT)],
            )
        )
        steps.append(
            (
                "Golden journeys",
                [python, "scripts/run_golden_journeys.py", "--report-path", str(GOLDEN_JOURNEYS_REPORT)],
            )
        )

    steps.append(
        (
            "Launch signoff",
            [
                python,
                "scripts/governance/verify_approval.py",
                str(LAUNCH_SIGNOFF_DOCUMENT),
                "--require-reviewer",
                "Engineering",
                "--require-reviewer",
                "QA",
                "--require-reviewer",
                "Design",
                "--require-reviewer",
                "Product",
            ],
        )
    )
    steps.append(("Clean source archive", archive_command))
    dossier_approved = (
        args.frontend_clean_install
        and args.require_signed_provenance
        and not args.allow_dirty_archive
        and not args.skip_browser_smoke
    )
    dossier_command = [
        python,
        "scripts/release/generate_release_candidate_dossier.py",
        "--prepared-from-clean-checkout",
        "no" if args.allow_dirty_archive else "yes",
        "--frontend-clean-install",
        "yes" if args.frontend_clean_install else "no",
        "--browser-smoke-status",
        "skipped" if args.skip_browser_smoke else "passed",
        "--browser-smoke-report",
        str(BROWSER_SMOKE_REPORT),
        "--golden-journeys-status",
        "skipped" if args.skip_browser_smoke else "passed",
        "--golden-journeys-report",
        str(GOLDEN_JOURNEYS_REPORT),
        "--bundle-budget-report",
        str(BUNDLE_BUDGET_REPORT),
        "--security-audit-report",
        str(SECURITY_AUDIT_REPORT),
        "--signoff-document",
        str(LAUNCH_SIGNOFF_DOCUMENT),
        "--approved",
        "yes" if dossier_approved else "no",
    ]
    steps.append(("Release candidate dossier", dossier_command))

    total = len(steps)
    for index, (label, command) in enumerate(steps, start=1):
        _run_step(index, total, label, command, env=shared_env)

    print("[RC] All release-candidate gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
