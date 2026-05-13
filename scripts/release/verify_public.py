#!/usr/bin/env python3
"""Run the public reproducibility gate for a fresh Project Parva checkout."""

from __future__ import annotations

import os
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


def _resolve_python311() -> list[str]:
    candidates: list[list[str]] = [[sys.executable]]

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
        "Unable to find Python 3.11. Install Python 3.11 or run with the py -3.11 launcher."
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

    checks: list[tuple[str, list[str]]] = [
        ("environment", [*python, "scripts/verify_environment.py"]),
        ("repository hygiene", [*python, "scripts/release/check_repo_hygiene.py"]),
        ("secret scan", [*python, "scripts/security/scan_repo_secrets.py"]),
        ("path leak scan", [*python, "scripts/check_path_leaks.py"]),
        ("documentation links", [*python, "scripts/check_docs_links.py"]),
        ("Render public blueprint", [*python, "scripts/release/check_render_blueprint.py"]),
        ("temporal trust verification", [*python, "scripts/parva_trust_verify.py"]),
        ("timegraph verification", [*python, "scripts/parva_timegraph_verify.py"]),
        ("rulelang verification", [*python, "scripts/parva_rulelang_verify.py"]),
        ("impact simulator verification", [*python, "scripts/parva_impact_verify.py"]),
        ("agentic temporal verification", [*python, "scripts/parva_agent_verify.py"]),
        ("agent benchmark", [*python, "scripts/parva_agent_benchmark.py"]),
        ("protocol verification", [*python, "scripts/parva_protocol_verify.py"]),
        ("protocol conformance", [*python, "scripts/parva_conformance.py", "--target", "local", "--level", "parva_core"]),
        ("documented route inventory", [*python, "scripts/release/check_documented_routes.py"]),
        ("backend smoke", [*python, "scripts/release/check_backend_smoke.py"]),
        ("Python SDK import smoke", [*python, "scripts/release/check_sdk_install.py"]),
        ("backend lint", [*python, "-m", "ruff", "check", "backend", "tests", "scripts", "sdk", "packages/parva-python"]),
        ("backend public tests", [*python, "-m", "pytest", "-q"]),
        ("Python package SDK tests", [*python, "-m", "pytest", "packages/parva-python/tests", "-q"]),
        ("frontend lint", build_npm_command(["--prefix", "frontend", "run", "lint"], node_runtime)),
        ("frontend tests", build_npm_command(["--prefix", "frontend", "test", "--", "--run"], node_runtime)),
        ("frontend build", build_npm_command(["--prefix", "frontend", "run", "build"], node_runtime)),
        ("JavaScript SDK tests", build_npm_command(["--prefix", "packages/parva-js", "test"], node_runtime)),
    ]

    for label, command in checks:
        if not _run(label, command, env):
            return 1

    print("\n[verify-public] Public reproducibility gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
