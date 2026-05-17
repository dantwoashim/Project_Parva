"""Enterprise calendar helpers for financial-system evaluation."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_confidence,
    gregorian_to_bs,
)
from app.calendar.fiscal import fiscal_year_label
from app.calendar.provenance import (
    ARCHIVED_RAW_OFFICIAL_RANGE_LABEL,
    STATIC_LOOKUP_RANGE_LABEL,
    STRUCTURED_OFFICIAL_RANGE_LABEL,
    get_bs_year_provenance,
)
from app.core.source_metadata import build_bs_claim_meta
from app.policy import get_policy_metadata
from app.services.bs_month_metadata_service import BsMonthCalculationMode, build_bs_month_metadata

ENGINE_FISCAL_YEAR = "parva_enterprise_fiscal_year_v1"
SOURCE_RANGE = STATIC_LOOKUP_RANGE_LABEL
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
    provenance = get_bs_year_provenance(bs_year)
    if provenance.confidence == "official":
        return "official_lookup", provenance.source_range
    if provenance.confidence == "static_lookup":
        return "static_lookup_unverified", provenance.source_range
    return "estimated", None


def _derived_confidence_for_bs_year(bs_year: int) -> str:
    confidence, _ = _confidence_for_bs_year(bs_year)
    if confidence == "official_lookup":
        return "derived_from_official_lookup"
    if confidence == "static_lookup_unverified":
        return "derived_from_static_lookup_unverified"
    return "estimated"


def _confidence_for_ad_date(ad_date: date) -> tuple[str, str | None]:
    confidence = get_bs_confidence(ad_date)
    if confidence == "official":
        bs_year, _, _ = gregorian_to_bs(ad_date)
        return "official_lookup", get_bs_year_provenance(bs_year).source_range
    if confidence == "static_lookup":
        bs_year, _, _ = gregorian_to_bs(ad_date)
        return "static_lookup_unverified", get_bs_year_provenance(bs_year).source_range
    return "estimated", None


def _provenance_payload(bs_year: int) -> dict[str, Any]:
    provenance = get_bs_year_provenance(bs_year)
    return {
        "source_status": provenance.source_status,
        "official_structured_range": STRUCTURED_OFFICIAL_RANGE_LABEL,
        "archived_raw_official_range": ARCHIVED_RAW_OFFICIAL_RANGE_LABEL,
        "static_lookup_range": STATIC_LOOKUP_RANGE_LABEL,
        "provenance_note": provenance.note,
    }


def _claim_meta_for_year(
    bs_year: int,
    *,
    trace_id: str | None,
    result_class: str,
) -> dict[str, Any]:
    return build_bs_claim_meta(bs_year, trace_id=trace_id, result_class=result_class)


def _bulk_claim_meta(
    *,
    mode: str,
    dates: list[str],
    results: list[dict[str, Any]],
    trace_id: str | None,
    result_class: str,
) -> dict[str, Any]:
    bs_year = 0
    try:
        first_success = next((row for row in results if row.get("success")), None)
        if first_success and mode == "ad_to_bs":
            bs_year = parse_bs_date(str(first_success["output"]))[0]
        elif first_success and mode == "bs_to_ad":
            bs_year = parse_bs_date(str(first_success["input"]))[0]
        elif dates and mode == "bs_to_ad":
            bs_year = parse_bs_date(str(dates[0]))[0]
    except (KeyError, StopIteration, TypeError, ValueError):
        bs_year = 0
    return _claim_meta_for_year(bs_year, trace_id=trace_id, result_class=result_class)


def fiscal_year_payload(bs_year: int, *, trace_id: str | None = None) -> dict[str, Any]:
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
        "confidence": _derived_confidence_for_bs_year(bs_year),
        "source_range": _confidence_for_bs_year(bs_year)[1],
        **_provenance_payload(bs_year),
        "engine": ENGINE_FISCAL_YEAR,
        "policy": get_policy_metadata(),
        "meta": _claim_meta_for_year(bs_year, trace_id=trace_id, result_class="fiscal_year"),
    }


def bs_months_payload(
    bs_year: int,
    *,
    trace_id: str | None = None,
    mode: BsMonthCalculationMode = "solar_civil",
) -> dict[str, Any]:
    metadata = build_bs_month_metadata(bs_year, mode=mode)
    months = metadata["months"]
    provenance = _provenance_payload(bs_year)
    if mode == "solar_civil":
        provenance = {
            **provenance,
            "source_status": metadata["source_status"],
            "provenance_note": metadata["provenance_note"],
        }
    return {
        "bs_year": bs_year,
        "months": months,
        "total_days": metadata["total_days"],
        "calculation_mode": metadata["calculation_mode"],
        "engine": metadata["engine"],
        "confidence": metadata.get("confidence", _confidence_for_bs_year(bs_year)[0]),
        "source_range": metadata.get("source_range", _confidence_for_bs_year(bs_year)[1]),
        "compatibility_mode": metadata.get("compatibility_mode"),
        "not_authority": True,
        **provenance,
        "policy": get_policy_metadata(),
        "meta": _claim_meta_for_year(bs_year, trace_id=trace_id, result_class="bs_month_metadata"),
    }


def business_days_payload(
    *,
    start_bs: str,
    end_bs: str,
    weekend: str = "saturday",
    include_start: bool = True,
    include_end: bool = True,
    holiday_policy: str = "none",
    trace_id: str | None = None,
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
        "confidence": _derived_confidence_for_bs_year(start_tuple[0]),
        **_provenance_payload(start_tuple[0]),
        "policy": get_policy_metadata(),
        "meta": _claim_meta_for_year(
            start_tuple[0],
            trace_id=trace_id,
            result_class="business_day_count",
        ),
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


def bulk_convert_payload(mode: str, dates: list[str], *, trace_id: str | None = None) -> dict[str, Any]:
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
        "policy": get_policy_metadata(),
        "meta": _bulk_claim_meta(
            mode=mode,
            dates=dates,
            results=results,
            trace_id=trace_id,
            result_class="bulk_conversion",
        ),
    }


def validate_cases_payload(cases: list[dict[str, Any]], *, trace_id: str | None = None) -> dict[str, Any]:
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
        "policy": get_policy_metadata(),
        "meta": _claim_meta_for_year(0, trace_id=trace_id, result_class="validation_suite"),
    }


def capabilities_payload(*, trace_id: str | None = None) -> dict[str, Any]:
    return {
        "surface": "enterprise_calendar",
        "status": "evaluation_ready",
        "publication_status": "computed_prediction_not_official",
        "stable": [
            "bs_to_ad",
            "ad_to_bs",
            "bs_month_lengths",
            "fiscal_year_boundaries",
            "bulk_conversion",
            "validation_suite",
            "compliance_profile_preview",
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
        "source_provenance": {
            "official_structured_range": STRUCTURED_OFFICIAL_RANGE_LABEL,
            "archived_raw_official_range": ARCHIVED_RAW_OFFICIAL_RANGE_LABEL,
            "static_lookup_range": STATIC_LOOKUP_RANGE_LABEL,
            "official_2070_2095_bundle_available": False,
            "note": (
                "The static lookup table covers 2070-2095 BS, but only "
                "2078-2083 BS currently has structured official source backing."
            ),
        },
        "policy": get_policy_metadata(),
        "meta": _claim_meta_for_year(2078, trace_id=trace_id, result_class="enterprise_capabilities"),
    }


__all__ = [
    "business_days_payload",
    "bulk_convert_payload",
    "bs_months_payload",
    "capabilities_payload",
    "fiscal_year_payload",
    "validate_cases_payload",
]
