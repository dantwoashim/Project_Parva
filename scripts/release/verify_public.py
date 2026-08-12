#!/usr/bin/env python3
"""Run the public reproducibility gate for a fresh Project Parva checkout."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from node_runtime import build_npm_command, resolve_node_runtime  # noqa: E402


def _python_version(command: list[str]) -> tuple[int, int] | None:
    result = subprocess.run(
        [
            *command,
            "-c",
            "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        major, minor = result.stdout.strip().split(".", 1)
        return int(major), int(minor)
    except ValueError:
        return None


def _configured_python_candidates(configured: str | None = None, args: str | None = None) -> list[list[str]]:
    configured = os.getenv("PARVA_PYTHON", "").strip() if configured is None else configured.strip()
    args = os.getenv("PARVA_PYTHON_ARGS", "").strip() if args is None else args.strip()
    if not configured:
        return []

    extra_args = shlex.split(args, posix=os.name != "nt") if args else []
    candidates = [[configured, *extra_args]]
    split_configured = shlex.split(configured, posix=os.name != "nt")
    if len(split_configured) > 1:
        candidates.append([*split_configured, *extra_args])
    return candidates


def _resolve_python311() -> list[str]:
    candidates: list[list[str]] = _configured_python_candidates()
    candidates.append([sys.executable])

    py_launcher = shutil.which("py")
    if py_launcher:
        candidates.append([py_launcher, "-3.11"])

    for name in ("python3.11", "python3", "python"):
        executable = shutil.which(name)
        if executable:
            candidates.append([executable])

    for command in candidates:
        if _python_version(command) == (3, 11):
            return command

    raise SystemExit(
        "Unable to find Python 3.11. Set PARVA_PYTHON to a Python 3.11 executable "
        "or use PARVA_PYTHON=py with PARVA_PYTHON_ARGS=-3.11."
    )


def _public_env() -> dict[str, str]:
    env = os.environ.copy()
    path_parts = [str(PROJECT_ROOT), str(PROJECT_ROOT / "backend")]
    if env.get("PYTHONPATH"):
        path_parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(path_parts)
    env["PARVA_ENV"] = "test"
    env["PARVA_ENABLE_EXPERIMENTAL_API"] = "false"
    env["PARVA_SHOW_PRIVATE_SCHEMA"] = "false"
    env["PARVA_ENABLE_PRIVATE_SOURCE_TESTS"] = "0"
    env["PARVA_ENABLE_WIDE_CORPUS_TESTS"] = "0"
    env.setdefault("PARVA_RATE_LIMIT_BACKEND", "memory")
    env.setdefault("PARVA_REQUIRE_PRECOMPUTED", "false")
    return env


def _run(label: str, command: list[str], env: dict[str, str]) -> bool:
    print(f"\n[verify-public] {label}")
    print("[verify-public] " + " ".join(command))
    result = subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=False)
    if result.returncode == 0:
        print(f"[verify-public] PASS: {label}")
        return True
    print(f"[verify-public] FAIL: {label} exited {result.returncode}")
    return False


def main() -> int:
    python = _resolve_python311()
    node_runtime = resolve_node_runtime()
    env = _public_env()
    if node_runtime:
        env = node_runtime.build_env(env)

    checks: list[tuple[str, list[str]]] = [
        ("environment", [*python, "scripts/verify_environment.py"]),
        ("repository hygiene", [*python, "scripts/release/check_repo_hygiene.py"]),
        ("clean clone assumptions", [*python, "scripts/release/verify_clean_clone_assumptions.py"]),
        ("archive hygiene", [*python, "scripts/release/check_archive_hygiene.py"]),
        ("package readiness", [*python, "scripts/release/check_package_readiness.py"]),
        ("secret scan", [*python, "scripts/security/scan_repo_secrets.py"]),
        ("path leak scan", [*python, "scripts/check_path_leaks.py"]),
        ("public safety gate", [*python, "scripts/release/check_public_safety_gate.py"]),
        ("license compliance", [*python, "scripts/release/check_license_compliance.py"]),
        ("documentation links", [*python, "scripts/check_docs_links.py"]),
        ("canonical runtime registry", [*python, "scripts/check_canonical_runtime.py"]),
        ("backend import cycles", [*python, "scripts/release/check_import_cycles.py", "backend/app"]),
        ("maturity lanes", [*python, "scripts/check_maturity_lanes.py"]),
        ("Future BS v7 freeze", [*python, "scripts/future_bs/freeze_public_v7.py", "--check"]),
        ("Render public blueprint", [*python, "scripts/release/check_render_blueprint.py"]),
        ("Cloud Run blueprint", [*python, "scripts/release/check_cloudrun_blueprint.py"]),
        ("temporal trust verification", [*python, "scripts/parva_trust_verify.py"]),
        ("timegraph verification", [*python, "scripts/parva_timegraph_verify.py"]),
        ("rulelang verification", [*python, "scripts/parva_rulelang_verify.py"]),
        ("impact simulator verification", [*python, "scripts/parva_impact_verify.py"]),
        ("agentic temporal verification", [*python, "scripts/parva_agent_verify.py"]),
        ("agent benchmark", [*python, "scripts/parva_agent_benchmark.py"]),
        ("protocol verification", [*python, "scripts/parva_protocol_verify.py"]),
        ("external temporal rules", [*python, "scripts/validate_external_temporal_rules.py"]),
        ("benchmark schema", [*python, "public-benchmark/validate_benchmark.py"]),
        ("ceiling depth semantics", [*python, "scripts/release/check_ceiling_depth_semantics.py"]),
        ("ceiling depth audit", [*python, "scripts/release/audit_ceiling_depth.py"]),
        ("ceiling climax demos", [*python, "scripts/release/run_ceiling_climax_demos.py"]),
        ("public claims", [*python, "scripts/release/check_public_claims.py"]),
        ("public surface security", [*python, "scripts/release/check_public_surface_security.py"]),
        ("Python module size", [*python, "scripts/release/check_python_module_size.py"]),
        ("TypeScript module size", [*python, "scripts/release/check_ts_module_size.py"]),
        ("mypy scope ratchet", [*python, "scripts/release/check_mypy_scope.py"]),
        ("mypy", [*python, "-m", "mypy"]),
        (
            "Python dependency audit",
            [
                *python,
                "-m",
                "pip_audit",
                "--strict",
                "--requirement",
                "requirements/constraints.txt",
            ],
        ),
        ("CI Node 24 readiness", [*python, "scripts/release/check_ci_node24_readiness.py"]),
        ("Panchanga JPL lane report", [*python, "scripts/release/check_jpl_lane.py", "--check"]),
        ("route proof contract matrix", [*python, "scripts/release/generate_route_proof_matrix.py", "--check"]),
        ("external reviewer dry audit", [*python, "scripts/release/generate_external_review_dry_audit.py", "--check"]),
        ("source coverage report", [*python, "scripts/release/generate_source_coverage_report.py", "--check"]),
        ("release artifact manifest", [*python, "scripts/release/verify_release_artifact_manifest.py"]),
        ("protocol conformance core", [*python, "scripts/parva_conformance.py", "--target", "local", "--level", "parva_core"]),
        ("protocol conformance full", [*python, "scripts/parva_conformance.py", "--target", "local", "--level", "parva_full"]),
        ("documented route inventory", [*python, "scripts/release/check_documented_routes.py"]),
        ("v3 contract freeze", [*python, "scripts/release/check_contract_freeze.py"]),
        ("public OpenAPI drift", [*python, "scripts/release/check_public_openapi_drift.py"]),
        ("backend smoke", [*python, "scripts/release/check_backend_smoke.py"]),
        ("Python SDK import smoke", [*python, "scripts/release/check_sdk_install.py"]),
        ("offline SDK proof examples", [*python, "scripts/release/check_sdk_examples.py"]),
        ("local kernel package readiness", [*python, "scripts/release/check_local_kernel_package.py"]),
        (
            "Python lint",
            [
                *python,
                "-m",
                "ruff",
                "check",
                "backend",
                "tests",
                "scripts",
                "sdk",
                "packages",
                "tools",
                "tools_lib",
                "parva_mcp_server",
                "public-benchmark",
            ],
        ),
        (
            "backend public tests",
            [
                *python,
                "-m",
                "pytest",
                "-q",
                "-m",
                "not private_source and not wide_corpus and not research_artifact",
            ],
        ),
        ("Python package SDK tests", [*python, "-m", "pytest", "packages/parva-python/tests", "-q"]),
        ("frontend component size", [*python, "scripts/frontend/check_component_size.py"]),
        ("frontend lint", build_npm_command(["--prefix", "frontend", "run", "lint"], node_runtime)),
        ("frontend dependency audit", build_npm_command(["--prefix", "frontend", "audit", "--audit-level=moderate"], node_runtime)),
        ("frontend tests", build_npm_command(["--prefix", "frontend", "test", "--", "--run"], node_runtime)),
        ("frontend build", build_npm_command(["--prefix", "frontend", "run", "build"], node_runtime)),
        (
            "frontend bundle budget",
            [
                *python,
                "scripts/release/check_frontend_bundle_budget.py",
                "--report-path",
                "tmp/verify-public-frontend-bundle-budget.json",
            ],
        ),
        ("JavaScript SDK dependency audit", build_npm_command(["--prefix", "packages/parva-js", "audit", "--audit-level=moderate"], node_runtime)),
        ("JavaScript SDK tests", build_npm_command(["--prefix", "packages/parva-js", "test"], node_runtime)),
        ("local kernel dependency audit", build_npm_command(["--prefix", "packages/parva-local-kernel", "audit", "--audit-level=moderate"], node_runtime)),
        ("local kernel tests", build_npm_command(["--prefix", "packages/parva-local-kernel", "test"], node_runtime)),
    ]

    for label, command in checks:
        if not _run(label, command, env):
            return 1

    print("\n[verify-public] Public reproducibility gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
