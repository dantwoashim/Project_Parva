"""BS month metadata service with solar-civil default and static compatibility mode."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Literal

from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month, get_bs_month_name
from app.calendar.ephemeris.swiss_eph import EphemerisError
from app.calendar.sankranti import compute_bs_month_lengths, get_bs_month_start

BsMonthCalculationMode = Literal["solar_civil", "static_lookup"]

SOLAR_CIVIL_ENGINE = "solar_civil_sankranti_v1"
STATIC_COMPAT_ENGINE = "static_lookup_compatibility_v1"


def build_bs_month_metadata(
    bs_year: int,
    *,
    mode: BsMonthCalculationMode = "solar_civil",
) -> dict[str, Any]:
    if mode == "solar_civil":
        return _solar_civil_month_metadata(bs_year)
    if mode == "static_lookup":
        return _static_lookup_month_metadata(bs_year)
    raise ValueError("mode must be 'solar_civil' or 'static_lookup'")


def _solar_civil_month_metadata(bs_year: int) -> dict[str, Any]:
    try:
        lengths = compute_bs_month_lengths(bs_year)
        starts = [get_bs_month_start(bs_year, month) for month in range(1, 13)]
    except EphemerisError as exc:
        raise ValueError(f"Could not compute solar-civil BS month metadata for {bs_year}.") from exc

    months = [
        _month_payload(
            bs_year=bs_year,
            month=month,
            days=lengths[month - 1],
            start_ad=starts[month - 1],
            calculation_mode="solar_civil",
            engine=SOLAR_CIVIL_ENGINE,
        )
        for month in range(1, 13)
    ]
    return {
        "months": months,
        "total_days": sum(lengths),
        "calculation_mode": "solar_civil",
        "engine": SOLAR_CIVIL_ENGINE,
        "confidence": "solar_civil_computed",
        "source_range": "solar_civil_sankranti_computation",
        "source_status": "computed_solar_civil",
        "compatibility_mode": "static_lookup",
        "provenance_note": (
            "Month lengths are computed from solar-civil sankranti month starts. "
            "This is deterministic astronomical/civil computation, not official authority."
        ),
    }


def _static_lookup_month_metadata(bs_year: int) -> dict[str, Any]:
    months = []
    for month in range(1, 13):
        days = days_in_bs_month(bs_year, month)
        start_ad = bs_to_gregorian(bs_year, month, 1)
        months.append(
            _month_payload(
                bs_year=bs_year,
                month=month,
                days=days,
                start_ad=start_ad,
                calculation_mode="static_lookup",
                engine=STATIC_COMPAT_ENGINE,
            )
        )
    return {
        "months": months,
        "total_days": sum(row["days"] for row in months),
        "calculation_mode": "static_lookup",
        "engine": STATIC_COMPAT_ENGINE,
        "compatibility_mode": None,
    }


def _month_payload(
    *,
    bs_year: int,
    month: int,
    days: int,
    start_ad: date,
    calculation_mode: BsMonthCalculationMode,
    engine: str,
) -> dict[str, Any]:
    return {
        "month": month,
        "name": get_bs_month_name(month),
        "days": days,
        "start_ad": start_ad.isoformat(),
        "end_ad": (start_ad + timedelta(days=days - 1)).isoformat(),
        "calculation_mode": calculation_mode,
        "engine": engine,
        "not_authority": True,
    }
