#!/usr/bin/env python3
"""Generate deterministic shared proof fixtures for backend and local-kernel tests."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from app.calendar.panchanga import get_panchanga
from app.membranes.capsule import (
    build_ad_to_bs_capsule,
    build_bs_months_capsule,
    build_convert_bs_to_ad_capsule,
    build_fiscal_year_capsule,
    build_holiday_capsule,
    build_validate_bs_date_capsule,
    build_working_day_capsule,
)
from app.panchanga.proof import build_panchanga_summary_capsule

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "proof"
EPHEMERIS_FIXTURE_ROOT = PROJECT_ROOT / "data" / "ephemeris" / "fixtures"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fixture(name: str, membrane: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_version": "parva-proof-fixture-v1",
        "name": name,
        "operation": membrane["canonical_query"]["operation"],
        "expected_verification_result": {"verified": True, "reason": "verified"},
        "expected_replay_result": membrane["result"],
        "membrane": membrane,
    }


def _write_civil_fixtures() -> None:
    cases = {
        "bs_to_ad_valid": build_convert_bs_to_ad_capsule(2082, 1, 1),
        "bs_to_ad_asar_end": build_convert_bs_to_ad_capsule(2082, 3, 32),
        "bs_to_ad_shrawan_end": build_convert_bs_to_ad_capsule(2082, 4, 31),
        "ad_to_bs_valid": build_ad_to_bs_capsule(date(2025, 4, 14)),
        "ad_to_bs_asar_end": build_ad_to_bs_capsule(date(2025, 7, 16)),
        "ad_to_bs_shrawan_end": build_ad_to_bs_capsule(date(2025, 8, 16)),
        "validate_bs_date_valid": build_validate_bs_date_capsule(2082, 1, 1),
        "validate_bs_date_invalid": build_validate_bs_date_capsule(2082, 1, 32),
        "validate_bs_shrawan_32_invalid": build_validate_bs_date_capsule(2082, 4, 32),
        "holiday_membership": build_holiday_capsule(2082, 1, 1),
        "holiday_non_membership": build_holiday_capsule(2082, 1, 2),
        "working_day_true": build_working_day_capsule(2082, 1, 2),
        "working_day_false": build_working_day_capsule(2082, 1, 6),
        "fiscal_year_boundary": build_fiscal_year_capsule(2082),
        "bs_months_canonical": build_bs_months_capsule(2082),
        "bs_months_static_lookup": build_bs_months_capsule(2082, mode="static_lookup"),
        "bs_months_compare": build_bs_months_capsule(2082, mode="compare"),
    }
    for name, membrane in cases.items():
        _write_json(FIXTURE_ROOT / "civil" / f"{name}.json", _fixture(name, membrane))


def _write_panchanga_fixtures() -> None:
    fixture_id = "kathmandu_2025_04_14_lahiri"
    target_date = date(2025, 4, 14)
    raw = get_panchanga(target_date, latitude=27.7172, longitude=85.3240, timezone_name="Asia/Kathmandu")
    _write_json(
        EPHEMERIS_FIXTURE_ROOT / f"{fixture_id}.json",
        {
            "fixture_id": fixture_id,
            "ephemeris_name": "Swiss/Moshier pinned Panchanga fixture slice",
            "ephemeris_version": "fixture-v1",
            "time_scale": "UTC",
            "coordinate_frame": "sidereal",
            "precision_tolerance": "exact pinned fixture replay",
            "supported_date_range": "2025-04-14 only",
            "jpl_fixture": False,
            "query": {
                "date": target_date.isoformat(),
                "latitude": 27.7172,
                "longitude": 85.324,
                "timezone": "Asia/Kathmandu",
                "ayanamsa": "lahiri",
            },
            "panchanga": raw,
        },
    )
    membrane = build_panchanga_summary_capsule(
        target_date,
        latitude=27.7172,
        longitude=85.3240,
        timezone_name="Asia/Kathmandu",
        provider_id="pinned_panchanga_fixture",
        fixture_id=fixture_id,
        ayanamsa="lahiri",
    )
    _write_json(FIXTURE_ROOT / "panchanga" / "summary_kathmandu_2025_04_14.json", _fixture("summary_kathmandu_2025_04_14", membrane))


def main() -> int:
    _write_civil_fixtures()
    _write_panchanga_fixtures()
    print(f"Wrote proof fixtures under {FIXTURE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
