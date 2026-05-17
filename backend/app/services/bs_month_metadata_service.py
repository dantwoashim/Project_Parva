"""BS month metadata service with explicit trust-bounded calculation modes."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from typing import Any, Literal

from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month, get_bs_month_name
from app.calendar.ephemeris.swiss_eph import EphemerisError
from app.calendar.sankranti import compute_bs_month_lengths, get_bs_month_start

BsMonthCalculationMode = Literal["canonical", "solar_civil", "static_lookup", "compare"]

CANONICAL_ENGINE = "bs_month_canonical_policy_v0"
SOLAR_CIVIL_ENGINE = "solar_civil_sankranti_v1"
STATIC_COMPAT_ENGINE = "static_lookup_compatibility_v1"
COMPARE_ENGINE = "bs_month_compare_v1"

BLOCKED_DECISION_USE_CASES = [
    "legal_final_authority",
    "tax_final_authority",
    "payroll_final_authority",
    "banking_contract_authority",
    "government_calendar_publication",
    "panchanga_final_authority",
]


def build_bs_month_metadata(
    bs_year: int,
    *,
    mode: BsMonthCalculationMode = "canonical",
) -> dict[str, Any]:
    if mode == "canonical":
        return _canonical_month_metadata(bs_year)
    if mode == "solar_civil":
        return _solar_civil_month_metadata(bs_year)
    if mode == "static_lookup":
        return _static_lookup_month_metadata(bs_year)
    if mode == "compare":
        return _compare_month_metadata(bs_year)
    raise ValueError("mode must be one of: canonical, solar_civil, static_lookup, compare")


def _canonical_month_metadata(bs_year: int) -> dict[str, Any]:
    selected = deepcopy(_solar_civil_month_metadata(bs_year))
    selected["calculation_mode"] = "canonical"
    selected["selected_mode"] = "solar_civil"
    selected["engine"] = CANONICAL_ENGINE
    selected["confidence"] = "canonical_solar_civil_computed"
    selected["source_status"] = "computed_solar_civil"
    selected["review_required"] = True
    selected["authority"] = "computed_reference_not_authority"
    selected["claim_boundary"] = "computed_solar_civil_not_official_calendar_authority"
    selected["canonical_decision"] = {
        "policy": "phase_00_trust_arrest_v0",
        "selected_mode": "solar_civil",
        "reason": (
            "Static lookup is compatibility/reference data only. Canonical BS month "
            "metadata selects deterministic solar-civil sankranti computation and "
            "keeps all output non-authoritative."
        ),
        "static_lookup_allowed": "explicit_mode_or_compare_branch_only",
    }
    for month in selected["months"]:
        month["calculation_mode"] = "canonical"
        month["selected_mode"] = "solar_civil"
        month["engine"] = CANONICAL_ENGINE
        month["review_required"] = True
        month["authority"] = "computed_reference_not_authority"
    return selected


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
        "review_required": True,
        "authority": "computed_reference_not_authority",
        "claim_boundary": "computed_solar_civil_not_official_calendar_authority",
        "blocked_use_cases": BLOCKED_DECISION_USE_CASES,
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
        "confidence": "static_lookup_unverified",
        "source_range": "2000-2099 BS static lookup table",
        "source_status": "static_reference",
        "authority": "static_reference",
        "review_required": True,
        "claim_boundary": "static_lookup_reference_not_authority",
        "blocked_use_cases": BLOCKED_DECISION_USE_CASES,
        "compatibility_mode": None,
        "provenance_note": (
            "Static lookup is explicit compatibility/reference data. It is not "
            "upgraded into source-backed, official, legal, tax, payroll, banking, "
            "government, or panchanga authority."
        ),
    }


def _compare_month_metadata(bs_year: int) -> dict[str, Any]:
    canonical = _canonical_month_metadata(bs_year)
    solar_civil = _solar_civil_month_metadata(bs_year)
    static_lookup = _static_lookup_month_metadata(bs_year)
    disagreement = solar_civil["total_days"] != static_lookup["total_days"] or [
        row["days"] for row in solar_civil["months"]
    ] != [row["days"] for row in static_lookup["months"]]

    return {
        "calculation_mode": "compare",
        "engine": COMPARE_ENGINE,
        "bs_year": bs_year,
        "branches": {
            "canonical": canonical,
            "solar_civil": solar_civil,
            "static_lookup": static_lookup,
        },
        "default_branch": "canonical",
        "selected_mode": "canonical",
        "disagreement": disagreement,
        "review_required": True,
        "authority": "comparison_reference_not_authority",
        "confidence": "comparison_requires_review",
        "source_status": "multiple_reference_branches",
        "claim_boundary": "compare_mode_not_authority",
        "blocked_use_cases": BLOCKED_DECISION_USE_CASES,
        "provenance_note": (
            "Compare mode is an audit view. Branches are intentionally separate so "
            "static lookup cannot be mistaken for canonical enterprise truth."
        ),
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
        "review_required": calculation_mode == "static_lookup",
        "authority": "static_reference" if calculation_mode == "static_lookup" else "computed_reference_not_authority",
    }
