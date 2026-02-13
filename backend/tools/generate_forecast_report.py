#!/usr/bin/env python3
"""Generate long-horizon forecast report (Year 3 Week 14-16)."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path

from app.forecast import build_error_curve, forecast_festivals, list_default_forecast_festivals


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate multi-year forecast report")
    parser.add_argument("--start-year", type=int, default=2030)
    parser.add_argument("--end-year", type=int, default=2050)
    parser.add_argument("--out", default="reports/forecast_2030_2050.json")
    parser.add_argument("--out-md", default="reports/forecast_2030_2050.md")
    args = parser.parse_args()

    start_year = min(args.start_year, args.end_year)
    end_year = max(args.start_year, args.end_year)
    festivals = list_default_forecast_festivals()

    rows = []
    for year in range(start_year, end_year + 1):
        rows.extend(item.__dict__ for item in forecast_festivals(year, festivals))

    curve = build_error_curve(start_year, end_year)
    avg_accuracy = round(sum(p["estimated_accuracy"] for p in curve) / len(curve), 4) if curve else 0.0
    near_term = [p for p in curve if p["horizon_years"] <= 5]
    near_term_avg = (
        round(sum(p["estimated_accuracy"] for p in near_term) / len(near_term), 4) if near_term else avg_accuracy
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "range": {"start_year": start_year, "end_year": end_year},
        "festival_count": len(festivals),
        "forecast_rows": len(rows),
        "average_estimated_accuracy": avg_accuracy,
        "near_term_average_accuracy": near_term_avg,
        "error_curve": curve,
        "forecasts": rows,
        "methodology": {
            "type": "confidence_decay",
            "note": "Accuracy decays with forecast horizon; intervals widen for long-range outputs.",
        },
    }

    out = PROJECT_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Forecast Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Horizon: **{start_year}–{end_year}**",
        f"- Festivals per year: **{len(festivals)}**",
        f"- Forecast rows: **{len(rows)}**",
        f"- Average estimated accuracy: **{avg_accuracy}**",
        f"- Near-term (<=5y) average: **{near_term_avg}**",
        "",
        "## Confidence Curve (Sample)",
        "",
        "| Year | Horizon | Estimated Accuracy | CI Days |",
        "|---|---:|---:|---:|",
    ]
    for point in curve[:10]:
        md_lines.append(
            f"| {point['year']} | {point['horizon_years']} | {point['estimated_accuracy']} | {point['confidence_interval_days']} |"
        )
    md_lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Forecast outputs are computed using the v2 festival engine with confidence decay metadata.",
            "- Consumers should use confidence interval and horizon fields for planning UI.",
        ]
    )

    out_md = PROJECT_ROOT / args.out_md
    out_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({"forecast_rows": len(rows), "avg_accuracy": avg_accuracy}, indent=2))
    print(f"Wrote {out}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
