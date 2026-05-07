#!/usr/bin/env python3
"""Verify the final future-BS and InfoDevelopers artifact package."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "data/future_bs/reports/claim_readiness_v_final.json",
    "data/future_bs/reports/time_travel_official_v_final.json",
    "data/future_bs/reports/time_travel_mismatch_diagnosis_v_final.md",
    "data/future_bs/reports/case_2083_ashwin_replay_v_final.json",
    "data/future_bs/reports/case_2083_ashwin_replay_v_final.md",
    "data/future_bs/reports/invalid_year_total_reconciliation_v_final.json",
    "data/future_bs/reports/parva_shadow_audit_sample_v_final.xlsx",
    "data/future_bs/reports/parva_shadow_audit_sample_v_final.md",
    "data/future_bs/reports/parva_calendar_var_sample_v_final.json",
    "data/future_bs/reports/parva_calendar_var_sample_v_final.md",
    "data/future_bs/reports/residual_report_v_final.md",
    "data/future_bs/accuracy_lab/best_model_config.json",
    "data/future_bs/accuracy_lab/best_metrics.json",
    "data/future_bs/accuracy_lab/accuracy_readiness_final.json",
    "data/future_bs/accuracy_lab/accuracy_readiness_final.md",
    "data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json",
    "data/future_bs/predictions/parva_future_bs_accuracy_best_claimable_subset.json",
    "data/future_bs/infodevelopers_ready/PARVA_INFODEVELOPERS_READINESS_SUMMARY.json",
    "data/future_bs/infodevelopers_ready/PARVA_INFODEVELOPERS_READINESS_SUMMARY.md",
    "data/future_bs/infodevelopers_ready/sample_infodev_input_sheet.xlsx",
    "docs/infodevelopers/INFODEVELOPERS_EXECUTIVE_SUMMARY.md",
    "docs/infodevelopers/INFODEVELOPERS_DEMO_SCRIPT.md",
    "docs/infodevelopers/SAFE_CLAIMS.md",
    "docs/infodevelopers/LIMITATIONS.md",
    "docs/infodevelopers/METHODOLOGY.md",
]


def _json(relative: str):
    return json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))


def _fail(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    missing = [relative for relative in REQUIRED_FILES if not (PROJECT_ROOT / relative).exists() or (PROJECT_ROOT / relative).stat().st_size == 0]
    if missing:
        _fail("Missing or empty final artifacts: " + ", ".join(missing))

    claim = _json("data/future_bs/reports/claim_readiness_v_final.json")
    if claim["official_cases"] < claim["required_official_cases"] and claim["claim_ready_99_green_zone"]:
        _fail("claim_ready_99_green_zone must be false when official cases are below requirement")

    prediction = _json("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json")
    if prediction.get("publication_status") != "computed_prediction_not_official":
        _fail("best prediction artifact missing top-level publication_status")
    invalid = []
    for year, payload in prediction.get("years", {}).items():
        total = sum(int(value) for value in payload.get("months", []))
        if total not in {365, 366}:
            if not all(detail.get("risk_label") == "RED" for detail in payload.get("month_details", [])):
                invalid.append(year)
        for detail in payload.get("month_details", []):
            if len(detail.get("prediction_set_95", [])) > 1 and detail.get("risk_label") == "GREEN":
                _fail(f"wide prediction set marked GREEN: {year} month {detail.get('month')}")
    if invalid:
        _fail("Invalid totals not marked RED/non-claimable: " + ", ".join(invalid))

    report = (PROJECT_ROOT / "IMPLEMENTATION_REPORT.md").read_text(encoding="utf-8")
    for relative in REQUIRED_FILES:
        if relative in report and not (PROJECT_ROOT / relative).exists():
            _fail(f"IMPLEMENTATION_REPORT.md references missing file {relative}")
    generated_mentions = re.findall(r"data/future_bs/[^`)\s]+|docs/infodevelopers/[^`)\s]+", report)
    missing_mentions = [item for item in generated_mentions if not (PROJECT_ROOT / item).exists()]
    if missing_mentions:
        _fail("IMPLEMENTATION_REPORT.md references missing files: " + ", ".join(sorted(set(missing_mentions))))

    print(json.dumps({"ok": True, "checked": len(REQUIRED_FILES), "publication_status": "computed_prediction_not_official"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
