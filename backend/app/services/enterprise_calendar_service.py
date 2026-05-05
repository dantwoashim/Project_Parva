"""Enterprise calendar helpers for financial-system evaluation."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_confidence,
    get_bs_month_name,
    gregorian_to_bs,
)
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR
from app.calendar.fiscal import fiscal_year_label

ENGINE_FISCAL_YEAR = "parva_enterprise_fiscal_year_v1"
SOURCE_RANGE = f"{BS_MIN_YEAR}-{BS_MAX_YEAR} BS"
WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _format_bs(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_bs_date(value: str) -> tuple[int, int, int]:
    try:
        year_raw, month_raw, day_raw = value.split("-")
        year = int(year_raw)
        month = int(month_raw)
        day = int(day_raw)
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"Invalid BS date '{value}'. Use YYYY-MM-DD.") from exc
    if len(year_raw) != 4 or len(month_raw) != 2 or len(day_raw) != 2:
        raise ValueError(f"Invalid BS date '{value}'. Use YYYY-MM-DD.")
    bs_to_gregorian(year, month, day)
    return year, month, day


def parse_ad_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid AD date '{value}'. Use YYYY-MM-DD.") from exc


def _confidence_for_bs_year(bs_year: int) -> tuple[str, str | None]:
    if BS_MIN_YEAR <= bs_year <= BS_MAX_YEAR:
        return "official_lookup", SOURCE_RANGE
    return "estimated", None


def _confidence_for_ad_date(ad_date: date) -> tuple[str, str | None]:
    confidence = get_bs_confidence(ad_date)
    if confidence == "official":
        return "official_lookup", SOURCE_RANGE
    return "estimated", None


def fiscal_year_payload(bs_year: int) -> dict[str, Any]:
    start_bs = (bs_year, 4, 1)
    end_year = bs_year + 1
    end_day = days_in_bs_month(end_year, 3)
    end_bs = (end_year, 3, end_day)
    start_ad = bs_to_gregorian(*start_bs)
    end_ad = bs_to_gregorian(*end_bs)
    return {
        "fiscal_year": fiscal_year_label(bs_year),
        "start": {
            "bs": _format_bs(*start_bs),
            "ad": start_ad.isoformat(),
        },
        "end": {
            "bs": _format_bs(*end_bs),
            "ad": end_ad.isoformat(),
        },
        "basis": "Nepal fiscal year: Shrawan 1 to Ashadh end",
        "confidence": "derived_from_bs_lookup",
        "source_range": SOURCE_RANGE,
        "engine": ENGINE_FISCAL_YEAR,
    }


def bs_months_payload(bs_year: int) -> dict[str, Any]:
    months = [
        {
            "month": month,
            "name": get_bs_month_name(month),
            "days": days_in_bs_month(bs_year, month),
        }
        for month in range(1, 13)
    ]
    return {
        "bs_year": bs_year,
        "months": months,
        "total_days": sum(month["days"] for month in months),
        "confidence": "official_lookup",
        "source_range": SOURCE_RANGE,
    }


def business_days_payload(
    *,
    start_bs: str,
    end_bs: str,
    weekend: str = "saturday",
    include_start: bool = True,
    include_end: bool = True,
    holiday_policy: str = "none",
) -> dict[str, Any]:
    weekend_key = weekend.strip().lower()
    if weekend_key not in WEEKDAY_INDEX:
        raise ValueError("weekend must be one of: " + ", ".join(sorted(WEEKDAY_INDEX)))
    if holiday_policy != "none":
        raise ValueError("Only holiday_policy='none' is available for this evaluation endpoint.")

    start_tuple = parse_bs_date(start_bs)
    end_tuple = parse_bs_date(end_bs)
    start_ad = bs_to_gregorian(*start_tuple)
    end_ad = bs_to_gregorian(*end_tuple)
    if start_ad > end_ad:
        raise ValueError("start_bs must be on or before end_bs.")

    cursor = start_ad + (timedelta(days=0) if include_start else timedelta(days=1))
    final = end_ad - (timedelta(days=0) if include_end else timedelta(days=1))
    weekend_index = WEEKDAY_INDEX[weekend_key]
    calendar_days = 0
    weekend_days = 0
    business_days = 0

    while cursor <= final:
        calendar_days += 1
        if cursor.weekday() == weekend_index:
            weekend_days += 1
        else:
            business_days += 1
        cursor += timedelta(days=1)

    return {
        "start_bs": _format_bs(*start_tuple),
        "end_bs": _format_bs(*end_tuple),
        "start_ad": start_ad.isoformat(),
        "end_ad": end_ad.isoformat(),
        "calendar_days": calendar_days,
        "business_days": business_days,
        "weekend_days": weekend_days,
        "holiday_days": 0,
        "holiday_policy": holiday_policy,
        "note": "Holiday exclusion disabled unless a holiday policy is configured.",
        "confidence": "derived_from_bs_lookup",
    }


def convert_one(mode: str, value: str) -> dict[str, Any]:
    if mode == "ad_to_bs":
        ad_date = parse_ad_date(value)
        bs = gregorian_to_bs(ad_date)
        confidence, source_range = _confidence_for_ad_date(ad_date)
        return {
            "input": value,
            "output": _format_bs(*bs),
            "success": True,
            "confidence": confidence,
            "source_range": source_range,
        }
    if mode == "bs_to_ad":
        bs = parse_bs_date(value)
        ad_date = bs_to_gregorian(*bs)
        confidence, source_range = _confidence_for_bs_year(bs[0])
        return {
            "input": value,
            "output": ad_date.isoformat(),
            "success": True,
            "confidence": confidence,
            "source_range": source_range,
        }
    raise ValueError("mode must be 'ad_to_bs' or 'bs_to_ad'.")


def bulk_convert_payload(mode: str, dates: list[str]) -> dict[str, Any]:
    results = []
    success = 0
    for value in dates:
        try:
            result = convert_one(mode, value)
            success += 1
        except ValueError as exc:
            result = {
                "input": value,
                "output": None,
                "success": False,
                "error": str(exc),
            }
        results.append(result)

    total = len(dates)
    return {
        "mode": mode,
        "total": total,
        "success": success,
        "failed": total - success,
        "results": results,
    }


def validate_cases_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    passed = 0
    failed = 0
    generated_reference = 0

    for case in cases:
        case_id = str(case.get("id") or "")
        case_type = str(case.get("type") or "")
        input_value = str(case.get("input") or "")
        expected_raw = case.get("expected")
        expected = "" if expected_raw is None else str(expected_raw)
        result = {
            "id": case_id,
            "type": case_type,
            "input": input_value,
            "expected": expected,
            "actual": None,
            "passed": False,
            "status": "failed",
        }

        try:
            actual = convert_one(case_type, input_value)["output"]
            result["actual"] = actual
            if expected == "":
                result["passed"] = True
                result["status"] = "generated_reference"
                generated_reference += 1
                passed += 1
            elif expected.upper() == "ERROR":
                result["status"] = "failed"
                result["error"] = "Expected conversion error, but conversion succeeded."
                failed += 1
            elif actual == expected:
                result["passed"] = True
                result["status"] = "passed"
                passed += 1
            else:
                result["status"] = "failed"
                failed += 1
        except ValueError as exc:
            result["error"] = str(exc)
            if expected.upper() == "ERROR":
                result["passed"] = True
                result["status"] = "passed"
                passed += 1
            else:
                result["status"] = "error"
                failed += 1

        results.append(result)

    total = len(cases)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "generated_reference": generated_reference,
        "pass_rate": round((passed / total) * 100.0, 2) if total else 0.0,
        "results": results,
    }


def capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "enterprise_calendar",
        "status": "evaluation_ready",
        "stable": [
            "bs_to_ad",
            "ad_to_bs",
            "bs_month_lengths",
            "fiscal_year_boundaries",
            "bulk_conversion",
            "validation_suite",
        ],
        "experimental": [
            "business_days_weekend_only",
            "holiday_policy_profiles",
        ],
        "recommended_use": [
            "technical validation",
            "regression reference",
            "private deployment evaluation",
        ],
        "not_recommended_without_review": [
            "direct production use in financial systems",
            "legal/tax final authority",
        ],
    }


__all__ = [
    "business_days_payload",
    "bulk_convert_payload",
    "bs_months_payload",
    "capabilities_payload",
    "fiscal_year_payload",
    "validate_cases_payload",
]
