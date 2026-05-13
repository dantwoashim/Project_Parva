"""Enterprise temporal compliance decision support."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Any, Literal

from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month, gregorian_to_bs
from app.calendar.fiscal import fiscal_period_for_bs_date
from app.core.source_metadata import (
    COMPLIANCE_BOUNDARY,
    ENTERPRISE_COMPLIANCE_PROFILES,
    build_bs_claim_meta,
    build_claim_meta,
)
from app.policy import get_policy_metadata
from app.services.enterprise_calendar_service import parse_ad_date, parse_bs_date
from app.timegraph.fact_ids import (
    bs_ad_fact_id,
    fiscal_period_fact_id,
    profile_policy_fact_id,
    working_day_fact_id,
)

MAX_WORKING_DAY_SEARCH_DAYS = 370
MAX_ADD_WORKING_DAYS = 366

WEEKDAY_NAMES = (
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
)


@dataclass(frozen=True)
class WeekendPolicy:
    non_working_weekdays: tuple[str, ...]


@dataclass(frozen=True)
class HolidayPolicy:
    source_set: str
    include_public_holidays: bool
    include_optional_holidays: bool
    include_banking_holidays: bool
    support_status: str


@dataclass(frozen=True)
class FiscalPolicy:
    fiscal_year_start: str
    label_format: str


@dataclass(frozen=True)
class RiskPolicy:
    allow_research_preview: bool
    require_official_for_payroll: bool
    require_official_holiday_source: bool
    future_dates_require_review: bool
    unsupported_result_action: str


@dataclass(frozen=True)
class ComplianceProfile:
    profile_id: str
    label: str
    jurisdiction: str
    status: str
    description: str
    weekend_policy: WeekendPolicy
    holiday_policy: HolidayPolicy
    fiscal_policy: FiscalPolicy
    risk_policy: RiskPolicy
    warnings: tuple[str, ...]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "label": self.label,
            "jurisdiction": self.jurisdiction,
            "status": self.status,
            "description": self.description,
            "weekend_policy": asdict(self.weekend_policy),
            "holiday_policy": asdict(self.holiday_policy),
            "fiscal_policy": asdict(self.fiscal_policy),
            "risk_policy": asdict(self.risk_policy),
            "warnings": list(self.warnings),
        }


PROFILES: dict[str, ComplianceProfile] = {
    "nepal_public_general": ComplianceProfile(
        profile_id="nepal_public_general",
        label="Nepal public general",
        jurisdiction="NP",
        status="preview_public_corpus",
        description="General Nepal working-day support using Saturday weekend logic, fixed-date public corpus observances, and Nepali fiscal periods.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY",)),
        holiday_policy=HolidayPolicy(
            source_set="public_corpus",
            include_public_holidays=True,
            include_optional_holidays=False,
            include_banking_holidays=False,
            support_status="fixed_date_public_corpus_only",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=False,
            require_official_holiday_source=False,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("Official holiday publication overrides this public-corpus decision support.",),
    ),
    "nepal_government_general": ComplianceProfile(
        profile_id="nepal_government_general",
        label="Nepal government general",
        jurisdiction="NP",
        status="limited_requires_official_review",
        description="Government-style profile. Weekend logic is available, but official holiday source validation is required for operational decisions.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY",)),
        holiday_policy=HolidayPolicy(
            source_set="official_required_not_bundled",
            include_public_holidays=True,
            include_optional_holidays=False,
            include_banking_holidays=False,
            support_status="official_review_required",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=True,
            require_official_holiday_source=True,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("This profile needs official holiday validation before production use.",),
    ),
    "nepal_banking_general": ComplianceProfile(
        profile_id="nepal_banking_general",
        label="Nepal banking general",
        jurisdiction="NP",
        status="limited_requires_official_review",
        description="Banking-style profile. Public demo data does not include an authoritative banking holiday calendar.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY",)),
        holiday_policy=HolidayPolicy(
            source_set="banking_official_required_not_bundled",
            include_public_holidays=True,
            include_optional_holidays=False,
            include_banking_holidays=True,
            support_status="official_review_required",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=True,
            require_official_holiday_source=True,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("Banking holiday decisions require institution-approved source validation.",),
    ),
    "nepal_private_company_default": ComplianceProfile(
        profile_id="nepal_private_company_default",
        label="Nepal private company default",
        jurisdiction="NP",
        status="preview_public_corpus",
        description="Default private-company support for Saturday weekend logic, basic public corpus observances, and fiscal periods.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY",)),
        holiday_policy=HolidayPolicy(
            source_set="public_corpus",
            include_public_holidays=True,
            include_optional_holidays=False,
            include_banking_holidays=False,
            support_status="fixed_date_public_corpus_only",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=False,
            require_official_holiday_source=False,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("Use an organization-approved holiday policy before payroll finalization.",),
    ),
    "nepal_school_general": ComplianceProfile(
        profile_id="nepal_school_general",
        label="Nepal school general",
        jurisdiction="NP",
        status="limited_requires_review",
        description="School-style profile. Public demo data does not include institution-specific academic closures.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY",)),
        holiday_policy=HolidayPolicy(
            source_set="institution_policy_required_not_bundled",
            include_public_holidays=True,
            include_optional_holidays=True,
            include_banking_holidays=False,
            support_status="institution_review_required",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=True,
            require_official_holiday_source=True,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("School calendars need institution-specific closure rules.",),
    ),
    "custom_demo_company": ComplianceProfile(
        profile_id="custom_demo_company",
        label="Custom demo company",
        jurisdiction="NP",
        status="synthetic_demo",
        description="Synthetic demo profile with Saturday and Sunday weekends for integration testing.",
        weekend_policy=WeekendPolicy(non_working_weekdays=("SATURDAY", "SUNDAY")),
        holiday_policy=HolidayPolicy(
            source_set="fixture_only",
            include_public_holidays=False,
            include_optional_holidays=False,
            include_banking_holidays=False,
            support_status="demo_only",
        ),
        fiscal_policy=FiscalPolicy(fiscal_year_start="BS-04-01", label_format="FY {start_year}/{end_year}"),
        risk_policy=RiskPolicy(
            allow_research_preview=False,
            require_official_for_payroll=False,
            require_official_holiday_source=False,
            future_dates_require_review=True,
            unsupported_result_action="human_review_required",
        ),
        warnings=("Synthetic demo profile. Do not use for real payroll or legal decisions.",),
    ),
}

FIXED_BS_PUBLIC_HOLIDAYS = {
    (1, 1): {
        "holiday_id": "bs-new-year",
        "label": "Nepali New Year",
        "source_status": "public_fixed_date_observance",
    },
    (10, 1): {
        "holiday_id": "maghe-sankranti",
        "label": "Maghe Sankranti",
        "source_status": "public_fixed_date_observance",
    },
}


def list_profiles_payload(*, trace_id: str | None = None) -> dict[str, Any]:
    return {
        "profiles": [profile.to_public_dict() for profile in PROFILES.values()],
        "reason_codes": REASON_CODE_CATALOG,
        "policy": get_policy_metadata(),
        "meta": _compliance_meta(
            trace_id=trace_id,
            confidence="source_backed",
            result_class="compliance_profiles",
            warnings=["profiles_are_decision_support_not_legal_authority"],
        ),
    }


def get_profile_payload(profile_id: str, *, trace_id: str | None = None) -> dict[str, Any]:
    profile = _get_profile(profile_id)
    return {
        "profile": profile.to_public_dict(),
        "reason_codes": REASON_CODE_CATALOG,
        "policy": get_policy_metadata(),
        "meta": _compliance_meta(
            trace_id=trace_id,
            confidence="source_backed",
            result_class="compliance_profile",
            warnings=list(profile.warnings),
        ),
    }


def evaluate_date_payload(
    *,
    profile_id: str,
    bs_date: str | None = None,
    ad_date: str | None = None,
    decision_intent: str = "general",
    trace_id: str | None = None,
) -> dict[str, Any]:
    profile = _get_profile(profile_id)
    normalized = _normalize_date(bs_date=bs_date, ad_date=ad_date)
    decision = _evaluate_normalized(profile, normalized, decision_intent=decision_intent)
    return _decision_payload(
        profile=profile,
        normalized=normalized,
        decision=decision,
        trace_id=trace_id,
        result_class="compliance_date_evaluation",
    )


def next_working_day_payload(
    *,
    profile_id: str,
    bs_date: str | None = None,
    ad_date: str | None = None,
    include_input: bool = False,
    trace_id: str | None = None,
) -> dict[str, Any]:
    return _working_day_search_payload(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        direction=1,
        include_input=include_input,
        trace_id=trace_id,
        result_class="next_working_day",
    )


def previous_working_day_payload(
    *,
    profile_id: str,
    bs_date: str | None = None,
    ad_date: str | None = None,
    include_input: bool = False,
    trace_id: str | None = None,
) -> dict[str, Any]:
    return _working_day_search_payload(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        direction=-1,
        include_input=include_input,
        trace_id=trace_id,
        result_class="previous_working_day",
    )


def add_working_days_payload(
    *,
    profile_id: str,
    working_days: int,
    bs_date: str | None = None,
    ad_date: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    if abs(working_days) > MAX_ADD_WORKING_DAYS:
        raise ValueError(f"working_days must be between -{MAX_ADD_WORKING_DAYS} and {MAX_ADD_WORKING_DAYS}.")
    profile = _get_profile(profile_id)
    start = _normalize_date(bs_date=bs_date, ad_date=ad_date)
    if working_days == 0:
        decision = _evaluate_normalized(profile, start, decision_intent="general")
        return {
            **_decision_payload(
                profile=profile,
                normalized=start,
                decision=decision,
                trace_id=trace_id,
                result_class="add_working_days",
            ),
            "start_date": _date_block(start),
            "working_days_requested": working_days,
            "iterations": 0,
        }

    remaining = abs(working_days)
    direction = 1 if working_days > 0 else -1
    cursor = start["ad_date"]  # type: ignore[index]
    iterations = 0
    while remaining > 0:
        iterations += 1
        if iterations > MAX_WORKING_DAY_SEARCH_DAYS:
            raise ValueError("Working-day search exceeded the supported bounded window.")
        cursor = cursor + timedelta(days=direction)
        candidate = _normalize_date(ad_date=cursor.isoformat(), bs_date=None)
        decision = _evaluate_normalized(profile, candidate, decision_intent="general")
        if decision["is_working_day"] is True:
            remaining -= 1

    return {
        **_decision_payload(
            profile=profile,
            normalized=candidate,
            decision=decision,
            trace_id=trace_id,
            result_class="add_working_days",
        ),
        "start_date": _date_block(start),
        "working_days_requested": working_days,
        "iterations": iterations,
    }


def month_closing_day_payload(
    *,
    profile_id: str,
    bs_year: int,
    bs_month: int,
    trace_id: str | None = None,
) -> dict[str, Any]:
    if bs_month < 1 or bs_month > 12:
        raise ValueError("bs_month must be between 1 and 12.")
    profile = _get_profile(profile_id)
    last_day = days_in_bs_month(bs_year, bs_month)
    last_calendar = _normalize_date(bs_date=_format_bs(bs_year, bs_month, last_day), ad_date=None)

    cursor_day = last_day
    iterations = 0
    while cursor_day >= 1:
        iterations += 1
        candidate = _normalize_date(bs_date=_format_bs(bs_year, bs_month, cursor_day), ad_date=None)
        decision = _evaluate_normalized(profile, candidate, decision_intent="payroll")
        if decision["is_working_day"] is True:
            break
        cursor_day -= 1
    else:
        raise ValueError("No working day found inside the BS month for this profile.")

    return {
        **_decision_payload(
            profile=profile,
            normalized=candidate,
            decision=decision,
            trace_id=trace_id,
            result_class="month_closing_day",
        ),
        "bs_year": bs_year,
        "bs_month": bs_month,
        "last_calendar_day": _date_block(last_calendar),
        "last_working_day": _date_block(candidate),
        "iterations": iterations,
    }


def fiscal_period_payload(
    *,
    profile_id: str,
    bs_date: str | None = None,
    ad_date: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    profile = _get_profile(profile_id)
    normalized = _normalize_date(bs_date=bs_date, ad_date=ad_date)
    period = fiscal_period_for_bs_date(
        int(normalized["bs_year"]),
        int(normalized["bs_month"]),
        int(normalized["bs_day"]),
    )
    decision = _evaluate_normalized(profile, normalized, decision_intent="fiscal")
    return {
        **_decision_payload(
            profile=profile,
            normalized=normalized,
            decision=decision,
            trace_id=trace_id,
            result_class="fiscal_period",
        ),
        "fiscal_period": {
            "fiscal_year_start": period.fiscal_year_start,
            "fiscal_year_end": period.fiscal_year_end,
            "fiscal_year_label": period.fiscal_year_label,
            "fiscal_month": period.fiscal_month,
            "fiscal_quarter": period.fiscal_quarter,
            "basis": "Nepal fiscal year starts on BS Shrawan 1.",
        },
    }


def _working_day_search_payload(
    *,
    profile_id: str,
    bs_date: str | None,
    ad_date: str | None,
    direction: Literal[-1, 1],
    include_input: bool,
    trace_id: str | None,
    result_class: str,
) -> dict[str, Any]:
    profile = _get_profile(profile_id)
    start = _normalize_date(bs_date=bs_date, ad_date=ad_date)
    cursor = start["ad_date"] if include_input else start["ad_date"] + timedelta(days=direction)  # type: ignore[operator]
    iterations = 0
    while iterations <= MAX_WORKING_DAY_SEARCH_DAYS:
        candidate = _normalize_date(ad_date=cursor.isoformat(), bs_date=None)
        decision = _evaluate_normalized(profile, candidate, decision_intent="general")
        if decision["is_working_day"] is True:
            return {
                **_decision_payload(
                    profile=profile,
                    normalized=candidate,
                    decision=decision,
                    trace_id=trace_id,
                    result_class=result_class,
                ),
                "start_date": _date_block(start),
                "iterations": iterations + (0 if include_input else 1),
                "search_window_days": MAX_WORKING_DAY_SEARCH_DAYS,
            }
        iterations += 1
        cursor = cursor + timedelta(days=direction)
    raise ValueError("Working-day search exceeded the supported bounded window.")


def _evaluate_normalized(
    profile: ComplianceProfile,
    normalized: dict[str, Any],
    *,
    decision_intent: str,
) -> dict[str, Any]:
    ad = normalized["ad_date"]
    bs_year = int(normalized["bs_year"])
    bs_month = int(normalized["bs_month"])
    bs_day = int(normalized["bs_day"])
    weekday = WEEKDAY_NAMES[ad.weekday()]
    reason_codes: list[str] = []
    warnings: list[str] = list(profile.warnings)
    review_required = False

    if weekday in profile.weekend_policy.non_working_weekdays:
        reason_codes.append("WEEKEND")
        if weekday == "SATURDAY":
            reason_codes.append("SATURDAY_NON_WORKING")
        is_working_day = False
    else:
        reason_codes.append("WEEKDAY")
        is_working_day = True

    holiday_match = _match_public_holiday(profile, bs_month, bs_day)
    if holiday_match:
        reason_codes.append("PUBLIC_HOLIDAY_MATCH")
        is_working_day = False
    elif profile.holiday_policy.include_public_holidays:
        reason_codes.append("NO_MATCHING_PUBLIC_HOLIDAY")

    if profile.holiday_policy.include_banking_holidays:
        reason_codes.append("BANKING_HOLIDAY_SOURCE_NOT_AVAILABLE")

    source_meta = build_bs_claim_meta(bs_year)
    source_confidence = str(source_meta["confidence"])
    if profile.risk_policy.require_official_for_payroll and source_confidence != "official_verified":
        reason_codes.append("SOURCE_CONFIDENCE_TOO_LOW")
        review_required = True

    if profile.risk_policy.require_official_holiday_source:
        reason_codes.append("PROFILE_REQUIRES_OFFICIAL_SOURCE")
        review_required = True

    if ad > date.today() and profile.risk_policy.future_dates_require_review:
        reason_codes.append("FUTURE_DATE_REVIEW_REQUIRED")
        review_required = True

    if decision_intent == "payroll" and (
        source_confidence != "official_verified" or profile.risk_policy.require_official_holiday_source
    ):
        reason_codes.append("PAYROLL_REVIEW_REQUIRED")
        review_required = True

    fiscal = fiscal_period_for_bs_date(bs_year, bs_month, bs_day)
    if fiscal.fiscal_month == 1 and bs_day == 1:
        reason_codes.append("FISCAL_YEAR_BOUNDARY")

    if holiday_match and holiday_match["source_status"] == "public_fixed_date_observance":
        warnings.append("public_fixed_date_holiday_not_official_holiday_notice")

    is_payroll_safe = is_working_day is True and not review_required and decision_intent in {"payroll", "general"}
    return {
        "is_working_day": is_working_day,
        "is_business_day": is_working_day,
        "is_payroll_safe": is_payroll_safe,
        "requires_human_review": review_required,
        "reason_codes": _dedupe(reason_codes),
        "holiday": holiday_match,
        "weekday": weekday,
        "decision_intent": decision_intent,
        "warnings": _dedupe(warnings),
    }


def _decision_payload(
    *,
    profile: ComplianceProfile,
    normalized: dict[str, Any],
    decision: dict[str, Any],
    trace_id: str | None,
    result_class: str,
) -> dict[str, Any]:
    bs_year = int(normalized["bs_year"])
    meta = build_bs_claim_meta(bs_year, trace_id=trace_id, result_class=result_class)
    confidence = str(meta["confidence"])
    warnings = _dedupe([*meta["warnings"], *decision["warnings"]])
    if decision["requires_human_review"] and confidence == "official_verified":
        confidence = "source_backed"
    elif decision["requires_human_review"] and confidence not in {"unsupported", "research_preview"}:
        confidence = "unsupported" if "SOURCE_CONFIDENCE_TOO_LOW" in decision["reason_codes"] else confidence
    meta = {
        **meta,
        "confidence": confidence,
        "claim_boundary": COMPLIANCE_BOUNDARY,
        "warnings": warnings,
    }
    fact_ids = [
        profile_policy_fact_id(profile.profile_id),
        working_day_fact_id(profile.profile_id, bs_year, int(normalized["bs_month"]), int(normalized["bs_day"])),
        fiscal_period_fact_id(bs_year, int(normalized["bs_month"]), int(normalized["bs_day"])),
        bs_ad_fact_id(bs_year, int(normalized["bs_month"]), int(normalized["bs_day"])),
    ]
    trace_fact_id = fact_ids[1]
    return {
        "profile_id": profile.profile_id,
        "profile": {
            "label": profile.label,
            "status": profile.status,
            "jurisdiction": profile.jurisdiction,
        },
        "date": _date_block(normalized),
        "decision": {
            key: value
            for key, value in decision.items()
            if key not in {"warnings", "weekday", "decision_intent"}
        },
        "fiscal_period": _fiscal_summary(normalized),
        "policy": get_policy_metadata(),
        "fact_ids": fact_ids,
        "trace_url": f"/v3/api/timegraph/facts/{trace_fact_id}/trace",
        "meta": meta,
    }


def _normalize_date(*, bs_date: str | None, ad_date: str | None) -> dict[str, Any]:
    if bool(bs_date) == bool(ad_date):
        raise ValueError("Provide exactly one of bs_date or ad_date.")
    if bs_date:
        bs_year, bs_month, bs_day = parse_bs_date(bs_date)
        ad = bs_to_gregorian(bs_year, bs_month, bs_day)
    else:
        ad = parse_ad_date(str(ad_date))
        bs_year, bs_month, bs_day = gregorian_to_bs(ad)
    return {
        "bs": _format_bs(bs_year, bs_month, bs_day),
        "ad": ad.isoformat(),
        "bs_year": bs_year,
        "bs_month": bs_month,
        "bs_day": bs_day,
        "ad_date": ad,
    }


def _date_block(normalized: dict[str, Any]) -> dict[str, str]:
    return {
        "bs": str(normalized["bs"]),
        "ad": str(normalized["ad"]),
    }


def _fiscal_summary(normalized: dict[str, Any]) -> dict[str, Any]:
    period = fiscal_period_for_bs_date(
        int(normalized["bs_year"]),
        int(normalized["bs_month"]),
        int(normalized["bs_day"]),
    )
    return {
        "fiscal_year_label": period.fiscal_year_label,
        "fiscal_month": period.fiscal_month,
        "fiscal_quarter": period.fiscal_quarter,
    }


def _format_bs(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def _get_profile(profile_id: str) -> ComplianceProfile:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"Unknown compliance profile: {profile_id}") from exc


def _match_public_holiday(
    profile: ComplianceProfile,
    bs_month: int,
    bs_day: int,
) -> dict[str, str] | None:
    if not profile.holiday_policy.include_public_holidays:
        return None
    match = FIXED_BS_PUBLIC_HOLIDAYS.get((bs_month, bs_day))
    return dict(match) if match else None


def _compliance_meta(
    *,
    trace_id: str | None,
    confidence: str,
    result_class: str,
    warnings: list[str],
) -> dict[str, Any]:
    return build_claim_meta(
        source=ENTERPRISE_COMPLIANCE_PROFILES,
        confidence=confidence,
        claim_boundary=COMPLIANCE_BOUNDARY,
        warnings=_dedupe([*warnings, "not_legal_tax_or_banking_contract_authority"]),
        trace_id=trace_id,
        result_class=result_class,
    )


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


REASON_CODE_CATALOG = {
    "WEEKDAY": "The normalized AD weekday is not configured as a non-working weekday for the profile.",
    "WEEKEND": "The normalized AD weekday is configured as non-working for the profile.",
    "SATURDAY_NON_WORKING": "Saturday is configured as non-working for this profile.",
    "PUBLIC_HOLIDAY_MATCH": "A public-corpus fixed-date observance matched the normalized BS date.",
    "BANKING_HOLIDAY_SOURCE_NOT_AVAILABLE": "The profile asks for banking holiday support, but no authoritative banking holiday source is bundled.",
    "PROFILE_REQUIRES_OFFICIAL_SOURCE": "The profile policy requires official-source review before operational use.",
    "SOURCE_CONFIDENCE_TOO_LOW": "The date source confidence is below the profile policy requirement.",
    "OUTSIDE_SUPPORTED_RANGE": "The request falls outside the supported calendar range.",
    "RESEARCH_PREVIEW_BLOCKED": "Research-preview data is not allowed for this compliance profile.",
    "FUTURE_DATE_REVIEW_REQUIRED": "The profile requires human review for future-dated decisions.",
    "NO_MATCHING_PUBLIC_HOLIDAY": "No fixed-date public-corpus holiday matched the normalized BS date.",
    "FISCAL_YEAR_BOUNDARY": "The date is the first day of a Nepali fiscal year.",
    "PAYROLL_REVIEW_REQUIRED": "Payroll-style use requires stronger source and policy review.",
}


__all__ = [
    "MAX_ADD_WORKING_DAYS",
    "MAX_WORKING_DAY_SEARCH_DAYS",
    "REASON_CODE_CATALOG",
    "add_working_days_payload",
    "evaluate_date_payload",
    "fiscal_period_payload",
    "get_profile_payload",
    "list_profiles_payload",
    "month_closing_day_payload",
    "next_working_day_payload",
    "previous_working_day_payload",
]
