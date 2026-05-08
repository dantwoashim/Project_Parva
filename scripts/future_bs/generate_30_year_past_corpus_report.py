#!/usr/bin/env python3
"""Materialize the 30+ past-year Tier 1-4 reconstruction slice."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs import data_acquisition as da  # noqa: E402

OUT_CSV = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "reconstructed_30_past_year_month_lengths.csv"
OUT_JSON = PROJECT_ROOT / "data" / "future_bs" / "data_acquisition" / "thirty_year_past_reconstruction_report.json"
OUT_MD = PROJECT_ROOT / "data" / "future_bs" / "data_acquisition" / "thirty_year_past_reconstruction_report.md"


def main() -> int:
    metrics = da.coverage_metrics()
    years = [int(year) for year in metrics["medium_high_past_years_with_12_months_list"]]
    if len(years) < 30:
        raise SystemExit(f"30-year past reconstruction target not met: only {len(years)} years")

    length_rows = da.read_csv(da.CORPUS_DIR / "reconstructed_month_lengths.csv")
    selected = [
        row
        for row in length_rows
        if int(row["bs_year"]) in years and int(row["best_source_tier"]) <= 4
    ]
    selected_years = sorted({int(row["bs_year"]) for row in selected})
    if len(selected_years) < 30:
        raise SystemExit(f"30-year output slice target not met: only {len(selected_years)} years")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=da.MONTH_LENGTH_FIELDS)
        writer.writeheader()
        writer.writerows(selected)

    tier_counts = Counter(row["best_source_tier"] for row in selected)
    status_counts = Counter(row["verification_status"] for row in selected)
    payload = {
        "publication_status": da.PUBLICATION_STATUS,
        "target": "30+ past BS years with complete Tier 1-4 reconstructed month-length support",
        "target_met": True,
        "year_count": len(selected_years),
        "years": selected_years,
        "month_rows": len(selected),
        "source_tier_scope": "Tier 1-4 only",
        "best_tier_distribution": dict(sorted(tier_counts.items())),
        "verification_status_distribution": dict(sorted(status_counts.items())),
        "official_claim_note": (
            "This is not a Tier 1/Tier 2-only corpus and must not be used as official_strict claim-readiness."
        ),
        "output_csv": str(OUT_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 30+ Past-Year Reconstruction Report",
        "",
        f"Publication status: `{da.PUBLICATION_STATUS}`",
        "",
        f"- Target met: {str(payload['target_met']).lower()}",
        f"- Past BS years reconstructed: {payload['year_count']}",
        f"- Month rows in 30-year slice: {payload['month_rows']}",
        f"- Years: {', '.join(str(year) for year in selected_years)}",
        f"- Best-tier distribution: {json.dumps(payload['best_tier_distribution'], sort_keys=True)}",
        f"- Verification-status distribution: {json.dumps(payload['verification_status_distribution'], sort_keys=True)}",
        "",
        "This slice is Tier 1-4 source-labeled reconstruction, not official-only proof.",
        "Tier 4 publisher-reference rows remain useful for modeling, disagreement targeting, and active learning, but not for official claim-readiness.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
