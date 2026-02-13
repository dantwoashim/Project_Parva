#!/usr/bin/env python3
"""Generate authority dashboard from CI artifacts and runtime metadata."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs" / "public_beta"
OUT_JSON = REPORTS_DIR / "authority_dashboard.json"
OUT_DOC_JSON = DOCS_DIR / "authority_dashboard.json"
OUT_MD = DOCS_DIR / "authority_dashboard.md"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _collect_discrepancy_classes() -> Dict[str, int]:
    counts: Counter[str] = Counter()
    ignore = {"match", "exact_match", "ok", "none"}

    eval_v4 = _read_json(REPORTS_DIR / "evaluation_v4" / "evaluation_v4.json")
    for cause, value in (eval_v4.get("summary", {}).get("causes", {}) or {}).items():
        cause_key = str(cause).strip().lower()
        if cause_key not in ignore:
            counts[cause_key] += int(value)
    for row in eval_v4.get("rows", []):
        if row.get("passed") is False:
            cause = str(row.get("probable_cause") or "unclassified").strip().lower()
            if cause not in ignore:
                counts[cause] += 1

    discrepancies = _read_json(PROJECT_ROOT / "data" / "ground_truth" / "discrepancies.json")
    for cause, value in (discrepancies.get("summary", {}).get("by_cause", {}) or {}).items():
        cause_key = str(cause).strip().lower()
        if cause_key not in ignore:
            counts[cause_key] += int(value)
    for row in discrepancies.get("discrepancies", []):
        cause = str(row.get("probable_cause") or row.get("cause") or "unclassified").strip().lower()
        if cause not in ignore:
            counts[cause] += 1

    return dict(sorted(counts.items(), key=lambda item: item[0]))


def _collect_rule_confidence_breakdown() -> Dict[str, int]:
    catalog = _read_json(PROJECT_ROOT / "data" / "festivals" / "festival_rules_v4.json")
    rows = catalog.get("festivals", [])
    return dict(Counter(str(row.get("confidence", "unknown")) for row in rows))


def _collect_response_confidence_breakdown() -> Dict[str, Any]:
    client = TestClient(app)
    endpoints = [
        "/v5/api/calendar/today",
        "/v5/api/calendar/convert?date=2026-02-15",
        "/v5/api/calendar/panchanga?date=2026-02-15",
        "/v5/api/festivals/upcoming?days=30",
        "/v5/api/festivals/coverage",
        "/v5/api/resolve?date=2026-10-21",
        "/v5/api/spec/conformance",
    ]
    confidence = Counter()
    boundary = Counter()
    failures = []

    for endpoint in endpoints:
        response = client.get(endpoint)
        if response.status_code != 200:
            failures.append({"endpoint": endpoint, "status_code": response.status_code})
            continue
        try:
            payload = response.json()
            meta = payload.get("meta", {})
            confidence_level = str(meta.get("confidence", {}).get("level", "unknown"))
            confidence[confidence_level] += 1
            boundary_risk = str(meta.get("uncertainty", {}).get("boundary_risk", "unknown"))
            boundary[boundary_risk] += 1
        except Exception:
            failures.append({"endpoint": endpoint, "status_code": response.status_code, "error": "invalid_json"})

    return {
        "sample_size": len(endpoints),
        "confidence_levels": dict(confidence),
        "boundary_risk": dict(boundary),
        "failed_samples": failures,
    }


def _collect_pipeline_health() -> Dict[str, Any]:
    conformance = _read_json(REPORTS_DIR / "conformance_report.json")
    ingestion = _read_json(REPORTS_DIR / "rule_ingestion_summary.json")
    e2e_path = PROJECT_ROOT / "docs" / "weekly_execution" / "year1_week36" / "e2e_smoke.md"

    return {
        "conformance_total": conformance.get("total"),
        "conformance_passed": conformance.get("passed"),
        "conformance_pass_rate": conformance.get("pass_rate"),
        "rule_catalog_total": ingestion.get("total_rules"),
        "rule_catalog_generated": ingestion.get("generated_rules"),
        "rule_catalog_coverage_pct": ingestion.get("coverage_pct"),
        "smoke_reference_present": e2e_path.exists(),
    }


def _build_markdown(payload: Dict[str, Any]) -> str:
    discrepancy_rows = payload["discrepancy_classes"]
    confidence_rules = payload["confidence_breakdown"]["rule_catalog"]
    confidence_responses = payload["confidence_breakdown"]["response_samples"]["confidence_levels"]

    lines = [
        "# Authority Dashboard",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Release Track: `{payload['release_track']}`",
        "",
        "## Pipeline Health",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Conformance Pass Rate | {payload['pipeline_health'].get('conformance_pass_rate', 0)}% |",
        f"| Rule Catalog Total | {payload['pipeline_health'].get('rule_catalog_total', 0)} |",
        f"| Rule Catalog Coverage (target 300) | {payload['pipeline_health'].get('rule_catalog_coverage_pct', 0)}% |",
        "",
        "## Discrepancy Classes",
        "",
    ]

    if discrepancy_rows:
        lines.extend(
            [
                "| Class | Count |",
                "|---|---:|",
            ]
        )
        for key, value in discrepancy_rows.items():
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("- No discrepancies recorded in current artifacts.")

    lines.extend(
        [
            "",
            "## Confidence Breakdown",
            "",
            "### Rule Catalog Confidence",
            "",
            "| Confidence | Count |",
            "|---|---:|",
        ]
    )
    for key, value in confidence_rules.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "### Runtime Response Confidence (sampled v5 endpoints)",
            "",
            "| Confidence | Count |",
            "|---|---:|",
        ]
    )
    for key, value in confidence_responses.items():
        lines.append(f"| {key} | {value} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    discrepancy_classes = _collect_discrepancy_classes()
    confidence_breakdown = {
        "rule_catalog": _collect_rule_confidence_breakdown(),
        "response_samples": _collect_response_confidence_breakdown(),
    }
    pipeline_health = _collect_pipeline_health()

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_track": "authority-v5",
        "pipeline_health": pipeline_health,
        "discrepancy_classes": discrepancy_classes,
        "confidence_breakdown": confidence_breakdown,
        "artifacts": {
            "conformance_report": str(REPORTS_DIR / "conformance_report.json"),
            "evaluation_v4": str(REPORTS_DIR / "evaluation_v4" / "evaluation_v4.json"),
            "discrepancies": str(PROJECT_ROOT / "data" / "ground_truth" / "discrepancies.json"),
            "rule_catalog": str(PROJECT_ROOT / "data" / "festivals" / "festival_rules_v4.json"),
            "rule_ingestion_summary": str(REPORTS_DIR / "rule_ingestion_summary.json"),
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_DOC_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(_build_markdown(payload), encoding="utf-8")

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_DOC_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
