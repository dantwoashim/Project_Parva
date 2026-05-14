#!/usr/bin/env python3
"""Generate the Phase 01 baseline truth-freeze reports.

The script is intentionally read-only with respect to product behavior. It runs
verification commands, inspects route/profile and repository surfaces, and
writes markdown/json reports under reports/phase_01_baseline.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import re
import shlex
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "reports" / "phase_01_baseline"

VERIFICATION_COMMANDS: list[dict[str, Any]] = [
    {"command": "python scripts/release/check_repo_hygiene.py", "timeout": 120},
    {"command": "python scripts/security/scan_repo_secrets.py", "timeout": 120},
    {"command": "python scripts/check_path_leaks.py", "timeout": 120},
    {"command": "python scripts/check_docs_links.py", "timeout": 180},
    {"command": "python tools/validate_schemas.py", "timeout": 180},
    {"command": "python scripts/release/check_route_inventory.py", "timeout": 180},
    {"command": "python scripts/release/check_documented_routes.py", "timeout": 180},
    {"command": "python scripts/release/check_backend_smoke.py", "timeout": 240},
    {"command": "python scripts/parva_trust_verify.py", "timeout": 240},
    {"command": "python scripts/parva_timegraph_verify.py", "timeout": 240},
    {"command": "python scripts/parva_rulelang_verify.py", "timeout": 240},
    {"command": "python scripts/parva_impact_verify.py", "timeout": 240},
    {"command": "python scripts/parva_agent_verify.py", "timeout": 240},
    {"command": "python scripts/parva_agent_benchmark.py", "timeout": 240},
    {"command": "python scripts/parva_protocol_verify.py", "timeout": 240},
    {"command": "python scripts/parva_conformance.py --target local --level parva_core", "timeout": 300},
    {"command": "python scripts/parva_offline_bundle.py --output dist/parva-offline-bundle", "timeout": 300},
    {"command": "python scripts/parva_offline_verify.py dist/parva-offline-bundle", "timeout": 300},
    {
        "command": "python -m ruff check backend tests scripts sdk packages/parva-python",
        "timeout": 300,
    },
    {
        "command": 'pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=10',
        "timeout": 1200,
    },
    {"command": "python -m pytest packages/parva-python/tests -q", "timeout": 300},
    {"command": "npm --prefix packages/parva-js test", "timeout": 300},
    {"command": "npm --prefix frontend run lint", "timeout": 300},
    {"command": "npm --prefix frontend run build", "timeout": 600},
    {"command": "npm --prefix frontend test -- --run", "timeout": 600},
]

FINGERPRINT_COMMANDS = [
    "git status --short",
    "python --version",
    'python -c "import sys; print(sys.executable); print(sys.version)"',
    "node --version",
    "npm --version",
    "find .github/workflows -maxdepth 1 -type f -print 2>/dev/null | sort",
]

SUBSYSTEMS: list[dict[str, Any]] = [
    {
        "subsystem": "Core Calendar",
        "current_maturity": "stable",
        "public_exposure": "true",
        "route_profiles": ["public_demo", "public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/calendar/routes.py; backend/app/calendar/bikram_sambat.py",
        "known_duplicate_paths": ["backend/app/calendar/calculator.py", "backend/app/calendar/calculator_v2.py"],
        "data_dependencies": ["backend/app/calendar/bs_calendar_data.py"],
        "verification_commands": ["python -m pytest tests/unit/calendar -q"],
        "primary_risks": ["future estimated fallback policy requires ongoing public boundary checks"],
        "phase_owner": "core-calendar-team",
    },
    {
        "subsystem": "Panchanga",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/calendar/panchanga.py",
        "known_duplicate_paths": ["backend/app/calendar/tithi.py", "backend/app/calendar/tithi/"],
        "data_dependencies": ["Swiss Ephemeris runtime", "optional JPL kernels"],
        "verification_commands": ["python -m pytest tests/unit/calendar/test_tithi.py -q"],
        "primary_risks": ["CPU-heavy calculations must be bounded or precomputed in later phases"],
        "phase_owner": "panchanga-team",
    },
    {
        "subsystem": "Tithi",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/calendar/tithi/",
        "known_duplicate_paths": ["backend/app/calendar/tithi.py"],
        "data_dependencies": ["astronomical calculations"],
        "verification_commands": ["python -m pytest tests/unit/calendar/test_tithi.py -q"],
        "primary_risks": ["parallel module/package naming causes canonical-runtime ambiguity"],
        "phase_owner": "panchanga-team",
    },
    {
        "subsystem": "Nakshatra/Yoga/Karana",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/calendar/panchanga.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["astronomical calculations"],
        "verification_commands": ["python scripts/release/check_backend_smoke.py"],
        "primary_risks": ["authority-sensitive interpretation needs clear claim boundary"],
        "phase_owner": "panchanga-team",
    },
    {
        "subsystem": "Festivals/Observances",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_demo", "public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/rules/service.py; backend/app/rules/catalog_v4.py",
        "known_duplicate_paths": ["backend/app/calendar/calculator.py", "backend/app/calendar/calculator_v2.py"],
        "data_dependencies": ["data/festivals/festival_rules_v4.json"],
        "verification_commands": ["python scripts/validate_festival_catalog.py"],
        "primary_risks": ["legacy naming and multiple calculators obscure source of truth"],
        "phase_owner": "festival-team",
    },
    {
        "subsystem": "Holidays",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/api/festival_routes.py; backend/app/calendar/routes.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["public source policy and release artifacts"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["official release ingestion workflow is not fully matured"],
        "phase_owner": "trust-team",
    },
    {
        "subsystem": "Fiscal/Working Day",
        "current_maturity": "stable",
        "public_exposure": "true",
        "route_profiles": ["public_demo", "public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/api/enterprise_routes.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["calendar conversion runtime", "holiday/working-day policy"],
        "verification_commands": ["python scripts/release/check_backend_smoke.py"],
        "primary_risks": ["institution-specific policies need explicit profile separation"],
        "phase_owner": "core-calendar-team",
    },
    {
        "subsystem": "RuleLang",
        "current_maturity": "developer_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_demo", "developer_preview", "enterprise_preview"],
        "canonical_candidate": "backend/app/services/rulelang_service.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["rules/public", "rules/private when explicitly enabled"],
        "verification_commands": ["python scripts/parva_rulelang_verify.py"],
        "primary_risks": ["trace privacy and human-review policy need deeper hardening"],
        "phase_owner": "rules-team",
    },
    {
        "subsystem": "Trust/Provenance",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_demo", "public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/services/trust_infrastructure_service.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["data/public/releases", "data/public/source_registry"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["deterministic regeneration from fresh clone remains a release gate"],
        "phase_owner": "trust-team",
    },
    {
        "subsystem": "Source Registry",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "data/public/source_registry",
        "known_duplicate_paths": ["data/source_inventory/"],
        "data_dependencies": ["public-safe source records"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["private source inventory must stay out of public artifacts"],
        "phase_owner": "trust-team",
    },
    {
        "subsystem": "Release Manifests",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "data/public/releases",
        "known_duplicate_paths": [],
        "data_dependencies": ["public artifacts and hashes"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["hash drift must fail CI"],
        "phase_owner": "release-engineering",
    },
    {
        "subsystem": "Evidence Packets",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/services/trust_infrastructure_service.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["public evidence packets"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["must not leak private source paths"],
        "phase_owner": "trust-team",
    },
    {
        "subsystem": "Transparency Logs",
        "current_maturity": "hash-only preview",
        "public_exposure": "partial",
        "route_profiles": ["developer_preview", "enterprise_preview"],
        "canonical_candidate": "data/transparency; trust service",
        "known_duplicate_paths": [],
        "data_dependencies": ["append-only log artifacts"],
        "verification_commands": ["python scripts/parva_trust_verify.py"],
        "primary_risks": ["unsigned preview must not look like third-party certification"],
        "phase_owner": "trust-team",
    },
    {
        "subsystem": "Offline Bundles",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "scripts/parva_offline_bundle.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["dist/parva-offline-bundle generated artifact"],
        "verification_commands": ["python scripts/parva_offline_verify.py dist/parva-offline-bundle"],
        "primary_risks": ["bundle integrity must not depend on local private data"],
        "phase_owner": "release-engineering",
    },
    {
        "subsystem": "TimeGraph",
        "current_maturity": "developer_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_demo", "developer_preview", "enterprise_preview"],
        "canonical_candidate": "backend/app/services/timegraph_service.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["public release artifacts"],
        "verification_commands": ["python scripts/parva_timegraph_verify.py"],
        "primary_risks": ["currently public-artifact/in-memory oriented"],
        "phase_owner": "intelligence-team",
    },
    {
        "subsystem": "Impact Simulator",
        "current_maturity": "developer_preview",
        "public_exposure": "partial",
        "route_profiles": ["developer_preview", "enterprise_preview"],
        "canonical_candidate": "backend/app/services/impact_service.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["TimeGraph", "RuleLang", "trust artifacts"],
        "verification_commands": ["python scripts/parva_impact_verify.py"],
        "primary_risks": ["sample dependency extraction is not production-grade"],
        "phase_owner": "intelligence-team",
    },
    {
        "subsystem": "Agent Tools",
        "current_maturity": "developer_preview",
        "public_exposure": "partial",
        "route_profiles": ["developer_preview", "enterprise_preview"],
        "canonical_candidate": "backend/app/api/agent_routes.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["public-safe temporal tools"],
        "verification_commands": ["python scripts/parva_agent_verify.py"],
        "primary_risks": ["unsupported operational claims must require human review"],
        "phase_owner": "intelligence-team",
    },
    {
        "subsystem": "Parva Protocol",
        "current_maturity": "protocol_draft",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "schemas/parva-protocol; specs/parva-protocol",
        "known_duplicate_paths": [],
        "data_dependencies": ["schema examples and conformance fixtures"],
        "verification_commands": ["python scripts/parva_protocol_verify.py"],
        "primary_risks": ["must not be described as a standard before external implementation"],
        "phase_owner": "protocol-team",
    },
    {
        "subsystem": "Conformance",
        "current_maturity": "protocol_draft",
        "public_exposure": "true",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "scripts/parva_conformance.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["conformance fixtures"],
        "verification_commands": ["python scripts/parva_conformance.py --target local --level parva_core"],
        "primary_risks": ["suite must reject invalid fixtures meaningfully"],
        "phase_owner": "protocol-team",
    },
    {
        "subsystem": "Credentials",
        "current_maturity": "protocol_draft",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "schemas/parva-protocol/calendar-credential.schema.json",
        "known_duplicate_paths": [],
        "data_dependencies": ["unsigned preview credentials unless otherwise configured"],
        "verification_commands": ["python tools/validate_schemas.py"],
        "primary_risks": ["must not imply third-party or government certification"],
        "phase_owner": "protocol-team",
    },
    {
        "subsystem": "Future-BS Research",
        "current_maturity": "research_private",
        "public_exposure": "metadata_only",
        "route_profiles": ["public_reference capabilities", "private experimental routes"],
        "canonical_candidate": "backend/app/future_bs; backend/app/api/future_bs_routes.py",
        "known_duplicate_paths": ["tests/fixtures/bs_future_projection.json"],
        "data_dependencies": ["private/generated future-BS research artifacts when explicitly enabled"],
        "verification_commands": ["python -m pytest tests/accuracy -q"],
        "primary_risks": ["exact future predictions must remain gated and labeled computed_prediction_not_official"],
        "phase_owner": "research-team",
    },
    {
        "subsystem": "Kundali",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["developer_preview", "enterprise_preview"],
        "canonical_candidate": "backend/app/api/kundali_routes.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["astronomical calculations"],
        "verification_commands": ["python scripts/release/check_backend_smoke.py"],
        "primary_risks": ["authority-sensitive and CPU-heavy outputs need gating"],
        "phase_owner": "panchanga-team",
    },
    {
        "subsystem": "Muhurta",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_reference", "developer_preview"],
        "canonical_candidate": "backend/app/api/muhurta_routes.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["panchanga calculations"],
        "verification_commands": ["python scripts/release/check_backend_smoke.py"],
        "primary_risks": ["must preserve review gates for sensitive decisions"],
        "phase_owner": "panchanga-team",
    },
    {
        "subsystem": "Frontend",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_demo"],
        "canonical_candidate": "frontend/src/redesign/ParvaRedesign.jsx",
        "known_duplicate_paths": [],
        "data_dependencies": ["VITE_API_BASE"],
        "verification_commands": ["npm --prefix frontend run lint", "npm --prefix frontend run build"],
        "primary_risks": ["large component surface and route capability complexity"],
        "phase_owner": "frontend-team",
    },
    {
        "subsystem": "Embeds",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["public_demo"],
        "canonical_candidate": "frontend and docs embeds",
        "known_duplicate_paths": [],
        "data_dependencies": ["public API base"],
        "verification_commands": ["npm --prefix frontend run build"],
        "primary_risks": ["must not hardcode private routes or exact future values"],
        "phase_owner": "frontend-team",
    },
    {
        "subsystem": "Python SDK",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference"],
        "canonical_candidate": "packages/parva-python",
        "known_duplicate_paths": ["sdk/python"],
        "data_dependencies": ["public API"],
        "verification_commands": ["python -m pytest packages/parva-python/tests -q"],
        "primary_risks": ["legacy SDK path may confuse canonical client story"],
        "phase_owner": "dx-team",
    },
    {
        "subsystem": "JS/TS SDK",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["public_reference"],
        "canonical_candidate": "packages/parva-js",
        "known_duplicate_paths": [],
        "data_dependencies": ["public API"],
        "verification_commands": ["npm --prefix packages/parva-js test"],
        "primary_risks": ["OpenAPI drift and retry behavior need continuous tests"],
        "phase_owner": "dx-team",
    },
    {
        "subsystem": "CLI/scripts",
        "current_maturity": "public_preview",
        "public_exposure": "partial",
        "route_profiles": ["local"],
        "canonical_candidate": "scripts/",
        "known_duplicate_paths": [],
        "data_dependencies": ["public artifacts", "optional private data"],
        "verification_commands": ["python scripts/release/verify_public.py"],
        "primary_risks": ["scripts must clearly separate public, private, and research lanes"],
        "phase_owner": "release-engineering",
    },
    {
        "subsystem": "Billing/API keys",
        "current_maturity": "enterprise_preview",
        "public_exposure": "partial",
        "route_profiles": ["enterprise_preview"],
        "canonical_candidate": "backend/app/billing",
        "known_duplicate_paths": [],
        "data_dependencies": ["Postgres/SQLite store depending on environment"],
        "verification_commands": ["python -m pytest tests/unit/billing -q"],
        "primary_risks": ["manual activation/idempotency and store production posture need audit"],
        "phase_owner": "commercial-platform-team",
    },
    {
        "subsystem": "CI/SRE",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["ci"],
        "canonical_candidate": ".github/workflows; scripts/release/verify_public.py",
        "known_duplicate_paths": [],
        "data_dependencies": ["public fixtures and package locks"],
        "verification_commands": ["python scripts/release/verify_public.py"],
        "primary_risks": ["verification breadth and performance budgets still need maturity lanes"],
        "phase_owner": "sre-team",
    },
    {
        "subsystem": "Docs",
        "current_maturity": "public_preview",
        "public_exposure": "true",
        "route_profiles": ["docs"],
        "canonical_candidate": "docs/README.md",
        "known_duplicate_paths": ["docs/internal_audit", "docs/archive"],
        "data_dependencies": [],
        "verification_commands": ["python scripts/check_docs_links.py"],
        "primary_risks": ["historical docs can conflict with current maturity labels"],
        "phase_owner": "dx-team",
    },
]


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def run_command(command: str, *, timeout: int = 120, requested_command: str | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        duration = round(time.perf_counter() - started, 3)
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        status = "pass" if completed.returncode == 0 else "fail"
        return {
            "command": command,
            "requested_command": requested_command or command,
            "status": status,
            "exit_code": completed.returncode,
            "duration_seconds": duration,
            "summary": summarize_output(stdout, stderr),
            "stdout_tail": tail_text(stdout),
            "stderr_tail": tail_text(stderr),
            "blocking_reason": None,
            "failure_category": categorize_result(command, status, stdout, stderr),
        }
    except subprocess.TimeoutExpired as exc:
        duration = round(time.perf_counter() - started, 3)
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": command,
            "requested_command": requested_command or command,
            "status": "blocked",
            "exit_code": None,
            "duration_seconds": duration,
            "summary": f"Timed out after {timeout}s.",
            "stdout_tail": tail_text(stdout),
            "stderr_tail": tail_text(stderr),
            "blocking_reason": f"timeout after {timeout}s",
            "failure_category": "environment issue",
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "requested_command": requested_command or command,
            "status": "blocked",
            "exit_code": None,
            "duration_seconds": 0,
            "summary": str(exc),
            "stdout_tail": "",
            "stderr_tail": str(exc),
            "blocking_reason": str(exc),
            "failure_category": "environment issue",
        }


def summarize_output(stdout: str, stderr: str) -> str:
    combined = "\n".join(part.strip() for part in (stdout, stderr) if part.strip())
    if not combined:
        return "No output."
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    return lines[-1][:500] if lines else "No output."


def tail_text(text: str, *, max_lines: int = 30, max_chars: int = 4000) -> str:
    if not text:
        return ""
    lines = text.splitlines()[-max_lines:]
    tail = "\n".join(lines)
    if len(tail) > max_chars:
        return tail[-max_chars:]
    return tail


def categorize_result(command: str, status: str, stdout: str, stderr: str) -> str | None:
    if status == "pass":
        return None
    text = f"{stdout}\n{stderr}".lower()
    if "not recognized" in text or "no such file" in text or "could not find" in text:
        return "environment issue"
    if "private" in text or "source_archive" in text or "wide_corpus" in text:
        return "private-data issue"
    if "experimental" in text or "gated" in text or "disabled" in text:
        return "expected gated issue"
    return "repo issue"


def command_with_python(command: str, python_command: str) -> str:
    """Rewrite Python command prefixes for the supported interpreter override."""
    if python_command == "python":
        return command
    if command.startswith("python "):
        return f"{python_command} {command.removeprefix('python ')}"
    if command.startswith("pytest "):
        return f"{python_command} -m {command}"
    return command


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_files() -> list[str]:
    result = run_command("git ls-files", timeout=60)
    if result["status"] != "pass":
        return []
    return [line.strip() for line in result["stdout_tail"].splitlines() if line.strip()]


def all_git_files() -> list[str]:
    completed = subprocess.run(
        "git ls-files",
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def grep(pattern: str, paths: list[str] | None = None, *, limit: int = 80) -> list[str]:
    quoted_paths = ""
    if paths:
        quoted_paths = " " + " ".join(shlex.quote(path) for path in paths)
    command = f"git grep -n -I -E {shlex.quote(pattern)} --{quoted_paths}"
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        return [f"grep failed: {completed.stderr.strip()}"]
    return completed.stdout.splitlines()[:limit]


def load_packages() -> dict[str, Any]:
    packages: dict[str, Any] = {}
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.exists():
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data.get("project", {})
        packages["backend"] = {
            "name": project.get("name"),
            "version": project.get("version"),
            "requires_python": project.get("requires-python"),
            "dependencies": project.get("dependencies", []),
            "optional_dependencies": project.get("optional-dependencies", {}),
        }
    for label, rel in {
        "frontend": "frontend/package.json",
        "parva-js": "packages/parva-js/package.json",
    }.items():
        path = REPO_ROOT / rel
        if path.exists():
            payload = read_json(path)
            packages[label] = {
                "name": payload.get("name"),
                "version": payload.get("version"),
                "scripts": payload.get("scripts", {}),
                "dependencies": payload.get("dependencies", {}),
                "devDependencies": payload.get("devDependencies", {}),
            }
    py_sdk = REPO_ROOT / "packages/parva-python/pyproject.toml"
    if py_sdk.exists():
        data = tomllib.loads(py_sdk.read_text(encoding="utf-8"))
        project = data.get("project", {})
        packages["parva-python"] = {
            "name": project.get("name"),
            "version": project.get("version"),
            "dependencies": project.get("dependencies", []),
        }
    return packages


def lockfiles_present(files: list[str]) -> list[str]:
    names = {
        "package-lock.json",
        "npm-shrinkwrap.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "requirements.txt",
        "constraints.txt",
        "poetry.lock",
        "uv.lock",
    }
    return [path for path in files if Path(path).name in names or path.endswith("requirements/constraints.txt")]


def route_inventory() -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT / "backend"))
    try:
        from app.bootstrap import router_registry as rr  # type: ignore

        profiles = {
            "minimal_public": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="minimal_public", enable_experimental_api=False
            ),
            "public_demo": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="public_demo", enable_experimental_api=False
            ),
            "public_reference": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="public_reference", enable_experimental_api=False
            ),
            "developer_preview": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="developer_preview", enable_experimental_api=False
            ),
            "enterprise_preview": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="enterprise_preview", enable_experimental_api=False
            ),
            "full": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="full", enable_experimental_api=False
            ),
            "full_experimental": rr._registrations_for_profile(  # noqa: SLF001
                route_profile="full", enable_experimental_api=True
            ),
        }
        profile_payload: dict[str, Any] = {}
        for profile_name, registrations in profiles.items():
            entries = []
            for registration in registrations:
                prefix = registration.policy_path or registration.router.prefix or ""
                private = bool(registration.register_when_experimental_enabled)
                exact_future = "future_bs_private" in registration.policy_name or (
                    registration.policy_name == "future_bs" and "capabilities" not in prefix
                )
                entries.append(
                    {
                        "policy_name": registration.policy_name,
                        "audience": registration.audience,
                        "access_policy": registration.access_policy,
                        "prefix_or_policy_path": prefix,
                        "include_v3": registration.include_v3,
                        "include_base": registration.include_base,
                        "include_experimental_versions": registration.include_experimental_versions,
                        "private_or_experimental": private,
                        "public_safe_draft": not private,
                        "future_bs_exact_output_risk": exact_future,
                        "mutates_sensitive_state_risk": registration.policy_name
                        in {"billing", "provenance"},
                        "cpu_heavy_risk": registration.policy_name
                        in {"panchanga", "kundali", "muhurta", "muhurta_heatmap", "impact"},
                        "public_openapi_expected": not private,
                    }
                )
            profile_payload[profile_name] = entries
        return {
            "status": "pass",
            "profiles": profile_payload,
            "policy_specs": rr.iter_route_policy_specs(),
        }
    except Exception as exc:  # noqa: BLE001 - baseline must record import failure instead of aborting
        return {"status": "fail", "error": repr(exc), "profiles": {}, "policy_specs": []}


def discover_duplicate_truth_paths(files: list[str]) -> list[dict[str, Any]]:
    interesting = [
        "calculator",
        "tithi",
        "festival",
        "rule",
        "source",
        "confidence",
        "program_synthesis",
        "latent_truth",
    ]
    candidates = [
        path
        for path in files
        if path.startswith(("backend/", "data/", "docs/", "tests/", "scripts/", "packages/", "sdk/"))
        and any(token in path.lower() for token in interesting)
    ]
    rows = []
    for path in candidates[:400]:
        basename = Path(path).name
        refs = grep(re.escape(basename), limit=8)
        lower = path.lower()
        classification = "candidate"
        if "future_bs" in lower or "research" in lower or "program_synthesis" in lower:
            classification = "research"
        if "legacy" in lower or "deprecated" in lower or "compat" in lower:
            classification = "compatibility"
        if "calculator_v2" in lower or "catalog_v4" in lower or "rulelang_service" in lower:
            classification = "canonical_candidate"
        rows.append(
            {
                "path": path,
                "classification": classification,
                "reference_count_sample": len(refs),
                "reference_sample": refs[:5],
                "phase_to_resolve": "Phase 03 Canonical Runtime Consolidation",
            }
        )
    return rows


def test_lane_inventory(files: list[str]) -> list[dict[str, Any]]:
    test_files = [path for path in files if path.startswith(("tests/", "backend/tests/")) and path.endswith(".py")]
    rows = []
    for path in test_files:
        text = (REPO_ROOT / path).read_text(encoding="utf-8", errors="ignore")
        markers = re.findall(r"pytest\.mark\.([a-zA-Z0-9_]+)", text)
        lane = "public_ci"
        marker_needed = ""
        public_safe = True
        dependency = "public fixtures"
        if "private_source" in path or "source_archive" in text or "PARVA_ENABLE_PRIVATE_SOURCE_TESTS" in text:
            lane = "private_source_ci"
            marker_needed = "private_source"
            public_safe = False
            dependency = "private source archive"
        elif "wide_corpus" in text or "PARVA_ENABLE_WIDE_CORPUS_TESTS" in text:
            lane = "research_artifact_ci"
            marker_needed = "wide_corpus"
            public_safe = False
            dependency = "wide corpus"
        elif "research_artifact" in text or "future_bs" in path:
            lane = "research_artifact_ci"
            marker_needed = "research_artifact"
            public_safe = "computed_prediction_not_official" in text
            dependency = "generated research artifacts or public-safe future-BS metadata"
        elif "performance" in path:
            lane = "performance_ci"
            dependency = "performance environment"
        elif "protocol" in path or "conformance" in path:
            lane = "protocol_ci"
        elif "security" in path or "secret" in text:
            lane = "security_ci"
        rows.append(
            {
                "test_path": path,
                "public_safe": public_safe,
                "marker_needed": marker_needed or "none",
                "current_marker": ", ".join(sorted(set(markers))) or "none",
                "data_dependency": dependency,
                "recommended_lane": lane,
            }
        )
    return rows


def dead_code_candidates(files: list[str]) -> list[dict[str, Any]]:
    candidates = []
    patterns = ("legacy", "deprecated", "old", "archive", "historical", "unused", "compat")
    for path in files:
        lower = path.lower()
        if any(token in lower for token in patterns):
            refs = grep(re.escape(Path(path).name), limit=10)
            evidence = []
            if len(refs) <= 1:
                evidence.append("no or only self filename references found in grep sample")
            if "archive" in lower or "historical" in lower:
                evidence.append("path indicates archive/historical material")
            if "legacy" in lower or "compat" in lower:
                evidence.append("path indicates compatibility or legacy surface")
            if evidence:
                candidates.append(
                    {
                        "path": path,
                        "evidence": "; ".join(evidence),
                        "risk_of_deletion": "medium" if path.startswith(("backend/", "tests/")) else "low",
                        "recommended_action": "review in Phase 03/04 before deletion",
                        "phase": "Phase 03 or Phase 04",
                    }
                )
    return candidates[:120]


def boundary_inventory(files: list[str]) -> dict[str, Any]:
    categories = {
        "future_bs_exact_predictions": r"future[-_ ]?BS|month-length|2084|2099|2200|computed_prediction_not_official",
        "private_source_archive_paths": r"source_archive|source_inventory|private_source|wide_corpus",
        "generated_research_artifacts": r"model_runs|accuracy_lab|residual|calibration|research_artifact",
        "model_accuracy_claims": r"99%|99 percent|100%|green-zone|accuracy",
        "credentials_or_signatures": r"credential|signature|signing|api_key|PARVA_API_KEYS|pepper",
        "official_source_claims": r"official|government|authority|MoHA|NPNS|Panchanga",
        "authority_sensitive_surfaces": r"kundali|muhurta|panchanga|banking|payroll|legal|tax",
    }
    return {
        name: grep(pattern, limit=60)
        for name, pattern in categories.items()
    }


def generated_artifact_gaps(files: list[str]) -> list[dict[str, Any]]:
    watched_prefixes = (
        "dist/",
        "output/",
        "reports/",
        "data/future_bs/",
        "data/source_archive/",
        "data/source_inventory/",
        "backend/data/traces/",
        "backend/data/snapshots/",
    )
    rows = []
    for path in files:
        if path.startswith(watched_prefixes):
            rows.append(
                {
                    "path": path,
                    "policy_gap": "tracked generated/private-sensitive prefix requires review",
                    "recommended_action": "confirm public-safe status or move to generated artifact storage",
                    "phase": "Phase 04/06/07",
                }
            )
    return rows


def data_inventory(files: list[str]) -> dict[str, Any]:
    groups: dict[str, list[str]] = {}
    for path in files:
        if path.startswith("data/"):
            parts = path.split("/")
            key = "/".join(parts[:2]) if len(parts) >= 2 else "data"
            groups.setdefault(key, []).append(path)
    return {key: value[:80] for key, value in sorted(groups.items())}


def frontend_inventory(files: list[str]) -> list[dict[str, Any]]:
    rows = []
    for path in files:
        if path.startswith("frontend/src/") and path.endswith((".js", ".jsx", ".ts", ".tsx", ".css")):
            full = REPO_ROOT / path
            try:
                line_count = len(full.read_text(encoding="utf-8", errors="ignore").splitlines())
            except OSError:
                line_count = 0
            rows.append(
                {
                    "path": path,
                    "lines": line_count,
                    "risk": "large component" if line_count > 700 else "normal",
                    "phase": "Phase 09" if line_count > 700 else "n/a",
                }
            )
    return sorted(rows, key=lambda row: row["lines"], reverse=True)


def sdk_inventory(files: list[str], packages: dict[str, Any]) -> dict[str, Any]:
    return {
        "packages": {key: packages[key] for key in packages if key in {"parva-python", "parva-js"}},
        "legacy_sdk_files": [path for path in files if path.startswith("sdk/")][:120],
        "package_sdk_files": [path for path in files if path.startswith("packages/parva-")][:160],
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        escaped = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in row]
        out.append("| " + " | ".join(escaped) + " |")
    return "\n".join(out)


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    if not text or any(ch in text for ch in ":#[]{}\n"):
        return json.dumps(text)
    return text


def subsystem_yaml(subsystems: list[dict[str, Any]]) -> str:
    lines = ["generated_at: " + now_iso(), "subsystems:"]
    for item in subsystems:
        lines.append("  - subsystem: " + yaml_scalar(item["subsystem"]))
        for key in (
            "current_maturity",
            "public_exposure",
            "canonical_candidate",
            "phase_owner",
        ):
            lines.append(f"    {key}: {yaml_scalar(item.get(key))}")
        for key in ("route_profiles", "known_duplicate_paths", "data_dependencies", "verification_commands", "primary_risks"):
            lines.append(f"    {key}:")
            values = item.get(key, [])
            if not values:
                lines.append("      []")
            else:
                for value in values:
                    lines.append("      - " + yaml_scalar(value))
    return "\n".join(lines)


def render_verification_markdown(payload: dict[str, Any]) -> str:
    rows = [
        [
            command["command"],
            command.get("requested_command", command["command"]),
            command["status"],
            command.get("exit_code"),
            command.get("failure_category") or "",
            command.get("duration_seconds"),
            command.get("summary", ""),
        ]
        for command in payload["commands"]
    ]
    detail_sections = []
    for command in payload["commands"]:
        detail_sections.append(
            "\n".join(
                [
                    f"### `{command['command']}`",
                    "",
                    f"- requested_command: `{command.get('requested_command', command['command'])}`",
                    f"- status: `{command['status']}`",
                    f"- exit_code: `{command.get('exit_code')}`",
                    f"- duration_seconds: `{command.get('duration_seconds')}`",
                    f"- failure_category: `{command.get('failure_category') or ''}`",
                    f"- blocking_reason: `{command.get('blocking_reason') or ''}`",
                    "",
                    "stdout tail:",
                    "",
                    "```text",
                    command.get("stdout_tail") or "",
                    "```",
                    "",
                    "stderr tail:",
                    "",
                    "```text",
                    command.get("stderr_tail") or "",
                    "```",
                ]
            )
        )
    return "\n\n".join(
        [
            "# Phase 01 Verification Matrix",
            "",
            f"Generated at: `{payload['generated_at']}`",
            "",
            markdown_table(
                [
                    "Command run",
                    "Requested command",
                    "Status",
                    "Exit code",
                    "Category",
                    "Seconds",
                    "Summary",
                ],
                rows,
            ),
            "",
            "## Command Output Tails",
            "",
            "\n\n".join(detail_sections),
        ]
    )


def render_subsystems_markdown(subsystems: list[dict[str, Any]]) -> str:
    rows = [
        [
            item["subsystem"],
            item["current_maturity"],
            item["public_exposure"],
            ", ".join(item["route_profiles"]),
            item["canonical_candidate"],
            ", ".join(item["primary_risks"]),
        ]
        for item in subsystems
    ]
    return "\n\n".join(
        [
            "# Phase 01 Subsystem Inventory",
            "",
            markdown_table(
                [
                    "Subsystem",
                    "Current maturity",
                    "Public exposure",
                    "Route profiles",
                    "Canonical candidate",
                    "Primary risks",
                ],
                rows,
            ),
        ]
    )


def render_route_inventory_markdown(payload: dict[str, Any]) -> str:
    sections = ["# Phase 01 Route Profile Inventory", "", f"Import status: `{payload['status']}`"]
    if payload.get("error"):
        sections.extend(["", f"Import error: `{payload['error']}`"])
    for profile, registrations in payload.get("profiles", {}).items():
        rows = [
            [
                item["policy_name"],
                item["audience"],
                item["access_policy"],
                item["prefix_or_policy_path"],
                item["private_or_experimental"],
                item["future_bs_exact_output_risk"],
                item["mutates_sensitive_state_risk"],
                item["cpu_heavy_risk"],
            ]
            for item in registrations
        ]
        sections.extend(
            [
                "",
                f"## `{profile}`",
                "",
                markdown_table(
                    [
                        "Policy",
                        "Audience",
                        "Access",
                        "Path",
                        "Private/experimental",
                        "Future exact risk",
                        "Sensitive mutation",
                        "CPU-heavy risk",
                    ],
                    rows,
                ),
            ]
        )
    return "\n".join(sections)


def render_duplicate_markdown(rows: list[dict[str, Any]]) -> str:
    table_rows = [
        [
            row["path"],
            row["classification"],
            row["reference_count_sample"],
            row["phase_to_resolve"],
            "<br>".join(row["reference_sample"][:3]),
        ]
        for row in rows
    ]
    return "\n\n".join(
        [
            "# Phase 01 Duplicate Truth Path Discovery",
            "",
            "This is a conservative discovery list, not a deletion list.",
            "",
            markdown_table(
                ["Path", "Classification", "Reference sample count", "Phase", "Evidence sample"],
                table_rows,
            ),
        ]
    )


def render_boundary_markdown(payload: dict[str, Any]) -> str:
    sections = [
        "# Phase 01 Public, Private, and Research Boundary Inventory",
        "",
        "This report records references that require boundary review. A match is not automatically a leak.",
    ]
    for category, matches in payload.items():
        sections.extend(["", f"## {category}", ""])
        if not matches:
            sections.append("No matches found.")
        else:
            sections.extend(f"- `{match}`" for match in matches)
    return "\n".join(sections)


def render_test_lane_markdown(rows: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        [
            "# Phase 01 Test Lane Inventory",
            "",
            markdown_table(
                [
                    "Test path",
                    "Public-safe?",
                    "Marker needed",
                    "Current marker",
                    "Data dependency",
                    "Recommended lane",
                ],
                [
                    [
                        row["test_path"],
                        row["public_safe"],
                        row["marker_needed"],
                        row["current_marker"],
                        row["data_dependency"],
                        row["recommended_lane"],
                    ]
                    for row in rows
                ],
            ),
        ]
    )


def render_dead_code_markdown(rows: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        [
            "# Phase 01 Dead-Code Candidate Inventory",
            "",
            "No files are deleted in Phase 01. These are review targets only.",
            "",
            markdown_table(
                ["Path", "Evidence", "Risk of deletion", "Recommended action", "Phase"],
                [
                    [
                        row["path"],
                        row["evidence"],
                        row["risk_of_deletion"],
                        row["recommended_action"],
                        row["phase"],
                    ]
                    for row in rows
                ],
            ),
        ]
    )


def render_generated_artifacts_markdown(rows: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        [
            "# Phase 01 Generated Artifact and Policy Gap Inventory",
            "",
            markdown_table(
                ["Path", "Policy gap", "Recommended action", "Phase"],
                [[row["path"], row["policy_gap"], row["recommended_action"], row["phase"]] for row in rows]
                or [["None found in tracked files", "", "", ""]],
            ),
        ]
    )


def render_security_markdown(route_payload: dict[str, Any]) -> str:
    sensitive = []
    for profile, registrations in route_payload.get("profiles", {}).items():
        for item in registrations:
            if item["mutates_sensitive_state_risk"] or item["access_policy"] not in {"public", "trust_read"}:
                sensitive.append(
                    [
                        profile,
                        item["policy_name"],
                        item["access_policy"],
                        item["prefix_or_policy_path"],
                        item["mutates_sensitive_state_risk"],
                    ]
                )
    return "\n\n".join(
        [
            "# Phase 01 Security Surface Inventory",
            "",
            "Sensitive surfaces require deeper Phase 05 review. This inventory does not certify them.",
            "",
            markdown_table(
                ["Profile", "Policy", "Access policy", "Path", "Mutation risk"],
                sensitive,
            ),
            "",
            "## Static security references",
            "",
            "\n".join(f"- `{line}`" for line in grep(r"PBKDF2|api_key|CORS|CSP|trusted_proxy|csrf|audit", limit=80)),
        ]
    )


def render_data_inventory_markdown(payload: dict[str, Any]) -> str:
    sections = ["# Phase 01 Data and Source Artifact Inventory"]
    for group, paths in payload.items():
        sections.extend(["", f"## `{group}`", ""])
        sections.extend(f"- `{path}`" for path in paths[:80])
    return "\n".join(sections)


def render_frontend_inventory_markdown(rows: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        [
            "# Phase 01 Frontend Surface Inventory",
            "",
            markdown_table(
                ["Path", "Lines", "Risk", "Phase"],
                [[row["path"], row["lines"], row["risk"], row["phase"]] for row in rows[:120]],
            ),
        ]
    )


def render_sdk_inventory_markdown(payload: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            "# Phase 01 SDK Inventory",
            "",
            "## Package metadata",
            "",
            "```json",
            json.dumps(payload["packages"], indent=2, sort_keys=True),
            "```",
            "",
            "## Legacy SDK files",
            "",
            "\n".join(f"- `{path}`" for path in payload["legacy_sdk_files"]) or "None.",
            "",
            "## Package SDK files",
            "",
            "\n".join(f"- `{path}`" for path in payload["package_sdk_files"]) or "None.",
        ]
    )


def render_scorecard() -> str:
    rows = [
        ["Engineering", "6.5", "Duplicate truth paths and resolver migration remain", "Phase 03", "canonical runtime checks"],
        ["Trust", "6.5", "Trust artifacts exist, deterministic rebuild still needs stronger proof", "Phase 06", "trust verify and bundle hash replay"],
        ["Security", "6.5", "Good startup and key hashing posture, deeper privacy/trace audit needed", "Phase 05", "security tests and secret scans"],
        ["Performance", "5.5", "Heavy calendrical routes need explicit budgets/offload", "Phase 08", "route p95/p99 measurements"],
        ["Product clarity", "6.5", "Public positioning improved, maturity lanes need enforcement", "Phase 04", "route/docs maturity inventory"],
        ["Protocol", "5.5", "Draft exists but not external-implementer-grade", "Phase 10", "full conformance and invalid fixtures"],
        ["Research governance", "6.0", "Future-BS public/private separation improved, exact future policy still needs audits", "Phase 07", "leakage tests"],
        ["Frontend", "5.5", "Public UI exists but large component and route complexity remain", "Phase 09", "frontend smoke and component split"],
        ["SDK/DX", "6.0", "SDKs exist, canonical story and drift tests need tightening", "Phase 09", "SDK tests and OpenAPI drift"],
        ["Operations", "6.5", "verify-public and workflows exist, SLO/deploy smoke lanes need expansion", "Phase 08", "CI and performance smoke"],
        ["Documentation", "6.5", "Public docs are strong but historical/internal docs need maturity labels", "Phase 04", "docs link/status checks"],
        ["Maintainability", "5.5", "Broad exceptions, duplicate runtimes, and mixed maturity increase load", "Phase 03/05", "ruff/mypy/import graph"],
    ]
    return "\n\n".join(
        [
            "# Phase 01 Initial 9+ Scorecard",
            "",
            markdown_table(
                ["Dimension", "Current score", "Blocker below 9", "Phase expected to fix", "Evidence required"],
                rows,
            ),
        ]
    )


def render_risk_register() -> str:
    rows = [
        ["Public future exact leakage", "critical", "Phase 07", "Route/OpenAPI tests and public grep"],
        ["Duplicate calendar/festival truth paths", "high", "Phase 03", "Canonical runtime and import graph"],
        ["Private source dependency in public verification", "high", "Phase 06", "Public verify from fresh clone"],
        ["CPU-heavy route blocking", "high", "Phase 08", "Latency budgets and worker/precompute plan"],
        ["Protocol overclaim", "medium", "Phase 10", "Draft labels and external implementer gate"],
        ["PII in traces/reason logs", "high", "Phase 05", "Privacy fixtures and trace scrubber"],
        ["Frontend maturity confusion", "medium", "Phase 09", "Route split and capability-aware UI"],
        ["SQLite/local store in production", "high", "Phase 05", "Startup hard-fail tests"],
        ["Generated artifact drift", "medium", "Phase 06", "Deterministic rebuild checks"],
        ["Legacy SDK confusion", "medium", "Phase 09", "Canonical SDK policy"],
    ]
    return "\n\n".join(
        [
            "# Phase 01 Initial Risk Register",
            "",
            markdown_table(["Risk", "Severity", "Next phase owner", "Verification"], rows),
        ]
    )


def render_next_phase_targets(verification: dict[str, Any]) -> str:
    failed = [
        command
        for command in verification["commands"]
        if command["status"] in {"fail", "blocked"}
    ]
    rows = [
        [
            command["command"],
            command.get("requested_command", command["command"]),
            command["status"],
            command.get("failure_category") or "",
            command.get("summary") or "",
        ]
        for command in failed
    ]
    static_targets = [
        ["Public verification gate", "Phase 02", "Make `scripts/release/verify_public.py` green from a clean public clone."],
        ["Route profile contract", "Phase 02", "Convert route inventory into failing tests/snapshots."],
        ["Docs links", "Phase 02", "Fix any link check failures found in this baseline."],
        ["Private/research markers", "Phase 02", "Ensure private, wide, and research tests are excluded from public CI."],
        ["OpenAPI drift", "Phase 02", "Pin public OpenAPI output for safe profiles."],
    ]
    return "\n\n".join(
        [
            "# Phase 01 Handoff: Phase 02 Red-Check Targets",
            "",
            "## Failed or blocked baseline commands",
            "",
            markdown_table(["Command run", "Requested command", "Status", "Category", "Summary"], rows)
            if rows
            else "No failed or blocked baseline commands were recorded.",
            "",
            "## Static red-check targets",
            "",
            markdown_table(["Target", "Phase", "Reason"], static_targets),
        ]
    )


def render_readme(
    *,
    fingerprint: dict[str, Any],
    packages: dict[str, Any],
    workflows: list[str],
    files: list[str],
) -> str:
    lockfiles = lockfiles_present(files)
    route_profile_default = "developer_preview"
    render_profile = "unknown"
    render_path = REPO_ROOT / "render.yaml"
    if render_path.exists():
        match = re.search(r"PARVA_ROUTE_PROFILE\s*\n\s*value:\s*([A-Za-z0-9_ -]+)", render_path.read_text())
        if match:
            render_profile = match.group(1).strip()
    return "\n\n".join(
        [
            "# Phase 01 Baseline Truth Freeze",
            "",
            f"Generated at: `{now_iso()}`",
            "",
            "This directory freezes the current repository truth before broad refactor or hardening phases. It is an audit baseline, not a product-behavior change.",
            "",
            "## Repository fingerprint",
            "",
            markdown_table(
                ["Field", "Value"],
                [
                    ["git_branch", fingerprint.get("git_branch")],
                    ["git_commit", fingerprint.get("git_commit")],
                    ["git_status_short", fingerprint.get("git_status_short") or "(clean)"],
                    ["python_version", fingerprint.get("python_version")],
                    ["python_executable", fingerprint.get("python_executable")],
                    ["node_version", fingerprint.get("node_version")],
                    ["npm_version", fingerprint.get("npm_version")],
                    ["phase_python_command", fingerprint.get("phase_python_command")],
                    ["phase_python_version", fingerprint.get("phase_python_version")],
                    ["phase_python_executable", fingerprint.get("phase_python_executable")],
                    ["platform", platform.platform()],
                    ["route_profile_default", route_profile_default],
                    ["render_route_profile", render_profile],
                ],
            ),
            "",
            "## Lockfiles present",
            "",
            "\n".join(f"- `{path}`" for path in lockfiles) or "No lockfiles found.",
            "",
            "## CI workflows present",
            "",
            "\n".join(f"- `{path}`" for path in workflows) or "No workflow files found.",
            "",
            "## Package metadata",
            "",
            "```json",
            json.dumps(packages, indent=2, sort_keys=True),
            "```",
            "",
            "## Report files",
            "",
            "\n".join(
                f"- `{path.name}`"
                for path in sorted(REPORT_DIR.glob("*"))
                if path.name != "README.md"
            ),
        ]
    )


def fingerprint(*, phase_python_command: str) -> dict[str, Any]:
    def output(command: str) -> str:
        result = run_command(command, timeout=60)
        return (result.get("stdout_tail") or result.get("summary") or "").strip()

    py_info = output('python -c "import sys; print(sys.executable); print(sys.version)"').splitlines()
    phase_py_info = output(
        f'{phase_python_command} -c "import sys; print(sys.executable); print(sys.version)"'
    ).splitlines()
    return {
        "git_branch": output("git branch --show-current"),
        "git_commit": output("git rev-parse HEAD"),
        "git_status_short": output("git status --short"),
        "python_version": output("python --version"),
        "python_executable": py_info[0] if py_info else "",
        "python_full_version": py_info[1] if len(py_info) > 1 else "",
        "node_version": output("node --version"),
        "npm_version": output("npm --version"),
        "phase_python_command": phase_python_command,
        "phase_python_version": output(f"{phase_python_command} --version"),
        "phase_python_executable": phase_py_info[0] if phase_py_info else "",
        "phase_python_full_version": phase_py_info[1] if len(phase_py_info) > 1 else "",
    }


def run_fingerprint_command_attempts() -> list[dict[str, Any]]:
    return [run_command(command, timeout=60) for command in FINGERPRINT_COMMANDS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Generate inventories without running the long verification matrix.",
    )
    parser.add_argument(
        "--python-command",
        default="python",
        help="Python command to use for Python-based verification commands.",
    )
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    files = all_git_files()
    packages = load_packages()
    workflows = sorted(
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in (REPO_ROOT / ".github" / "workflows").glob("*")
        if path.is_file()
    )

    route_payload = route_inventory()
    duplicates = discover_duplicate_truth_paths(files)
    boundary = boundary_inventory(files)
    test_lanes = test_lane_inventory(files)
    dead_candidates = dead_code_candidates(files)
    generated_gaps = generated_artifact_gaps(files)
    data_payload = data_inventory(files)
    frontend_rows = frontend_inventory(files)
    sdk_payload = sdk_inventory(files, packages)

    if args.skip_verification:
        verification = {
            "generated_at": now_iso(),
            "commands": [
                {
                    "command": command_with_python(item["command"], args.python_command),
                    "requested_command": item["command"],
                    "status": "skipped",
                    "exit_code": None,
                    "summary": "Skipped by --skip-verification.",
                    "blocking_reason": "manual skip",
                    "failure_category": None,
                }
                for item in VERIFICATION_COMMANDS
            ],
        }
    else:
        verification = {
            "generated_at": now_iso(),
            "commands": [
                run_command(
                    command_with_python(item["command"], args.python_command),
                    requested_command=item["command"],
                    timeout=int(item["timeout"]),
                )
                for item in VERIFICATION_COMMANDS
            ],
        }

    fp = fingerprint(phase_python_command=args.python_command)
    fingerprint_attempts = run_fingerprint_command_attempts()
    write_json(REPORT_DIR / "fingerprint_command_attempts.json", fingerprint_attempts)
    write_json(REPORT_DIR / "verification_matrix.json", verification)
    write_text(REPORT_DIR / "verification_matrix.md", render_verification_markdown(verification))
    write_text(REPORT_DIR / "subsystem_inventory.md", render_subsystems_markdown(SUBSYSTEMS))
    write_text(REPORT_DIR / "subsystem_maturity_draft.yaml", subsystem_yaml(SUBSYSTEMS))
    write_json(REPORT_DIR / "route_profile_inventory.json", route_payload)
    write_text(REPORT_DIR / "route_profile_inventory.md", render_route_inventory_markdown(route_payload))
    write_text(
        REPORT_DIR / "canonical_runtime_discovery.md",
        "\n\n".join(
            [
                "# Phase 01 Canonical Runtime Discovery",
                "",
                "This is a draft discovery map for Phase 03. It is not a migration.",
                "",
                render_subsystems_markdown(SUBSYSTEMS).split("\n\n", 2)[-1],
            ]
        ),
    )
    write_text(REPORT_DIR / "duplicate_truth_paths.md", render_duplicate_markdown(duplicates))
    write_json(REPORT_DIR / "duplicate_truth_paths.json", duplicates)
    write_text(REPORT_DIR / "public_private_research_boundary.md", render_boundary_markdown(boundary))
    write_json(REPORT_DIR / "public_private_research_boundary.json", boundary)
    write_text(REPORT_DIR / "test_lane_inventory.md", render_test_lane_markdown(test_lanes))
    write_json(REPORT_DIR / "test_lane_inventory.json", test_lanes)
    write_text(REPORT_DIR / "dead_code_candidates.md", render_dead_code_markdown(dead_candidates))
    write_json(REPORT_DIR / "dead_code_candidates.json", dead_candidates)
    write_text(REPORT_DIR / "generated_artifacts_policy_gaps.md", render_generated_artifacts_markdown(generated_gaps))
    write_json(REPORT_DIR / "generated_artifacts_policy_gaps.json", generated_gaps)
    write_text(REPORT_DIR / "security_surface_inventory.md", render_security_markdown(route_payload))
    write_text(REPORT_DIR / "data_and_source_artifact_inventory.md", render_data_inventory_markdown(data_payload))
    write_json(REPORT_DIR / "data_and_source_artifact_inventory.json", data_payload)
    write_text(REPORT_DIR / "frontend_surface_inventory.md", render_frontend_inventory_markdown(frontend_rows))
    write_json(REPORT_DIR / "frontend_surface_inventory.json", frontend_rows)
    write_text(REPORT_DIR / "sdk_inventory.md", render_sdk_inventory_markdown(sdk_payload))
    write_json(REPORT_DIR / "sdk_inventory.json", sdk_payload)
    write_text(REPORT_DIR / "risk_register_initial.md", render_risk_register())
    write_text(REPORT_DIR / "scorecard_initial.md", render_scorecard())
    write_text(REPORT_DIR / "next_phase_red_check_targets.md", render_next_phase_targets(verification))
    write_text(
        REPORT_DIR / "README.md",
        render_readme(
            fingerprint=fp,
            packages=packages,
            workflows=workflows,
            files=files,
        ),
    )
    print(f"Wrote Phase 01 baseline reports to {REPORT_DIR}")
    failed = [item for item in verification["commands"] if item["status"] in {"fail", "blocked"}]
    print(f"Verification commands: {len(verification['commands'])}; failed/blocked: {len(failed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
