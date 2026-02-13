"""Cross-calendar observance resolver."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from app.festivals.repository import get_repository
from app.rules import get_rule_service
from app.rules.plugins import (
    ChineseObservancePlugin,
    HebrewObservancePlugin,
    IslamicObservancePlugin,
    TibetanBuddhistObservancePlugin,
)


@dataclass
class RankedObservance:
    observance: str
    calendar_family: str
    date: str
    confidence: str
    rank_score: int
    reason_codes: list[str]
    metadata: dict


def _confidence_weight(confidence: str) -> int:
    return {
        "official": 30,
        "exact": 25,
        "computed": 20,
        "astronomical": 20,
        "approximate": 10,
        "estimated": 8,
    }.get(confidence, 5)


def _location_weight(location: str, calendar_family: str) -> tuple[int, list[str]]:
    loc = (location or "").lower()
    score = 0
    reasons: list[str] = []

    if "kathmandu" in loc or "valley" in loc:
        if calendar_family in {"nepali_hindu", "tibetan_buddhist"}:
            score += 15
            reasons.append("REGIONAL_CUSTOM")
    elif "terai" in loc:
        if calendar_family in {"nepali_hindu", "islamic"}:
            score += 12
            reasons.append("REGIONAL_CUSTOM")
    elif "usa" in loc or "uk" in loc or "australia" in loc or "diaspora" in loc:
        score += 8
        reasons.append("DIASPORA_CONTEXT")

    return score, reasons


def _preference_weight(preferences: set[str], calendar_family: str) -> tuple[int, list[str]]:
    if not preferences:
        return 0, []
    if calendar_family in preferences:
        return 30, ["USER_PREFERRED"]
    return 0, []


def _append_result(
    bucket: list[RankedObservance],
    *,
    observance: str,
    calendar_family: str,
    target: date,
    confidence: str,
    base_score: int,
    reason_codes: Iterable[str],
    metadata: dict,
) -> None:
    bucket.append(
        RankedObservance(
            observance=observance,
            calendar_family=calendar_family,
            date=target.isoformat(),
            confidence=confidence,
            rank_score=base_score,
            reason_codes=sorted(set(reason_codes)),
            metadata=metadata,
        )
    )


def resolve_observances(
    target_date: date,
    location: str = "kathmandu",
    preferences: list[str] | None = None,
) -> list[dict]:
    """Resolve and rank observances across available calendar families."""
    pref_set = {p.strip().lower() for p in (preferences or []) if p.strip()}
    results: list[RankedObservance] = []

    repo = get_repository()
    svc = get_rule_service()

    # Nepali Hindu (primary family in current product)
    for festival_id, dates in svc.on_date(target_date):
        fest = repo.get_by_id(festival_id)
        confidence = "official" if getattr(dates, "method", "") == "override" else "computed"
        score = 60 + _confidence_weight(confidence)
        reasons = ["PRIMARY_TRADITION"]
        loc_boost, loc_reasons = _location_weight(location, "nepali_hindu")
        pref_boost, pref_reasons = _preference_weight(pref_set, "nepali_hindu")
        score += loc_boost + pref_boost
        reasons += loc_reasons + pref_reasons
        if fest and fest.is_national_holiday:
            score += 20
            reasons.append("GOVERNMENT_HOLIDAY")

        _append_result(
            results,
            observance=festival_id,
            calendar_family="nepali_hindu",
            target=target_date,
            confidence=confidence,
            base_score=score,
            reason_codes=reasons,
            metadata={
                "method": getattr(dates, "method", "v2"),
                "start_date": dates.start_date.isoformat(),
                "end_date": dates.end_date.isoformat(),
            },
        )

    # Tibetan/Buddhist plugin
    tib = TibetanBuddhistObservancePlugin()
    for rule in tib.list_rules():
        out = tib.calculate(rule.id, target_date.year)
        if out and out.start_date == target_date:
            score = 40 + _confidence_weight(out.confidence)
            reasons = ["ASTRONOMICAL_MATCH"]
            loc_boost, loc_reasons = _location_weight(location, "tibetan_buddhist")
            pref_boost, pref_reasons = _preference_weight(pref_set, "tibetan_buddhist")
            score += loc_boost + pref_boost
            reasons += loc_reasons + pref_reasons
            _append_result(
                results,
                observance=rule.id,
                calendar_family="tibetan_buddhist",
                target=target_date,
                confidence=out.confidence,
                base_score=score,
                reason_codes=reasons,
                metadata={"method": out.method},
            )

    # Islamic plugin (prefer announced mode when date matches)
    isl = IslamicObservancePlugin()
    for rule in isl.list_rules():
        candidate = isl.calculate(rule.id, target_date.year, mode="announced")
        mode = "announced"
        if not candidate or candidate.start_date != target_date:
            candidate = isl.calculate(rule.id, target_date.year, mode="tabular")
            mode = "tabular"
        if candidate and candidate.start_date == target_date:
            score = 35 + _confidence_weight(candidate.confidence)
            reasons = ["ASTRONOMICAL_MATCH"]
            loc_boost, loc_reasons = _location_weight(location, "islamic")
            pref_boost, pref_reasons = _preference_weight(pref_set, "islamic")
            score += loc_boost + pref_boost
            reasons += loc_reasons + pref_reasons
            if mode == "announced":
                reasons.append("GOVERNMENT_HOLIDAY")
            _append_result(
                results,
                observance=rule.id,
                calendar_family="islamic",
                target=target_date,
                confidence=candidate.confidence,
                base_score=score,
                reason_codes=reasons,
                metadata={"method": candidate.method, "mode": mode},
            )

    # Hebrew plugin
    heb = HebrewObservancePlugin()
    for rule in heb.list_rules():
        out = heb.calculate(rule.id, target_date.year)
        if out and out.start_date == target_date:
            score = 30 + _confidence_weight(out.confidence)
            reasons = ["ASTRONOMICAL_MATCH"]
            loc_boost, loc_reasons = _location_weight(location, "hebrew")
            pref_boost, pref_reasons = _preference_weight(pref_set, "hebrew")
            score += loc_boost + pref_boost
            reasons += loc_reasons + pref_reasons
            _append_result(
                results,
                observance=rule.id,
                calendar_family="hebrew",
                target=target_date,
                confidence=out.confidence,
                base_score=score,
                reason_codes=reasons,
                metadata={"method": out.method},
            )

    # Chinese plugin
    chinese = ChineseObservancePlugin()
    for rule in chinese.list_rules():
        out = chinese.calculate(rule.id, target_date.year)
        if out and out.start_date == target_date:
            score = 30 + _confidence_weight(out.confidence)
            reasons = ["ASTRONOMICAL_MATCH"]
            loc_boost, loc_reasons = _location_weight(location, "chinese")
            pref_boost, pref_reasons = _preference_weight(pref_set, "chinese")
            score += loc_boost + pref_boost
            reasons += loc_reasons + pref_reasons
            _append_result(
                results,
                observance=rule.id,
                calendar_family="chinese",
                target=target_date,
                confidence=out.confidence,
                base_score=score,
                reason_codes=reasons,
                metadata={"method": out.method},
            )

    results.sort(key=lambda r: r.rank_score, reverse=True)
    out: list[dict] = []
    for idx, row in enumerate(results, start=1):
        out.append(
            {
                "rank": idx,
                "observance": row.observance,
                "calendar_family": row.calendar_family,
                "date": row.date,
                "confidence": row.confidence,
                "rank_score": row.rank_score,
                "reason_codes": row.reason_codes,
                "metadata": row.metadata,
            }
        )
    return out
