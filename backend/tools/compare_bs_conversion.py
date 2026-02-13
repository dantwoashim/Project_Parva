#!/usr/bin/env python3
"""
Compare official (lookup) vs estimated (sankranti-based) BS conversion.

Outputs:
- docs/BS_CONVERSION_COMPARISON.md
- docs/bs_conversion_comparison.csv
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import os
from typing import List, Tuple

from app.calendar.bikram_sambat import (
    gregorian_to_bs_official,
    gregorian_to_bs_estimated,
)
from app.calendar.constants import BS_CALENDAR_DATA, BS_MIN_YEAR, BS_MAX_YEAR


def _official_range() -> Tuple:
    min_start = BS_CALENDAR_DATA[BS_MIN_YEAR][1]
    max_data = BS_CALENDAR_DATA[BS_MAX_YEAR]
    max_end = max_data[1] + timedelta(days=sum(max_data[0]) - 1)
    return (min_start, max_end)


def main() -> None:
    min_start, max_end = _official_range()
    total_days = (max_end - min_start).days + 1

    mismatches: List[Tuple[str, str, str]] = []
    per_year = {}
    matches = 0

    current = min_start
    while current <= max_end:
        off = gregorian_to_bs_official(current)
        est = gregorian_to_bs_estimated(current)
        if off == est:
            matches += 1
        else:
            mismatches.append(
                (current.isoformat(), f"{off[0]}-{off[1]:02d}-{off[2]:02d}", f"{est[0]}-{est[1]:02d}-{est[2]:02d}")
            )
            per_year.setdefault(off[0], 0)
            per_year[off[0]] += 1
        current += timedelta(days=1)

    mismatch_count = len(mismatches)
    match_rate = (matches / total_days) * 100.0

    base_dir = Path(os.environ.get("OUTPUT_DIR", Path(__file__).resolve().parents[2] / "docs"))
    base_dir.mkdir(parents=True, exist_ok=True)
    md_path = base_dir / "BS_CONVERSION_COMPARISON.md"
    csv_path = base_dir / "bs_conversion_comparison.csv"

    # Write CSV
    with csv_path.open("w", encoding="utf-8") as f:
        f.write("gregorian_date,official_bs,estimated_bs,match\n")
        current = min_start
        while current <= max_end:
            off = gregorian_to_bs_official(current)
            est = gregorian_to_bs_estimated(current)
            match = "YES" if off == est else "NO"
            f.write(f"{current.isoformat()},{off[0]}-{off[1]:02d}-{off[2]:02d},{est[0]}-{est[1]:02d}-{est[2]:02d},{match}\n")
            current += timedelta(days=1)

    # Write report
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# BS Conversion Comparison (Official vs Estimated)\n\n")
        f.write(f"**Official lookup range:** {min_start} to {max_end}  \n")
        f.write(f"**Total days compared:** {total_days}  \n")
        f.write(f"**Matches:** {matches}  \n")
        f.write(f"**Mismatches:** {mismatch_count}  \n")
        f.write(f"**Match rate:** {match_rate:.4f}%  \n\n")

        f.write("## Mismatch Summary by BS Year (Official)\n\n")
        if per_year:
            f.write("| BS Year | Mismatches |\n|---|---|\n")
            for year in sorted(per_year.keys()):
                f.write(f"| {year} | {per_year[year]} |\n")
        else:
            f.write("No mismatches detected.\n")

        f.write("\n## First 50 Mismatches\n\n")
        if mismatches:
            f.write("| Gregorian Date | Official BS | Estimated BS |\n|---|---|---|\n")
            for row in mismatches[:50]:
                f.write(f"| {row[0]} | {row[1]} | {row[2]} |\n")
        else:
            f.write("No mismatches detected.\n")

        f.write("\n---\n")
        f.write("Full row-level comparison is available in `docs/bs_conversion_comparison.csv`.\n")


if __name__ == "__main__":
    main()
