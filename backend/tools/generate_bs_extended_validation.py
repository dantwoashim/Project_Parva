#!/usr/bin/env python3
"""Generate extended-range BS validation samples and report."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    get_bs_confidence,
    get_bs_estimated_error_days,
    gregorian_to_bs,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HIST_PATH = PROJECT_ROOT / "tests" / "fixtures" / "bs_historical.json"
FUT_PATH = PROJECT_ROOT / "tests" / "fixtures" / "bs_future_projection.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "BS_EXTENDED_VALIDATION.md"

HISTORICAL_DATES = [
    date(1900, 1, 1),
    date(1943, 4, 14),
    date(1950, 1, 1),
    date(1975, 6, 15),
    date(2000, 1, 1),
]

FUTURE_DATES = [
    date(2040, 1, 1),
    date(2050, 2, 15),
    date(2080, 8, 1),
    date(2100, 1, 1),
    date(2200, 12, 31),
]


def build_rows(samples: list[date]) -> list[dict]:
    rows = []
    for g in samples:
        bs = gregorian_to_bs(g)
        back = bs_to_gregorian(*bs)
        rows.append(
            {
                "gregorian": g.isoformat(),
                "bs": {"year": bs[0], "month": bs[1], "day": bs[2]},
                "roundtrip_gregorian": back.isoformat(),
                "roundtrip_delta_days": (back - g).days,
                "confidence": get_bs_confidence(g),
                "estimated_error_days": get_bs_estimated_error_days(g),
            }
        )
    return rows


def main() -> None:
    historical = {
        "metadata": {
            "description": "Historical sample conversions for extended estimated mode",
            "note": "These are diagnostic samples, not official lookup truth outside 2070-2095 BS.",
        },
        "samples": build_rows(HISTORICAL_DATES),
    }

    future = {
        "metadata": {
            "description": "Future sample conversions for extended estimated mode",
            "note": "Use confidence field to distinguish official vs estimated outputs.",
        },
        "samples": build_rows(FUTURE_DATES),
    }

    HIST_PATH.write_text(json.dumps(historical, ensure_ascii=False, indent=2), encoding="utf-8")
    FUT_PATH.write_text(json.dumps(future, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# BS Extended Range Validation",
        "",
        "This report validates extended-range conversion behavior (diagnostic mode).",
        "",
        "## Historical Samples",
        "",
        "| Gregorian | BS | Roundtrip Δ (days) | Confidence |",
        "|---|---|---:|---|",
    ]
    for row in historical["samples"]:
        bs = row["bs"]
        lines.append(
            f"| {row['gregorian']} | {bs['year']}-{bs['month']:02d}-{bs['day']:02d} | {row['roundtrip_delta_days']} | {row['confidence']} |"
        )

    lines += [
        "",
        "## Future Samples",
        "",
        "| Gregorian | BS | Roundtrip Δ (days) | Confidence |",
        "|---|---|---:|---|",
    ]
    for row in future["samples"]:
        bs = row["bs"]
        lines.append(
            f"| {row['gregorian']} | {bs['year']}-{bs['month']:02d}-{bs['day']:02d} | {row['roundtrip_delta_days']} | {row['confidence']} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- Outside official range, results are intentionally marked `estimated`.",
        "- Roundtrip deltas are expected to be small for estimated-mode consistency checks.",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {HIST_PATH}")
    print(f"Wrote {FUT_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
