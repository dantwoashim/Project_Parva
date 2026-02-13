#!/usr/bin/env python3
"""Generate official-vs-estimated BS overlap fixture and report."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    gregorian_to_bs_estimated,
    gregorian_to_bs_official,
)
from app.calendar.constants import BS_CALENDAR_DATA, BS_MAX_YEAR, BS_MIN_YEAR


@dataclass
class Row:
    gregorian: str
    official_bs: str
    estimated_bs: str
    match: bool
    delta_days: int | None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "bs_overlap_comparison.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "BS_OVERLAP_REPORT.md"


def official_range() -> tuple[date, date]:
    min_start = BS_CALENDAR_DATA[BS_MIN_YEAR][1]
    max_lengths, max_start = BS_CALENDAR_DATA[BS_MAX_YEAR]
    max_end = max_start + timedelta(days=sum(max_lengths) - 1)
    return min_start, max_end


def fmt_bs(bs: tuple[int, int, int]) -> str:
    return f"{bs[0]:04d}-{bs[1]:02d}-{bs[2]:02d}"


def compute_rows() -> tuple[list[Row], dict[int, dict[str, float | int]]]:
    start, end = official_range()
    rows: list[Row] = []
    by_year: dict[int, dict[str, float | int]] = {}

    current = start
    while current <= end:
        official = gregorian_to_bs_official(current)
        estimated = gregorian_to_bs_estimated(current)
        match = official == estimated

        delta_days: int | None = None
        try:
            estimated_back = bs_to_gregorian(*estimated)
            delta_days = (estimated_back - current).days
        except Exception:
            delta_days = None

        rows.append(
            Row(
                gregorian=current.isoformat(),
                official_bs=fmt_bs(official),
                estimated_bs=fmt_bs(estimated),
                match=match,
                delta_days=delta_days,
            )
        )

        by = by_year.setdefault(official[0], {"total": 0, "matches": 0, "mismatches": 0})
        by["total"] += 1
        if match:
            by["matches"] += 1
        else:
            by["mismatches"] += 1

        current += timedelta(days=1)

    for stats in by_year.values():
        total = int(stats["total"])
        stats["match_rate"] = round((int(stats["matches"]) / total) * 100.0, 4)

    return rows, by_year


def build_fixture(rows: list[Row], by_year: dict[int, dict[str, float | int]]) -> dict:
    total = len(rows)
    matches = sum(1 for r in rows if r.match)
    mismatches = total - matches
    deltas = [abs(r.delta_days) for r in rows if r.delta_days is not None]

    start, end = official_range()

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "official_bs_range": f"{BS_MIN_YEAR}-{BS_MAX_YEAR}",
            "gregorian_start": start.isoformat(),
            "gregorian_end": end.isoformat(),
            "total_days": total,
            "matches": matches,
            "mismatches": mismatches,
            "match_rate": round((matches / total) * 100.0, 4),
            "abs_delta_days_avg": round(mean(deltas), 4) if deltas else 0.0,
            "abs_delta_days_max": max(deltas) if deltas else 0,
        },
        "summary_by_bs_year": [
            {
                "bs_year": year,
                "total": int(stats["total"]),
                "matches": int(stats["matches"]),
                "mismatches": int(stats["mismatches"]),
                "match_rate": stats["match_rate"],
            }
            for year, stats in sorted(by_year.items())
        ],
        "rows": [
            {
                "gregorian": r.gregorian,
                "official_bs": r.official_bs,
                "estimated_bs": r.estimated_bs,
                "match": r.match,
                "delta_days": r.delta_days,
            }
            for r in rows
        ],
    }


def write_report(fixture: dict) -> None:
    meta = fixture["metadata"]
    rows = fixture["rows"]
    mismatches = [r for r in rows if not r["match"]]

    lines = [
        "# BS Overlap Report (Official vs Estimated)",
        "",
        "This report compares sankranti-based estimated conversion against the official lookup table",
        "for every day inside the official overlap window.",
        "",
        f"- Official range: `{meta['official_bs_range']} BS`",
        f"- Gregorian overlap: `{meta['gregorian_start']}` to `{meta['gregorian_end']}`",
        f"- Days compared: **{meta['total_days']}**",
        f"- Matches: **{meta['matches']}**",
        f"- Mismatches: **{meta['mismatches']}**",
        f"- Match rate: **{meta['match_rate']}%**",
        "",
        "## Interpretation",
        "",
        "- Official conversion remains authoritative in-table.",
        "- Estimated mode is useful for long-range extrapolation but not identical to committee tables.",
        "- API confidence must therefore stay explicit: `official` in-range, `estimated` out-of-range.",
        "",
        "## First 20 Mismatches",
        "",
        "| Gregorian | Official BS | Estimated BS | Delta Days |",
        "|---|---|---|---|",
    ]

    for row in mismatches[:20]:
        lines.append(
            f"| {row['gregorian']} | {row['official_bs']} | {row['estimated_bs']} | {row['delta_days']} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- `delta_days` is measured by converting the estimated BS back to Gregorian and comparing with input date.",
        "- Use this file together with `tests/fixtures/bs_overlap_comparison.json` in regression and contract docs.",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, by_year = compute_rows()
    fixture = build_fixture(rows, by_year)

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_report(fixture)

    print(f"Wrote {FIXTURE_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
