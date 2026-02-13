#!/usr/bin/env python3
"""Precompute daily panchanga payloads into yearly JSON artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta, timezone, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.bikram_sambat import (  # noqa: E402
    get_bs_confidence,
    get_bs_estimated_error_days,
    get_bs_month_name,
    get_bs_source_range,
    gregorian_to_bs,
)
from app.calendar.panchanga import get_panchanga  # noqa: E402
from app.provenance import get_provenance_payload  # noqa: E402
from app.uncertainty import build_bs_uncertainty, build_panchanga_uncertainty  # noqa: E402


OUT_DIR = PROJECT_ROOT / "output" / "precomputed"


def _build_panchanga_response(target_date: date) -> dict:
    panchanga = get_panchanga(target_date)
    bs_year, bs_month, bs_day = gregorian_to_bs(target_date)
    confidence = get_bs_confidence(target_date)
    estimated_error = get_bs_estimated_error_days(target_date)

    return {
        "date": target_date.isoformat(),
        "bikram_sambat": {
            "year": bs_year,
            "month": bs_month,
            "day": bs_day,
            "month_name": get_bs_month_name(bs_month),
            "confidence": confidence,
            "source_range": get_bs_source_range(target_date),
            "estimated_error_days": estimated_error,
            "uncertainty": build_bs_uncertainty(confidence, estimated_error),
        },
        "panchanga": {
            "confidence": "astronomical",
            "uncertainty": build_panchanga_uncertainty(),
            "tithi": {
                "number": panchanga["tithi"]["number"],
                "name": panchanga["tithi"]["name"],
                "paksha": panchanga["tithi"]["paksha"],
                "progress": panchanga["tithi"]["progress"],
                "method": "ephemeris_udaya",
                "confidence": "exact",
                "reference_time": "sunrise",
                "sunrise_used": panchanga["sunrise"]["local"],
            },
            "nakshatra": {
                "number": panchanga["nakshatra"]["number"],
                "name": panchanga["nakshatra"]["name"],
                "pada": panchanga["nakshatra"].get("pada", 1),
            },
            "yoga": {
                "number": panchanga["yoga"]["number"],
                "name": panchanga["yoga"]["name"],
            },
            "karana": {
                "number": panchanga["karana"]["number"],
                "name": panchanga["karana"]["name"],
            },
            "vaara": {
                "name_sanskrit": panchanga["vaara"]["name_sanskrit"],
                "name_english": panchanga["vaara"]["name_english"],
            },
        },
        "ephemeris": {
            "mode": panchanga.get("mode", "swiss_moshier"),
            "accuracy": panchanga.get("accuracy", "arcsecond"),
            "library": panchanga.get("library", "pyswisseph"),
        },
        "engine_version": "v2",
        "provenance": get_provenance_payload(verify_url="/v2/api/provenance/root", create_if_missing=True),
    }


def precompute_year(year: int) -> Path:
    start = date(year, 1, 1)
    end = date(year + 1, 1, 1)

    entries: dict[str, dict] = {}
    d = start
    while d < end:
        entries[d.isoformat()] = _build_panchanga_response(d)
        d += timedelta(days=1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"panchanga_{year}.json"
    payload = {
        "year": year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "dates": entries,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute panchanga yearly artifacts")
    parser.add_argument("--start-year", type=int, default=date.today().year)
    parser.add_argument("--end-year", type=int, default=date.today().year + 2)
    args = parser.parse_args()

    start_year = min(args.start_year, args.end_year)
    end_year = max(args.start_year, args.end_year)

    for year in range(start_year, end_year + 1):
        out = precompute_year(year)
        print(f"Wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
