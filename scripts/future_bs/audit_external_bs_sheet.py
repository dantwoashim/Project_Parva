#!/usr/bin/env python3
"""Generate an external future-BS sheet audit report."""

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

from _report_io import write_simple_pdf, write_simple_xlsx  # noqa: E402
from app.calendar.constants import BS_MONTH_NAMES  # noqa: E402
from app.services.future_bs_service import compare_external_sheet, predict_bs_year  # noqa: E402


def _sample_years(start: int, end: int) -> list[dict[str, object]]:
    years = []
    for year in range(start, end + 1):
        prediction = predict_bs_year(year)
        months = list(prediction["months"])
        if year in {2084, 2091, 2112}:
            months[5] = 30 if months[5] != 30 else 31
        years.append({"bs_year": year, "months": months})
    return years


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--start", type=int, default=2084)
    parser.add_argument("--end", type=int, default=2200)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()

    if not args.sample:
        raise SystemExit("Only --sample generation is supported by the reproducible audit script.")

    external = _sample_years(args.start, args.end)
    report = compare_external_sheet("sample_external_reference_month_lengths", external)
    rows = [
        ["section", "metric", "value"],
        ["executive_summary", "months_compared", report["summary"]["months_compared"]],
        ["executive_summary", "match_rate", report["summary"]["match_rate"]],
        ["executive_summary", "mismatches", report["summary"]["mismatches"]],
    ]
    rows.append(["review_months", "bs_year", "month", "their_days", "parva_days", "class"])
    for mismatch in report["mismatches"][:100]:
        rows.append(
            [
                "review_months",
                mismatch["bs_year"],
                mismatch["month_name"],
                mismatch["their_days"],
                mismatch["parva_days"],
                mismatch["comparison_category"],
            ]
        )
    write_simple_xlsx(args.out, "Parva Shadow Audit", rows)
    if args.pdf:
        lines = [
            "Publication status: computed_prediction_not_official",
            f"Total months compared: {report['summary']['months_compared']}",
            f"Agreement rate: {report['summary']['match_rate']}%",
            f"High confidence disagreements: {report['summary']['category_counts'].get('PARVA_HIGH_CONFIDENCE_DISAGREES', 0)}",
            "Recommended policy: no-break dual schedule until official publication for risky months.",
            "2083 Ashwin replay: use override-ready policy for one-day boundary risk.",
            "Month columns: " + ", ".join(name.lower() for name in BS_MONTH_NAMES),
        ]
        for mismatch in report["mismatches"][:20]:
            lines.append(
                f"{mismatch['bs_year']} {mismatch['month_name']}: external={mismatch['their_days']} parva={mismatch['parva_days']} {mismatch['comparison_category']}"
            )
        write_simple_pdf(args.pdf, "Parva External Sheet Audit", lines)
    sidecar = args.out.with_suffix(".json")
    sidecar.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "pdf": str(args.pdf) if args.pdf else None}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
