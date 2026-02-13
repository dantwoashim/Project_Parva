#!/usr/bin/env python3
"""Precompute yearly festival date artifacts using V2 calculator."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.calculator_v2 import (  # noqa: E402
    calculate_festival_v2,
    list_festivals_v2,
)


OUT_DIR = PROJECT_ROOT / "output" / "precomputed"


def precompute_year(year: int, festival_ids: list[str]) -> Path:
    rows = []
    for festival_id in festival_ids:
        result = calculate_festival_v2(festival_id, year)
        if result is None:
            continue
        rows.append(
            {
                "festival_id": festival_id,
                "start": result.start_date.isoformat(),
                "end": result.end_date.isoformat(),
                "duration_days": result.duration_days,
                "method": result.method,
                "lunar_month": result.lunar_month,
                "is_adhik_year": result.is_adhik_year,
            }
        )

    rows.sort(key=lambda item: item["start"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"festivals_{year}.json"
    payload = {
        "year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "festivals": rows,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute festival yearly artifacts")
    parser.add_argument("--start-year", type=int, default=date.today().year)
    parser.add_argument("--end-year", type=int, default=date.today().year + 2)
    parser.add_argument(
        "--festivals",
        default="",
        help="Comma-separated festival ids. Defaults to all v2 festivals.",
    )
    args = parser.parse_args()

    start_year = min(args.start_year, args.end_year)
    end_year = max(args.start_year, args.end_year)
    festival_ids = [f.strip() for f in args.festivals.split(",") if f.strip()] or list_festivals_v2()

    for year in range(start_year, end_year + 1):
        out = precompute_year(year, festival_ids)
        print(f"Wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
