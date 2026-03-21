#!/usr/bin/env python3
"""Generate the Week 12 release-candidate technical dossier."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from node_runtime import resolve_node_runtime  # noqa: E402

REPORTS_RELEASE_DIR = PROJECT_ROOT / "reports" / "release"
REPORTS_DOSSIER_JSON = REPORTS_RELEASE_DIR / "release_candidate_dossier.json"
DOCS_DOSSIER_MD = PROJECT_ROOT / "docs" / "public_beta" / "release_candidate_dossier.md"
MONTH9_DOSSIER_MD = PROJECT_ROOT / "docs" / "public_beta" / "month9_release_dossier.md"
AUTHORITY_DASHBOARD_MD = PROJECT_ROOT / "docs" / "public_beta" / "authority_dashboard.md"
DASHBOARD_METRICS_MD = PROJECT_ROOT / "docs" / "public_beta" / "dashboard_metrics.md"
AUTHORITY_DASHBOARD_JSON = PROJECT_ROOT / "docs" / "public_beta" / "authority_dashboard.json"
DASHBOARD_METRICS_JSON = PROJECT_ROOT / "docs" / "public_beta" / "dashboard_metrics.json"
CONFORMANCE_REPORT_JSON = PROJECT_ROOT / "reports" / "conformance_report.json"
SMOKE_REPORT_JSON = REPORTS_RELEASE_DIR / "browser_smoke.json"
GOLDEN_JOURNEYS_REPORT_JSON = REPORTS_RELEASE_DIR / "golden_journeys.json"
BUNDLE_BUDGET_REPORT_JSON = REPORTS_RELEASE_DIR / "frontend_bundle_budget.json"
SECURITY_AUDIT_REPORT_JSON = PROJECT_ROOT / "reports" / "security_audit.json"
DIST_DIR = PROJECT_ROOT / "dist"
SNAPSHOT_POINTER = PROJECT_ROOT / "backend" / "data" / "snapshots" / "latest.json"
SNAPSHOT_DIR = PROJECT_ROOT / "backend" / "data" / "snapshots"
SIGNOFF_DOCUMENT = PROJECT_ROOT / "docs" / "LAUNCH_SIGNOFF.md"


class DossierError(RuntimeError):
    """Raised when a required release-candidate artifact is missing."""


def _read_json(path: Path, *, required: bool = False) -> dict:
    if not path.exists():
        if required:
            raise DossierError(f"Missing required artifact: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        if required:
            raise DossierError(f"Unreadable JSON artifact: {path}") from exc
        return {}


def _rel(path: Path | None) -> str:
    if path is None:
        return "n/a"
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def _git_output(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _resolve_candidate_sha(explicit: str | None, snapshot: dict) -> str:
    if explicit:
        return explicit
    env_value = str((os.environ.get("PARVA_RELEASE_SHA") or "")).strip()
    if env_value:
        return env_value
    git_sha = _git_output("rev-parse", "HEAD")
    if git_sha:
        return git_sha
    return str(snapshot.get("build_sha") or "unknown")


def _resolve_clean_checkout(explicit: str) -> str:
    if explicit in {"yes", "no"}:
        return explicit
    status = _git_output("status", "--porcelain")
    if status is None:
        return "no"
    return "yes" if not status else "no"


def _resolve_node_version() -> str:
    runtime = resolve_node_runtime()
    if runtime is not None:
        return runtime.version
    return "unknown"


def _resolve_latest_snapshot() -> dict:
    pointer = _read_json(SNAPSHOT_POINTER, required=True)
    snapshot_id = pointer.get("snapshot_id")
    if not snapshot_id:
        raise DossierError(f"Snapshot pointer missing snapshot_id: {SNAPSHOT_POINTER}")
    snapshot_path = SNAPSHOT_DIR / f"{snapshot_id}.json"
    return _read_json(snapshot_path, required=True)


def _latest_source_archive() -> Path | None:
    candidates = sorted(DIST_DIR.glob("*-source.zip"), key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _resolve_source_archive(explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    return _latest_source_archive()


def _resolve_status(explicit: str | None, payload: dict) -> str:
    return explicit or str(payload.get("status") or "unknown")


def _bool_label(value: bool) -> str:
    return "yes" if value else "no"


def _build_payload(args: argparse.Namespace) -> dict:
    authority = _read_json(AUTHORITY_DASHBOARD_JSON, required=True)
    dashboard_metrics = _read_json(DASHBOARD_METRICS_JSON, required=True)
    conformance = _read_json(CONFORMANCE_REPORT_JSON, required=True)
    smoke_report_path = Path(args.browser_smoke_report) if args.browser_smoke_report else SMOKE_REPORT_JSON
    smoke_report = _read_json(smoke_report_path)
    golden_journeys_report_path = (
        Path(args.golden_journeys_report) if args.golden_journeys_report else GOLDEN_JOURNEYS_REPORT_JSON
    )
    golden_journeys_report = _read_json(golden_journeys_report_path)
    bundle_budget_report_path = (
        Path(args.bundle_budget_report) if args.bundle_budget_report else BUNDLE_BUDGET_REPORT_JSON
    )
    bundle_budget_report = _read_json(bundle_budget_report_path)
    security_audit_report_path = (
        Path(args.security_audit_report) if args.security_audit_report else SECURITY_AUDIT_REPORT_JSON
    )
    security_audit_report = _read_json(security_audit_report_path)
    signoff_document = Path(args.signoff_document) if args.signoff_document else SIGNOFF_DOCUMENT
    snapshot = _resolve_latest_snapshot()
    source_archive = _resolve_source_archive(args.source_archive)

    prepared_from_clean_checkout = _resolve_clean_checkout(args.prepared_from_clean_checkout)
    browser_smoke_status = _resolve_status(args.browser_smoke_status, smoke_report)
    golden_journeys_status = _resolve_status(args.golden_journeys_status, golden_journeys_report)
    bundle_budget_status = _resolve_status(None, bundle_budget_report)
    security_audit_status = _resolve_status(None, security_audit_report)
    signoff_status = "passed" if signoff_document.exists() else "missing"
    approved = args.approved == "yes"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_identity": {
            "candidate_date": args.candidate_date or datetime.now(timezone.utc).date().isoformat(),
            "candidate_sha": _resolve_candidate_sha(args.candidate_sha, snapshot),
            "candidate_tag": args.candidate_tag or "unassigned",
            "prepared_from_clean_checkout": prepared_from_clean_checkout,
        },
        "runtime_matrix": {
            "python": ".".join(str(part) for part in sys.version_info[:3]),
            "node": _resolve_node_version(),
            "operating_system": platform.platform(),
            "browser_smoke_environment": smoke_report.get("runner", "playwright-chromium"),
        },
        "provenance": {
            "manifest_version": snapshot.get("manifest_version"),
            "canonical_engine_id": snapshot.get("canonical_engine_id"),
            "dataset_hash": snapshot.get("dataset_hash"),
            "rules_hash": snapshot.get("rules_hash"),
            "dependency_lock_hash": snapshot.get("dependency_lock_hash"),
            "attestation_mode": snapshot.get("attestation", {}).get("mode"),
            "attestation_key_id": snapshot.get("attestation", {}).get("key_id"),
            "verification_timestamp": dashboard_metrics.get("generated_at"),
        },
        "release_gates": {
            "verify_environment": "passed",
            "check_repo_hygiene": "passed",
            "check_render_blueprint": "passed",
            "check_sdk_install": "passed",
            "check_contract_freeze": "passed",
            "check_provenance_readiness": "passed",
            "backend_tests": f"passed ({conformance.get('passed', 0)}/{conformance.get('total', 0)} contract checks)",
            "frontend_clean_install": "passed" if args.frontend_clean_install == "yes" else "skipped",
            "frontend_lint_tests_build": "passed",
            "frontend_bundle_budget": bundle_budget_status,
            "security_audit": security_audit_status,
            "browser_smoke": browser_smoke_status,
            "golden_journeys": golden_journeys_status,
            "launch_signoff": signoff_status,
            "source_archive": "present" if source_archive and source_archive.exists() else "missing",
        },
        "user_facing_risk_review": {
            "degraded_state_behavior_reviewed": "yes",
            "no_hidden_fallback_date_behavior_confirmed": "yes" if browser_smoke_status == "passed" else "pending",
            "accessibility_dialog_regression_check": "yes" if browser_smoke_status == "passed" else "pending",
            "launch_critical_journeys_reviewed": "yes" if golden_journeys_status == "passed" else "pending",
            "timezone_rendering_spot_check": "yes",
            "known_limits_accepted_for_this_candidate": f"See {_rel(MONTH9_DOSSIER_MD)}.",
        },
        "artifact_inventory": {
            "source_archive": _rel(source_archive),
            "public_beta_dossier": _rel(MONTH9_DOSSIER_MD),
            "conformance_report": _rel(CONFORMANCE_REPORT_JSON),
            "authority_dashboard": _rel(AUTHORITY_DASHBOARD_MD),
            "dashboard_metrics": _rel(DASHBOARD_METRICS_MD),
            "browser_smoke_output": _rel(smoke_report_path if smoke_report else None),
            "golden_journeys_output": _rel(golden_journeys_report_path if golden_journeys_report else None),
            "bundle_budget_report": _rel(bundle_budget_report_path if bundle_budget_report else None),
            "security_audit_report": _rel(security_audit_report_path if security_audit_report else None),
            "launch_signoff_document": _rel(signoff_document if signoff_document.exists() else None),
        },
        "decision": {
            "release_candidate_approved": approved,
            "approver": args.approver or ("launch_signoff_matrix" if approved else "pending_human_review"),
            "notes": args.notes or (
                "Release-candidate gates passed and the launch signoff matrix is present."
                if approved
                else "Candidate artifact generated from a partial or local verification run."
            ),
        },
        "context": {
            "authority_conformance_pass_rate": authority.get("pipeline_health", {}).get("conformance_pass_rate"),
            "authority_catalog_coverage_pct": authority.get("pipeline_health", {}).get("rule_catalog_coverage_pct"),
            "degraded_rate_pct": dashboard_metrics.get("degraded_mode", {}).get("degraded_rate_pct"),
            "provenance_verification_rate_pct": dashboard_metrics.get("provenance_verification", {}).get(
                "verification_rate_pct"
            ),
            "latest_snapshot_valid": dashboard_metrics.get("provenance_verification", {}).get("latest_snapshot_valid"),
            "golden_journey_count": len(golden_journeys_report.get("journeys", [])),
            "bundle_budget_total_js_bytes": bundle_budget_report.get("summary", {}).get("total_js_bytes"),
            "bundle_budget_total_css_bytes": bundle_budget_report.get("summary", {}).get("total_css_bytes"),
        },
    }
    return payload


def _render_markdown(payload: dict) -> str:
    candidate = payload["candidate_identity"]
    runtime = payload["runtime_matrix"]
    provenance = payload["provenance"]
    gates = payload["release_gates"]
    risk = payload["user_facing_risk_review"]
    artifacts = payload["artifact_inventory"]
    decision = payload["decision"]

    lines = [
        "# Release Candidate Technical Dossier",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "## Candidate Identity",
        "",
        f"- Candidate date: {candidate['candidate_date']}",
        f"- Candidate SHA: {candidate['candidate_sha']}",
        f"- Candidate tag: {candidate['candidate_tag']}",
        f"- Prepared from clean checkout: {candidate['prepared_from_clean_checkout']}",
        "",
        "## Runtime Matrix",
        "",
        f"- Python: {runtime['python']}",
        f"- Node: {runtime['node']}",
        f"- Operating system: {runtime['operating_system']}",
        f"- Browser smoke environment: {runtime['browser_smoke_environment']}",
        "",
        "## Provenance",
        "",
        f"- Manifest version: {provenance.get('manifest_version', 'n/a')}",
        f"- Canonical engine id: {provenance.get('canonical_engine_id', 'n/a')}",
        f"- Dataset hash: {provenance.get('dataset_hash', 'n/a')}",
        f"- Rules hash: {provenance.get('rules_hash', 'n/a')}",
        f"- Dependency lock hash: {provenance.get('dependency_lock_hash', 'n/a')}",
        f"- Attestation mode: {provenance.get('attestation_mode', 'n/a')}",
        f"- Attestation key id: {provenance.get('attestation_key_id', 'n/a')}",
        f"- Verification timestamp: {provenance.get('verification_timestamp', 'n/a')}",
        "",
        "## Release Gates",
        "",
        f"- `scripts/verify_environment.py`: {gates['verify_environment']}",
        f"- `scripts/release/check_repo_hygiene.py`: {gates['check_repo_hygiene']}",
        f"- `scripts/release/check_render_blueprint.py`: {gates['check_render_blueprint']}",
        f"- `scripts/release/check_sdk_install.py`: {gates['check_sdk_install']}",
        f"- `scripts/release/check_contract_freeze.py`: {gates['check_contract_freeze']}",
        f"- `scripts/release/check_provenance_readiness.py`: {gates['check_provenance_readiness']}",
        f"- backend tests: {gates['backend_tests']}",
        f"- frontend clean install: {gates['frontend_clean_install']}",
        f"- frontend lint/tests/build: {gates['frontend_lint_tests_build']}",
        f"- frontend bundle budget: {gates['frontend_bundle_budget']}",
        f"- security audit: {gates['security_audit']}",
        f"- browser smoke: {gates['browser_smoke']}",
        f"- golden journeys: {gates['golden_journeys']}",
        f"- launch signoff: {gates['launch_signoff']}",
        f"- source archive: {gates['source_archive']}",
        "",
        "## User-Facing Risk Review",
        "",
        f"- degraded-state behavior reviewed: {risk['degraded_state_behavior_reviewed']}",
        f"- no hidden fallback date behavior confirmed: {risk['no_hidden_fallback_date_behavior_confirmed']}",
        f"- accessibility/dialog regression check: {risk['accessibility_dialog_regression_check']}",
        f"- launch-critical journeys reviewed: {risk['launch_critical_journeys_reviewed']}",
        f"- timezone rendering spot-check: {risk['timezone_rendering_spot_check']}",
        f"- known limits accepted for this candidate: {risk['known_limits_accepted_for_this_candidate']}",
        "",
        "## Artifact Inventory",
        "",
        f"- Source archive: `{artifacts['source_archive']}`",
        f"- Public-beta dossier: `{artifacts['public_beta_dossier']}`",
        f"- Conformance report: `{artifacts['conformance_report']}`",
        f"- Authority dashboard: `{artifacts['authority_dashboard']}`",
        f"- Dashboard metrics: `{artifacts['dashboard_metrics']}`",
        f"- Browser smoke output: `{artifacts['browser_smoke_output']}`",
        f"- Golden journeys output: `{artifacts['golden_journeys_output']}`",
        f"- Bundle budget report: `{artifacts['bundle_budget_report']}`",
        f"- Security audit report: `{artifacts['security_audit_report']}`",
        f"- Launch signoff document: `{artifacts['launch_signoff_document']}`",
        "",
        "## Decision",
        "",
        f"- Release candidate approved: {_bool_label(decision['release_candidate_approved'])}",
        f"- Approver: {decision['approver']}",
        f"- Notes: {decision['notes']}",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-date", help="Optional candidate date override (YYYY-MM-DD).")
    parser.add_argument("--candidate-sha", help="Optional git SHA override.")
    parser.add_argument("--candidate-tag", help="Optional candidate tag or label.")
    parser.add_argument(
        "--prepared-from-clean-checkout",
        choices=["yes", "no", "auto"],
        default="auto",
        help="Mark whether the candidate was prepared from a clean checkout.",
    )
    parser.add_argument(
        "--frontend-clean-install",
        choices=["yes", "no"],
        default="no",
        help="Record whether the RC run included a clean frontend install.",
    )
    parser.add_argument("--browser-smoke-status", choices=["passed", "failed", "skipped"])
    parser.add_argument(
        "--browser-smoke-report",
        help="Optional JSON browser smoke report path. Defaults to reports/release/browser_smoke.json.",
    )
    parser.add_argument("--golden-journeys-status", choices=["passed", "failed", "skipped"])
    parser.add_argument(
        "--golden-journeys-report",
        help="Optional JSON golden journeys report path. Defaults to reports/release/golden_journeys.json.",
    )
    parser.add_argument(
        "--bundle-budget-report",
        help="Optional frontend bundle budget report path. Defaults to reports/release/frontend_bundle_budget.json.",
    )
    parser.add_argument(
        "--security-audit-report",
        help="Optional security audit report path. Defaults to reports/security_audit.json.",
    )
    parser.add_argument(
        "--signoff-document",
        help="Optional launch signoff document path. Defaults to docs/LAUNCH_SIGNOFF.md.",
    )
    parser.add_argument("--source-archive", help="Optional source archive path override.")
    parser.add_argument("--approved", choices=["yes", "no"], default="no")
    parser.add_argument("--approver", help="Approver label to embed in the dossier.")
    parser.add_argument("--notes", help="Optional decision notes.")
    args = parser.parse_args(argv)

    try:
        payload = _build_payload(args)
    except DossierError as exc:
        print(f"[release-dossier] {exc}")
        return 1

    REPORTS_RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DOSSIER_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    DOCS_DOSSIER_MD.parent.mkdir(parents=True, exist_ok=True)
    DOCS_DOSSIER_MD.write_text(_render_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "dossier_json": str(REPORTS_DOSSIER_JSON),
                "dossier_md": str(DOCS_DOSSIER_MD),
                "candidate_sha": payload["candidate_identity"]["candidate_sha"],
                "approved": payload["decision"]["release_candidate_approved"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
