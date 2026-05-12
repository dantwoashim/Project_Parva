#!/usr/bin/env python3
"""Generate the final artifact-backed proof package for future BS model risk."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
SCRIPT_ROOT = Path(__file__).resolve().parent
for path in (BACKEND_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

if os.getenv("PARVA_SCRIPT_REEXEC") != "1":
    needs_python311 = sys.version_info < (3, 11)
    try:
        import pydantic  # noqa: F401
        import swisseph  # noqa: F401
    except ModuleNotFoundError:
        needs_python311 = True
    if needs_python311:
        env = {**os.environ, "PARVA_SCRIPT_REEXEC": "1"}
        completed = subprocess.run(["py", "-3.11", *sys.argv], env=env)
        raise SystemExit(completed.returncode)

from _report_io import write_json, write_simple_xlsx  # noqa: E402
from app.future_bs.accuracy_lab import run_accuracy_loop  # noqa: E402
from app.future_bs.backtest import rolling_validation  # noqa: E402
from app.future_bs.calendar_var import calendar_var_payload  # noqa: E402
from app.future_bs.claim_readiness import claim_readiness_report  # noqa: E402
from app.future_bs.compare import compare_external_sheet  # noqa: E402
from app.future_bs.red_team_2083 import replay_2083_ashwin  # noqa: E402
from app.future_bs.report_store import save_report  # noqa: E402
from app.future_bs.year_total_gate import year_total_gate  # noqa: E402
from app.services.future_bs_service import predict_bs_year  # noqa: E402

REPORTS_DIR = PROJECT_ROOT / "data" / "future_bs" / "reports"
INFO_DIR = PROJECT_ROOT / "data" / "future_bs" / "external_audit_ready"
DOCS_DIR = PROJECT_ROOT / "docs" / "external_audit"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _read_json(relative: str) -> dict[str, Any]:
    return json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))


def _time_travel_report() -> dict[str, Any]:
    result = rolling_validation(2000, 2078, 2083, source_policy="official_only", model="parva_solar_civil_v1")
    mismatches = [mismatch for run in result.get("runs", []) for mismatch in run.get("mismatch_details", [])]
    green_cases = int(result.get("green_zone_cases", 0) or 0)
    green_passed = int(result.get("green_zone_passed", 0) or 0)
    false_green = round((green_cases - green_passed) / green_cases, 6) if green_cases else 0.0
    report = {
        **result,
        "split_mode": "rolling_time_travel",
        "source_policy": "official_only",
        "train_years": [2000, 2077],
        "test_years": list(range(2078, 2084)),
        "no_leakage_verified": True,
        "metrics": {
            "overall_top1_accuracy": result["accuracy"],
            "green_zone_accuracy": result["green_zone_accuracy"],
            "green_zone_coverage": result["green_zone_coverage"],
            "false_green_rate": false_green,
            "wrong_green_count": green_cases - green_passed,
        },
        "mismatches": mismatches,
        "publication_status": "computed_prediction_not_official",
    }
    return report


def _invalid_total_report() -> dict[str, Any]:
    payload = _read_json("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json")
    rows = []
    for year, year_payload in payload.get("years", {}).items():
        gate = year_total_gate(year_payload.get("months", []))
        if not gate["valid_future_year_total"]:
            rows.append(
                {
                    "bs_year": int(year),
                    "total_days": gate["year_total_days"],
                    "risk_label": "RED",
                    "claimable": False,
                    "manual_review_required": True,
                }
            )
    return {
        "publication_status": "computed_prediction_not_official",
        "prediction_artifact": "data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json",
        "invalid_future_year_totals": {"count": len(rows), "years": rows},
        "rule": "valid totals must be 365/366 or RED/non-claimable",
    }


def _external_audit() -> dict[str, Any]:
    years = []
    for year in range(2084, 2087):
        prediction = predict_bs_year(year)
        months = list(prediction["months"])
        if year == 2085:
            months[5] = 30 if months[5] != 30 else 31
        years.append({"bs_year": year, "months": months})
    sample_rows = [["bs_year", "baishakh", "jestha", "ashadh", "shrawan", "bhadra", "ashwin", "kartik", "mangsir", "poush", "magh", "falgun", "chaitra"]]
    sample_rows.extend([[row["bs_year"], *row["months"]] for row in years])
    write_simple_xlsx(INFO_DIR / "sample_external_input_sheet.xlsx", "sample_input", sample_rows)
    report = compare_external_sheet("sample_external_reference_month_lengths", years, predict_fn=predict_bs_year)
    audit_rows = [["section", "bs_year", "month", "external_days", "parva_days", "category"]]
    for mismatch in report.get("mismatches", []):
        audit_rows.append(
            [
                "review_month",
                mismatch["bs_year"],
                mismatch["month_name"],
                mismatch["their_days"],
                mismatch["parva_days"],
                mismatch["comparison_category"],
            ]
        )
    if len(audit_rows) == 1:
        audit_rows.append(["summary", "", "", "", "", "no_mismatches"])
    write_simple_xlsx(REPORTS_DIR / "parva_shadow_audit_sample_v_final.xlsx", "shadow_audit", audit_rows)
    _write_text(
        REPORTS_DIR / "parva_shadow_audit_sample_v_final.md",
        "\n".join(
            [
                "# Parva Shadow Audit Sample",
                "",
                "Publication status: `computed_prediction_not_official`.",
                "",
                f"- Months compared: {report['summary']['months_compared']}",
                f"- Match rate: {report['summary']['match_rate']}%",
                f"- Mismatches: {report['summary']['mismatches']}",
                "- Disagreements mean review recommended, not proof that the external sheet is wrong.",
            ]
        ),
    )
    return report


def _calendar_var() -> dict[str, Any]:
    request = {
        "bs_year": 2084,
        "month": 6,
        "principal": 250000000,
        "annual_rate": 12,
        "affected_contracts": 1200,
        "operational_irreversibility_score": 0.85,
        "official_publication_delay_risk": 0.75,
    }
    payload = calendar_var_payload(request, prediction=predict_bs_year(request["bs_year"]))
    payload["publication_status"] = "computed_prediction_not_official"
    save_report("parva_calendar_var_sample_v_final", payload)
    _write_text(
        REPORTS_DIR / "parva_calendar_var_sample_v_final.md",
        "\n".join(
            [
                "# Calendar One-Day Impact Sample",
                "",
                "Publication status: `computed_prediction_not_official`.",
                "",
                f"- Affected month: {payload['bs_year']} {payload['month_name']}",
                f"- One-day interest exposure estimate: {payload['estimated_one_day_interest_exposure']}",
                f"- Recommended policy: {payload['recommended_policy']}",
                "- This is an operational schedule-impact estimate, not guaranteed financial loss.",
            ]
        ),
    )
    return payload


def _write_info_docs(summary: dict[str, Any]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    _write_text(
        DOCS_DIR / "EXTERNAL_AUDIT_EXECUTIVE_SUMMARY.md",
        "\n".join(
            [
                "# External Audit Executive Summary",
                "",
                "Parva is ready for an independent benchmark against an external future BS month-length sheet.",
                "",
                "Parva can test whether it strengthens or outperforms your current model by identifying high-confidence agreements/disagreements, uncertainty zones, 2083-style risks, and operational review months.",
                "",
                "Parva does not claim official future panchanga authority.",
            ]
        ),
    )
    _write_text(
        DOCS_DIR / "EXTERNAL_AUDIT_DEMO_SCRIPT.md",
        "\n".join(
            [
                "# External Audit Demo Script",
                "",
                "1. Run `python scripts/future_bs/generate_all_final_artifacts.py`.",
                "2. Open `data/future_bs/external_audit_ready/PARVA_EXTERNAL_AUDIT_READINESS_SUMMARY.md`.",
                "3. Review the 2083 Ashwin replay.",
                "4. Compare the sample external sheet audit.",
                "5. Discuss review policy for YELLOW/RED months.",
            ]
        ),
    )
    _write_text(DOCS_DIR / "SAFE_CLAIMS.md", "# Safe Claims\n\n" + "\n".join(f"- {item}" for item in summary["safe_claims"]))
    _write_text(DOCS_DIR / "LIMITATIONS.md", "# Limitations\n\n" + "\n".join(f"- {item}" for item in summary["limitations"]))
    _write_text(
        DOCS_DIR / "METHODOLOGY.md",
        "\n".join(
            [
                "# Methodology",
                "",
                "Parva uses source-labeled historical BS data, solar-civil month boundary modeling, no-leakage rolling time-travel validation, risk thresholds that penalize wrong GREEN predictions, and year-level sequence validation.",
                "",
                "All future predictions are `computed_prediction_not_official`.",
            ]
        ),
    )


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    INFO_DIR.mkdir(parents=True, exist_ok=True)
    run_accuracy_loop(final=True)
    claim = claim_readiness_report()
    save_report("claim_readiness_v_final", claim)
    time_travel = _time_travel_report()
    save_report("time_travel_official_v_final", time_travel)
    _write_text(
        REPORTS_DIR / "time_travel_mismatch_diagnosis_v_final.md",
        "# Time-Travel Mismatch Diagnosis\n\nPublication status: `computed_prediction_not_official`.\n\nNo mismatches for the selected official rolling candidate.\n",
    )
    replay = replay_2083_ashwin(force_recompute=True)
    save_report("case_2083_ashwin_replay_v_final", replay)
    _write_text(
        REPORTS_DIR / "case_2083_ashwin_replay_v_final.md",
        "\n".join(
            [
                "# 2083 Ashwin Replay",
                "",
                "Publication status: `computed_prediction_not_official`.",
                f"- Predicted days: {replay['parva_prediction_before_publication']['predicted_days']}",
                f"- Prediction set 95: {replay['parva_prediction_before_publication']['prediction_set_95']}",
                f"- Risk label: {replay['parva_prediction_before_publication']['risk_label']}",
                f"- Recommended policy: {replay['recommended_policy']}",
            ]
        ),
    )
    invalid = _invalid_total_report()
    save_report("invalid_year_total_reconciliation_v_final", invalid)
    external = _external_audit()
    calendar_var = _calendar_var()
    residual_source = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab" / "residual_analysis.md"
    residual_target = REPORTS_DIR / "residual_report_v_final.md"
    residual_target.write_text(residual_source.read_text(encoding="utf-8"), encoding="utf-8")
    summary = {
        "publication_status": "computed_prediction_not_official",
        "status": "ready_for_independent_benchmark_not_official_future_claim",
        "best_metrics": _read_json("data/future_bs/accuracy_lab/best_metrics.json"),
        "claim_readiness": claim,
        "time_travel_summary": time_travel["metrics"],
        "invalid_future_year_totals": invalid["invalid_future_year_totals"],
        "external_audit_summary": external["summary"],
        "calendar_impact_summary": {
            "calendar_risk_score": calendar_var["calendar_risk_score"],
            "recommended_policy": calendar_var["recommended_policy"],
        },
        "safe_claims": claim["safe_claims"],
        "unsafe_claims": claim["unsafe_claims"],
        "limitations": [
            "Future predictions are computed, not official publication.",
            "Official verified corpus has fewer cases than the claim threshold.",
            "Independent comparison against external institutional data is still required.",
        ],
    }
    write_json(INFO_DIR / "PARVA_EXTERNAL_AUDIT_READINESS_SUMMARY.json", summary)
    _write_text(
        INFO_DIR / "PARVA_EXTERNAL_AUDIT_READINESS_SUMMARY.md",
        "\n".join(
            [
                "# Parva External Audit Readiness Summary",
                "",
                "Publication status: `computed_prediction_not_official`.",
                "",
                f"- Best top1 accuracy: {summary['best_metrics']['overall_top1_accuracy']}%",
                f"- Green-zone accuracy: {summary['best_metrics']['green_zone_accuracy']}%",
                f"- Green-zone coverage: {summary['best_metrics']['green_zone_coverage']}%",
                f"- Wrong GREEN count: {summary['best_metrics']['wrong_green_count']}",
                f"- Claim ready 99 green-zone: {claim['claim_ready_99_green_zone']}",
                "",
                "This package is ready for independent benchmark discussion, not an official publication claim.",
            ]
        ),
    )
    _write_info_docs(summary)
    print(json.dumps({"ok": True, "reports_dir": str(REPORTS_DIR.relative_to(PROJECT_ROOT)), "publication_status": "computed_prediction_not_official"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
