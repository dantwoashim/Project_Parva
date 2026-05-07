#!/usr/bin/env python3
"""Generate a sample Calendar VaR report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
SCRIPT_ROOT = Path(__file__).resolve().parent
for path in (BACKEND_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from _report_io import write_json, write_simple_pdf  # noqa: E402
from app.future_bs.calendar_var import calendar_var_payload  # noqa: E402
from app.services.future_bs_service import predict_bs_year  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    payload = {
        "bs_year": 2084,
        "month": 6,
        "principal": 250000000,
        "annual_rate": 12.0,
        "affected_contracts": 1200,
        "operational_irreversibility_score": 0.85,
        "official_publication_delay_risk": 0.75,
    }
    prediction = predict_bs_year(payload["bs_year"])
    report = calendar_var_payload(payload, prediction=prediction)
    report["publication_status"] = "computed_prediction_not_official"
    if args.json:
        write_json(args.json, report)
    lines = [
        "Publication status: computed_prediction_not_official",
        f"Affected month: {report['bs_year']} {report['month_name']}",
        f"Predicted days: {report['parva_prediction']}",
        f"Mismatch probability: {report['mismatch_probability']}",
        f"Principal: {payload['principal']}",
        f"Annual rate: {payload['annual_rate']}",
        f"Affected contracts: {payload['affected_contracts']}",
        f"One-day interest exposure: {report['estimated_one_day_interest_exposure']}",
        f"Calendar risk score: {report['calendar_risk_score']}",
        f"Recommended policy: {report['recommended_policy']}",
    ]
    lines.extend(f"Stress: {scenario}" for scenario in report["stress_scenarios"])
    write_simple_pdf(args.out, "Parva Calendar VaR", lines)
    print(json.dumps({"ok": True, "out": str(args.out), "json": str(args.json) if args.json else None}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
