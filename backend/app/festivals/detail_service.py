"""Festival detail and explanation assembly helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from ..core.request_context import derive_support_tier
from ..explainability import create_reason_trace
from ..rules.catalog_v4 import get_rule_v4
from ..rules.variants import calculate_with_variants, filter_variants_by_profile
from .query_service import calibration_status, fallback_used, validate_profile
from .risk_service import build_risk_payload
from .trust import build_provenance


def completeness_section(status: str, note: str) -> dict[str, str]:
    return {"status": status, "note": note}


def build_detail_completeness(
    festival,
    *,
    dates,
    date_availability,
    nearby,
) -> dict[str, object]:
    mythology = festival.mythology
    has_summary_narrative = bool(
        mythology and (mythology.summary or mythology.origin_story or mythology.historical_context)
    )
    has_deep_narrative = bool(
        mythology
        and (
            mythology.origin_story
            or mythology.historical_context
            or mythology.legends
            or mythology.scriptural_references
            or mythology.regional_variations
        )
    )

    if has_summary_narrative and has_deep_narrative:
        narrative = completeness_section(
            "available",
            "Editorial origin, meaning, and contextual notes are published for this observance.",
        )
    elif festival.description or has_summary_narrative:
        narrative = completeness_section(
            "partial",
            "A summary is available, but the deeper editorial origin story is still partial.",
        )
    else:
        narrative = completeness_section(
            "missing",
            "Editorial origin material has not been published for this observance yet.",
        )

    ritual_days = festival.ritual_sequence.get("days", []) if isinstance(festival.ritual_sequence, dict) else []
    has_canonical_rituals = bool(ritual_days)
    has_source_rituals = bool(festival.daily_rituals or festival.simple_rituals)
    if has_canonical_rituals:
        ritual_sequence = completeness_section(
            "available",
            "Structured ritual steps are published for this observance.",
        )
    elif has_source_rituals:
        ritual_sequence = completeness_section(
            "partial",
            "Source ritual material exists, but the canonical step-by-step timeline is still being normalized.",
        )
    else:
        ritual_sequence = completeness_section(
            "missing",
            "Structured ritual steps are not part of the live profile for this observance yet.",
        )

    if dates is not None:
        date_resolution = completeness_section(
            "available",
            "Resolved calendar dates are available for the requested year.",
        )
    elif date_availability and date_availability.status == "missing_rule":
        date_resolution = completeness_section(
            "missing",
            "No computed rule is published for this observance yet, so live dates cannot be resolved.",
        )
    elif date_availability and date_availability.status == "calculation_error":
        date_resolution = completeness_section(
            "partial",
            "A rule exists, but the date engine failed while resolving the requested year.",
        )
    else:
        date_resolution = completeness_section(
            "missing",
            "Resolved calendar dates are not available for the requested year.",
        )

    if nearby:
        related_observances = completeness_section(
            "available",
            "Nearby observances are available for the current ritual window.",
        )
    elif festival.related_festivals:
        related_observances = completeness_section(
            "partial",
            "Editorial related observances are known, but the live nearby calendar window did not return companion festivals.",
        )
    else:
        related_observances = completeness_section(
            "missing",
            "No nearby observances were returned for this festival window.",
        )

    statuses = [
        narrative["status"],
        ritual_sequence["status"],
        date_resolution["status"],
        related_observances["status"],
    ]
    if festival.content_status == "complete" and "missing" not in statuses:
        overall = "complete"
    elif "available" in statuses or "partial" in statuses:
        overall = "partial"
    else:
        overall = "minimal"

    return {
        "overall": overall,
        "narrative": narrative,
        "ritual_sequence": ritual_sequence,
        "dates": date_resolution,
        "related_observances": related_observances,
    }


@dataclass(frozen=True)
class FestivalExplainPayload:
    festival_id: str
    festival_name: str
    year: int
    start_date: date
    end_date: date
    method: str
    confidence: str
    rule_summary: str
    explanation: str
    steps: list[str]
    calculation_trace_id: str
    profile_id: Optional[str]
    profile_note: Optional[str]
    authority_conflict: bool
    source_family: Optional[str]
    alternate_candidates: list[dict]
    authority_suggested_profile_id: Optional[str]
    authority_suggested_start_date: Optional[date]
    authority_suggested_reason: Optional[str]
    support_tier: str
    selection_policy: str
    engine_path: str
    fallback_used: bool
    calibration_status: str
    boundary_radar: str
    stability_score: float
    risk_mode: str
    abstained: bool
    recommended_action: str
    provenance: object


def build_festival_explain_payload(
    *,
    festival,
    festival_id: str,
    target_year: int,
    date_result,
    authority_mode: str,
    profile: Optional[str],
    override_info: Optional[dict],
    risk_mode: str = "standard",
) -> FestivalExplainPayload:
    selected_profile = validate_profile(profile)
    rule = get_rule_v4(festival_id)
    structured_steps = []
    if rule and getattr(rule, "type", None) == "lunar":
        rule_summary = f"{rule.lunar_month} {str(rule.paksha).capitalize()} {rule.tithi}"
        steps = [
            f"Load lunar rule for {festival.name}: {rule_summary}.",
            "Resolve lunar month boundaries (Amavasya to Amavasya).",
            "Compute udaya tithi (tithi at sunrise) for candidate dates.",
            f"Select date that matches required tithi/paksha in {target_year}.",
            f"Apply festival duration ({date_result.duration_days} day(s)).",
        ]
        explanation = (
            f"{festival.name} follows the lunar rule {rule_summary}. "
            f"For {target_year}, the matching udaya tithi resolves to "
            f"{date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "load_rule",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {"rule_summary": rule_summary, "rule_type": "lunar"},
                "rule_id": festival_id,
                "source": "festival_rules_v3.json",
                "math_expression": None,
            },
            {
                "step_type": "lunar_month_window",
                "input": {"lunar_month": rule.lunar_month, "adhik_policy": rule.adhik_policy},
                "output": {"window_model": "amavasya_to_amavasya"},
                "rule_id": festival_id,
                "source": "lunar_calendar.py",
                "math_expression": "month = [new_moon_i, new_moon_(i+1))",
            },
            {
                "step_type": "tithi_resolution",
                "input": {"paksha": rule.paksha, "tithi": rule.tithi},
                "output": {"start_date": date_result.start_date.isoformat()},
                "rule_id": festival_id,
                "source": "tithi_udaya.py",
                "math_expression": "tithi = floor(((lambda_moon - lambda_sun) mod 360)/12)+1",
            },
        ]
    elif rule and getattr(rule, "type", None) == "solar":
        month = getattr(rule, "bs_month", None)
        solar_day = getattr(rule, "solar_day", None)
        rule_summary = (
            f"Solar rule (BS month={month}, day={solar_day})"
            if month and solar_day
            else "Solar sankranti rule"
        )
        steps = [
            f"Load solar rule for {festival.name}: {rule_summary}.",
            "Resolve corresponding sankranti/BS month boundary.",
            f"Map resulting BS date into Gregorian year {target_year}.",
            f"Apply festival duration ({date_result.duration_days} day(s)).",
        ]
        explanation = (
            f"{festival.name} follows a solar rule. "
            f"For {target_year}, the computed start date is {date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "load_rule",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {"rule_summary": rule_summary, "rule_type": "solar"},
                "rule_id": festival_id,
                "source": "festival_rules_v3.json",
                "math_expression": None,
            },
            {
                "step_type": "solar_mapping",
                "input": {
                    "bs_month": getattr(rule, "bs_month", None),
                    "solar_day": getattr(rule, "solar_day", None),
                },
                "output": {"start_date": date_result.start_date.isoformat()},
                "rule_id": festival_id,
                "source": "sankranti.py",
                "math_expression": "find t where sun_longitude(t) = target_rashi_degree",
            },
        ]
    else:
        rule_summary = "Fallback legacy rule"
        steps = [
            "Festival is not yet in V3 lunar rule set.",
            "Use compatibility fallback calculation path.",
            f"Computed start date for {target_year}: {date_result.start_date.isoformat()}.",
        ]
        explanation = (
            f"{festival.name} used fallback rule handling for {target_year} "
            f"and resolved to {date_result.start_date.isoformat()}."
        )
        structured_steps = [
            {
                "step_type": "fallback",
                "input": {"festival_id": festival_id, "year": target_year},
                "output": {
                    "start_date": date_result.start_date.isoformat(),
                    "method": "fallback_v1",
                },
                "rule_id": festival_id,
                "source": "calculator.py",
                "math_expression": None,
            }
        ]

    if date_result.method == "override" and override_info and override_info.get("candidate_count", 1) > 1:
        candidate_count = int(override_info["candidate_count"])
        if authority_mode == "all_candidates":
            steps.append(
                f"Authority review found {candidate_count} candidate date entries for this festival-year; "
                "all published candidates are surfaced with the public default retained in the main date fields."
            )
        elif authority_mode == "authority_compare":
            steps.append(
                f"Authority review found {candidate_count} candidate date entries for this festival-year; "
                "compare mode retains the public default and exposes alternate authority-backed dates."
            )
        else:
            steps.append(
                f"Authority review found {candidate_count} candidate date entries for this festival-year; "
                f"the current default keeps {override_info['start'].isoformat()}."
            )
        structured_steps.append(
            {
                "step_type": "authority_conflict",
                "input": {"candidate_count": candidate_count},
                "output": {
                    "selected_start_date": override_info["start"].isoformat(),
                },
                "rule_id": festival_id,
                "source": "ground_truth_overrides+ground_truth",
                "math_expression": None,
            }
        )
        if override_info.get("authority_note"):
            explanation += f" {override_info['authority_note']}"
        if override_info.get("suggested_profile_id") and override_info.get("suggested_start"):
            suggested_profile_id = str(override_info["suggested_profile_id"])
            suggested_start = override_info["suggested_start"].isoformat()
            suggested_reason = override_info.get("suggested_reason") or (
                f"Use {suggested_profile_id} to inspect the alternate authority-backed date."
            )
            steps.append(
                f"An alternate authority-backed path is available via profile "
                f"{suggested_profile_id}, which resolves to {suggested_start}."
            )
            explanation += f" {suggested_reason}"

    profile_note = None
    if selected_profile is not None:
        variants = filter_variants_by_profile(calculate_with_variants(festival_id, target_year), profile)
        if variants:
            variant = variants[0]
            date_result.start_date = date.fromisoformat(variant["date"])
            date_result.end_date = date.fromisoformat(variant["end_date"])
            profile_note = variant.get("notes") or f"{profile} applies a documented profile variant."
            steps.append(
                f"Apply profile variant for {profile}, resolving the observance to {date_result.start_date.isoformat()}."
            )
            structured_steps.append(
                {
                    "step_type": "profile_variant",
                    "input": {"profile_id": profile},
                    "output": {"start_date": date_result.start_date.isoformat()},
                    "rule_id": festival_id,
                    "source": "regional_map.json",
                    "math_expression": None,
                }
            )
            explanation += f" Under the {profile} profile, the observance resolves to {date_result.start_date.isoformat()}."
        else:
            profile_note = (
                f"No dedicated {profile} variant is published for this festival-year, so the default date is shown."
            )
            explanation += f" {profile_note}"

    trace = create_reason_trace(
        trace_type="festival_date_explain",
        subject={"festival_id": festival_id, "festival_name": festival.name},
        inputs={"year": target_year, "rule_summary": rule_summary},
        outputs={
            "start_date": date_result.start_date.isoformat(),
            "end_date": date_result.end_date.isoformat(),
            "method": date_result.method,
        },
        steps=structured_steps,
        provenance=build_provenance(festival_id=festival_id, year=target_year).model_dump(),
    )
    confidence = "official" if date_result.method == "override" else "computed"
    authority_conflict = bool(override_info and int(override_info.get("candidate_count") or 1) > 1)
    rule_source_family = getattr(rule, "source", None) if rule else None
    explain_support_tier = (
        "conflicted"
        if authority_conflict
        else derive_support_tier(
            confidence=confidence,
            quality_band="validated" if confidence == "official" else "computed",
        )
    )
    explain_engine_path = date_result.method
    explain_fallback_used = fallback_used(date_result.method)
    risk = build_risk_payload(
        start_date=date_result.start_date,
        alternate_candidates=override_info.get("alternate_candidates", []) if override_info else [],
        support_tier=explain_support_tier,
        fallback_used=explain_fallback_used,
        risk_mode=risk_mode,
    )

    return FestivalExplainPayload(
        festival_id=festival_id,
        festival_name=festival.name,
        year=target_year,
        start_date=date_result.start_date,
        end_date=date_result.end_date,
        method=date_result.method,
        confidence=confidence,
        rule_summary=rule_summary,
        explanation=explanation,
        steps=steps,
        calculation_trace_id=trace["trace_id"],
        profile_id=profile,
        profile_note=profile_note,
        authority_conflict=authority_conflict,
        source_family=(override_info.get("source_family") if override_info else None) or rule_source_family,
        alternate_candidates=override_info.get("alternate_candidates", []) if override_info else [],
        authority_suggested_profile_id=override_info.get("suggested_profile_id") if override_info else None,
        authority_suggested_start_date=override_info.get("suggested_start") if override_info else None,
        authority_suggested_reason=override_info.get("suggested_reason") if override_info else None,
        support_tier=explain_support_tier,
        selection_policy=authority_mode,
        engine_path=explain_engine_path,
        fallback_used=explain_fallback_used,
        calibration_status=calibration_status(date_result.method),
        boundary_radar=risk["boundary_radar"],
        stability_score=risk["stability_score"],
        risk_mode=risk["risk_mode"],
        abstained=risk["abstained"],
        recommended_action=risk["recommended_action"],
        provenance=build_provenance(festival_id=festival_id, year=target_year),
    )


__all__ = [
    "FestivalExplainPayload",
    "build_detail_completeness",
    "build_festival_explain_payload",
]
