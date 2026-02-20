#!/usr/bin/env python3
"""Generate Month-9 evaluator dossier with reproducible evidence artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.rules.catalog_v4 import get_rules_scoreboard  # noqa: E402

REPORTS_RELEASE_DIR = PROJECT_ROOT / "reports" / "release"
REPORTS_RELEASE_JSON = REPORTS_RELEASE_DIR / "month9_dossier.json"
DOCS_RELEASE_MD = PROJECT_ROOT / "docs" / "public_beta" / "month9_release_dossier.md"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_known_limits() -> list[str]:
    known_limits_path = PROJECT_ROOT / "docs" / "KNOWN_LIMITS.md"
    if not known_limits_path.exists():
        return []

    lines = known_limits_path.read_text(encoding="utf-8").splitlines()
    bullet_lines = [line.strip().lstrip("- ").strip() for line in lines if line.strip().startswith("-")]
    return [line for line in bullet_lines if line]


def _build_payload() -> dict:
    client = TestClient(app)

    scoreboard = get_rules_scoreboard(target=300)
    plugin_quality = client.get("/v3/api/engine/plugins/quality").json()

    personal = client.get("/v3/api/personal/panchanga", params={"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"}).json()
    muhurta = client.get(
        "/v3/api/muhurta/auspicious",
        params={
            "date": "2026-02-15",
            "type": "vivah",
            "lat": 27.7172,
            "lon": 85.3240,
            "tz": "Asia/Kathmandu",
            "birth_nakshatra": "7",
            "assumption_set": "np-mainstream-v2",
        },
    ).json()
    kundali = client.get(
        "/v3/api/kundali",
        params={
            "datetime": "2026-02-15T06:30:00+05:45",
            "lat": 27.7172,
            "lon": 85.3240,
            "tz": "Asia/Kathmandu",
        },
    ).json()

    conformance = _read_json(PROJECT_ROOT / "reports" / "conformance_report.json")
    authority = _read_json(PROJECT_ROOT / "reports" / "authority_dashboard.json")
    accuracy = _read_json(PROJECT_ROOT / "reports" / "accuracy" / "annual_accuracy_2082.json")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_track": "v3-public-month9",
        "coverage_scoreboard": scoreboard,
        "plugin_quality": plugin_quality,
        "quality_gates": {
            "conformance": {
                "total": conformance.get("total"),
                "passed": conformance.get("passed"),
                "pass_rate": conformance.get("pass_rate"),
            },
            "authority_dashboard": {
                "conformance_pass_rate": authority.get("pipeline_health", {}).get("conformance_pass_rate"),
                "catalog_total": authority.get("pipeline_health", {}).get("rule_catalog_total"),
                "catalog_coverage_pct": authority.get("pipeline_health", {}).get("rule_catalog_coverage_pct"),
            },
            "accuracy": {
                "total_comparisons": accuracy.get("total_comparisons"),
                "accuracy_pct": accuracy.get("accuracy_pct"),
                "within_one_day_pct": accuracy.get("within_one_day_pct"),
            },
        },
        "personal_stack_methodology": {
            "personal_panchanga": {
                "method_profile": personal.get("method_profile"),
                "quality_band": personal.get("quality_band"),
                "assumption_set_id": personal.get("assumption_set_id"),
                "advisory_scope": personal.get("advisory_scope"),
            },
            "muhurta": {
                "method_profile": muhurta.get("method_profile"),
                "quality_band": muhurta.get("quality_band"),
                "assumption_set_id": muhurta.get("assumption_set_id"),
                "advisory_scope": muhurta.get("advisory_scope"),
            },
            "kundali": {
                "method_profile": kundali.get("method_profile"),
                "quality_band": kundali.get("quality_band"),
                "assumption_set_id": kundali.get("assumption_set_id"),
                "advisory_scope": kundali.get("advisory_scope"),
            },
        },
        "known_limits": _load_known_limits(),
        "artifacts": {
            "conformance_report": str(PROJECT_ROOT / "reports" / "conformance_report.json"),
            "authority_dashboard": str(PROJECT_ROOT / "reports" / "authority_dashboard.json"),
            "accuracy_report": str(PROJECT_ROOT / "reports" / "accuracy" / "annual_accuracy_2082.json"),
            "coverage_catalog": str(PROJECT_ROOT / "data" / "festivals" / "festival_rules_v4.json"),
        },
    }


def _render_markdown(payload: dict) -> str:
    scoreboard = payload["coverage_scoreboard"]
    plugin_rows = payload["plugin_quality"].get("plugins", [])
    personal = payload["personal_stack_methodology"]

    lines = [
        "# Month 9 Release Dossier (v3 Public)",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "## Coverage Scoreboard",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Computed Rules | {scoreboard.get('computed', {}).get('count', 0)} |",
        f"| Provisional Rules | {scoreboard.get('provisional', {}).get('count', 0)} |",
        f"| Inventory Rules | {scoreboard.get('inventory', {}).get('count', 0)} |",
        f"| Safe To Claim 300 | {scoreboard.get('claim_guard', {}).get('safe_to_claim_300', False)} |",
        "",
        "## Plugin Quality (Parity)",
        "",
        "| Plugin | Cases | Pass Rate | Quality Band | Within Error Budget |",
        "|---|---:|---:|---|---|",
    ]

    for row in sorted(plugin_rows, key=lambda item: item.get("plugin_id", "")):
        cal = row.get("confidence_calibration", {})
        lines.append(
            f"| {row.get('plugin_id')} | {row.get('validation_cases_total', 0)} | {row.get('pass_rate', 0)}% | {row.get('quality_band', 'provisional')} | {cal.get('within_error_budget', False)} |"
        )

    lines.extend([
        "",
        "## Personal Stack Methodology",
        "",
        "| Module | Method Profile | Quality | Assumption Set | Advisory Scope |",
        "|---|---|---|---|---|",
        f"| Personal Panchanga | {personal.get('personal_panchanga', {}).get('method_profile', 'n/a')} | {personal.get('personal_panchanga', {}).get('quality_band', 'n/a')} | {personal.get('personal_panchanga', {}).get('assumption_set_id', 'n/a')} | {personal.get('personal_panchanga', {}).get('advisory_scope', 'n/a')} |",
        f"| Muhurta | {personal.get('muhurta', {}).get('method_profile', 'n/a')} | {personal.get('muhurta', {}).get('quality_band', 'n/a')} | {personal.get('muhurta', {}).get('assumption_set_id', 'n/a')} | {personal.get('muhurta', {}).get('advisory_scope', 'n/a')} |",
        f"| Kundali | {personal.get('kundali', {}).get('method_profile', 'n/a')} | {personal.get('kundali', {}).get('quality_band', 'n/a')} | {personal.get('kundali', {}).get('assumption_set_id', 'n/a')} | {personal.get('kundali', {}).get('advisory_scope', 'n/a')} |",
        "",
        "## Known Limits",
        "",
    ])

    known_limits = payload.get("known_limits", [])
    if known_limits:
        lines.extend([f"- {item}" for item in known_limits])
    else:
        lines.append("- See `/docs/KNOWN_LIMITS.md`.")

    lines.extend([
        "",
        "## Evidence Artifacts",
        "",
        f"- `{payload['artifacts']['conformance_report']}`",
        f"- `{payload['artifacts']['authority_dashboard']}`",
        f"- `{payload['artifacts']['accuracy_report']}`",
        f"- `{payload['artifacts']['coverage_catalog']}`",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    payload = _build_payload()

    REPORTS_RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_RELEASE_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    DOCS_RELEASE_MD.parent.mkdir(parents=True, exist_ok=True)
    DOCS_RELEASE_MD.write_text(_render_markdown(payload), encoding="utf-8")

    print(json.dumps({
        "dossier_json": str(REPORTS_RELEASE_JSON),
        "dossier_md": str(DOCS_RELEASE_MD),
        "computed_rules": payload.get("coverage_scoreboard", {}).get("computed", {}).get("count"),
        "sota_badge_allowed": payload.get("plugin_quality", {}).get("global", {}).get("sota_badge_allowed"),
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
