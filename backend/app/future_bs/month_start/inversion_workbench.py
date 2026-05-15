"""Month-start inversion workbench for verified BS calendar evidence.

The workbench treats the observed BS month start as the hidden target. Month
lengths are derived evidence, while solar ingress timing and civil assignment
rules are candidate explanations for why the official month start landed on a
specific AD date.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from app.calendar.bikram_sambat import bs_to_gregorian
from app.calendar.ephemeris.swiss_eph import calculate_sunrise, calculate_sunset
from app.calendar.ephemeris.time_utils import NEPAL_TZ, to_nepal_time
from app.future_bs.accuracy import source_allowed_for_final_test, source_allowed_for_training
from app.future_bs.boundary_risk import boundary_risk_label, boundary_risk_payload
from app.future_bs.civil_rules import CivilRuleResult, assign_with_rule
from app.future_bs.corpus import corpus_rows
from app.future_bs.models import SolarIngressEvent, month_name
from app.future_bs.solar_ingress_engine import active_ephemeris_label, events_around_bs_year

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab" / "month_start_inversion_workbench"
)
PUBLICATION_STATUS = "computed_prediction_not_official"
DEFAULT_MAX_YEAR = 2083
OFFICIAL_POLICY_NAME = "official_strict"

FIXED_RULES = (
    "same_nepal_civil_date",
    "sunrise_rule",
    "next_day_if_after_noon",
    "fixed_cutoff_18_00",
    "month_specific_cutoff",
    "boundary_sensitive_rule",
)

MONTH_START_CANDIDATE_FIELDS = [
    "bs_year",
    "bs_month",
    "bs_month_name",
    "candidate_type",
    "candidate_rule",
    "candidate_start_ad",
    "observed_month_start_ad",
    "source_type",
    "verification_status",
    "source_reference",
    "extraction_method",
    "publication_status",
    "leakage_policy",
    "official_label_available",
]

SOLAR_FEATURE_FIELDS = [
    "bs_year",
    "bs_month",
    "bs_month_name",
    "observed_month_start_ad",
    "solar_ingress_nepal_time",
    "solar_ingress_utc",
    "solar_nepal_date",
    "minute_of_day",
    "weekday",
    "official_decision_days",
    "sunrise_nepal_time",
    "sunset_nepal_time",
    "signed_minutes_from_sunrise",
    "signed_minutes_from_noon",
    "signed_minutes_from_sunset",
    "min_fixed_cutoff_distance_minutes",
    "nearest_fixed_cutoff",
    "boundary_risk",
    "ephemeris",
    "calculation_version",
    "publication_status",
]

ASSIGNMENT_FIELDS = [
    "bs_year",
    "bs_month",
    "rule_name",
    "assigned_month_start_ad",
    "observed_month_start_ad",
    "official_match",
    "error_days",
    "cutoff_used",
    "boundary_distance_minutes",
    "boundary_risk",
    "rule_confidence",
    "leakage_policy",
    "publication_status",
]

OFFICIAL_LABEL_FIELDS = [
    "bs_year",
    "bs_month",
    "rule_name",
    "official_month_start_ad",
    "candidate_month_start_ad",
    "official_match",
    "error_days",
    "boundary_risk",
    "source_type",
    "verification_status",
    "leakage_policy",
    "publication_status",
]

FALSE_GREEN_FIELDS = [
    "bs_year",
    "bs_month",
    "rule_name",
    "predicted_start_ad",
    "official_start_ad",
    "error_days",
    "boundary_risk",
    "rule_confidence",
    "memory_key",
    "recommended_gate",
    "publication_status",
]

VERIFICATION_TARGET_FIELDS = [
    "priority",
    "bs_year",
    "bs_month",
    "issue_type",
    "current_source_type",
    "current_verification_status",
    "boundary_risk",
    "rule_disagreement_count",
    "reason",
    "expected_information_gain",
    "recommended_manual_action",
    "source_reference",
    "publication_status",
]


@dataclass(frozen=True)
class SourceMonthStart:
    bs_year: int
    bs_month: int
    observed_start: date
    next_start: date
    month_length: int
    source_type: str
    source_reference: str
    source_url_or_scan: str
    verification_status: str
    checksum: str
    notes: str
    final_test_allowed: bool
    training_allowed: bool

    @property
    def official_label_available(self) -> bool:
        return self.final_test_allowed

    def identity(self) -> tuple[int, int]:
        return (self.bs_year, self.bs_month)


def _iso(value: date | datetime | None) -> str:
    return value.isoformat() if value is not None else ""


def _bool(value: bool) -> str:
    return str(bool(value)).lower()


def _minute_of_day(value: datetime) -> int:
    return value.hour * 60 + value.minute


def _fixed_cutoff_dt(local_date: date, cutoff: time) -> datetime:
    return datetime.combine(local_date, cutoff, tzinfo=NEPAL_TZ)


def _signed_minutes(lhs: datetime, rhs: datetime) -> int:
    return int(round((lhs - rhs).total_seconds() / 60))


@lru_cache(maxsize=512)
def _sunrise_sunset(local_date: date) -> tuple[datetime | None, datetime | None, str | None]:
    try:
        sunrise = to_nepal_time(calculate_sunrise(local_date))
        sunset = to_nepal_time(calculate_sunset(local_date))
        return sunrise, sunset, None
    except (RuntimeError, TypeError, ValueError) as exc:  # pragma: no cover - defensive around ephemeris backends
        return None, None, str(exc)


def _event_for_month(record: SourceMonthStart) -> SolarIngressEvent:
    events = [event for event in events_around_bs_year(record.bs_year) if event.bs_month == record.bs_month]
    if not events:
        raise ValueError(f"No solar ingress event for BS {record.bs_year}-{record.bs_month:02d}.")
    return min(events, key=lambda event: abs((event.nepal_date - record.observed_start).days))


def source_month_starts(
    *,
    max_year: int = DEFAULT_MAX_YEAR,
    include_reference_targets: bool = True,
) -> list[SourceMonthStart]:
    """Load source rows and derive observed month-start records.

    Each row starts from a source-labeled year of month lengths. The first day of
    the BS year is anchored through the repository conversion table, then all
    subsequent month starts are derived from that source row's month lengths.
    Official match labels are only enabled for source-policy final-test rows.
    """

    records: list[SourceMonthStart] = []
    for row in corpus_rows():
        if row.bs_year > max_year:
            continue
        if not include_reference_targets and not (
            row.training_allowed or row.final_test_allowed
        ):
            continue
        year_start = bs_to_gregorian(row.bs_year, 1, 1)
        starts = [year_start]
        current = year_start
        for days in row.months:
            current = current + timedelta(days=days)
            starts.append(current)
        for index, month_length in enumerate(row.months, start=1):
            records.append(
                SourceMonthStart(
                    bs_year=row.bs_year,
                    bs_month=index,
                    observed_start=starts[index - 1],
                    next_start=starts[index],
                    month_length=month_length,
                    source_type=row.source_type,
                    source_reference=row.source_reference,
                    source_url_or_scan=row.source_url_or_scan,
                    verification_status=row.verification_status,
                    checksum=row.checksum,
                    notes=row.notes,
                    final_test_allowed=source_allowed_for_final_test(
                        row.source_type,
                        row.verification_status,
                    ),
                    training_allowed=source_allowed_for_training(
                        row.source_type,
                        row.verification_status,
                    ),
                )
            )
    return records


def _fit_month_cutoffs(records: Iterable[SourceMonthStart]) -> dict[int, dict[str, Any]]:
    by_month: dict[int, list[tuple[int, int, SourceMonthStart]]] = defaultdict(list)
    for record in records:
        if not record.final_test_allowed:
            continue
        event = _event_for_month(record)
        decision_days = (record.observed_start - event.nepal_date).days
        if decision_days not in {0, 1}:
            continue
        by_month[record.bs_month].append((_minute_of_day(event.datetime_nepal), decision_days, record))

    surfaces: dict[int, dict[str, Any]] = {}
    for month in range(1, 13):
        samples = by_month.get(month, [])
        if not samples:
            surfaces[month] = {
                "cutoff_minutes": 720,
                "cutoff_text": "12:00",
                "case_count": 0,
                "training_errors": 0,
                "training_accuracy": 0.0,
                "feasible_interval": None,
                "status": "no_official_samples",
            }
            continue
        lower = max((minute for minute, decision, _ in samples if decision == 0), default=None)
        upper = min((minute - 1 for minute, decision, _ in samples if decision == 1), default=None)
        best_cutoff = 720
        best_errors = len(samples) + 1
        for cutoff in range(24 * 60):
            errors = sum((0 if minute <= cutoff else 1) != decision for minute, decision, _ in samples)
            if errors < best_errors or (
                errors == best_errors and abs(cutoff - 720) < abs(best_cutoff - 720)
            ):
                best_cutoff = cutoff
                best_errors = errors
        feasible_interval = None
        if lower is not None or upper is not None:
            interval_low = lower if lower is not None else 0
            interval_high = upper if upper is not None else 1439
            feasible_interval = {
                "min_cutoff_minutes": interval_low,
                "max_cutoff_minutes": interval_high,
                "consistent": interval_low <= interval_high,
            }
        surfaces[month] = {
            "cutoff_minutes": best_cutoff,
            "cutoff_text": f"{best_cutoff // 60:02d}:{best_cutoff % 60:02d}",
            "case_count": len(samples),
            "training_errors": best_errors,
            "training_accuracy": round((len(samples) - best_errors) / len(samples), 6),
            "feasible_interval": feasible_interval,
            "status": "consistent" if best_errors == 0 else "conflicting_or_regime_mixed",
        }
    return surfaces


def _assign_cutoff(event: SolarIngressEvent, cutoff_minutes: int, rule_name: str, confidence: float) -> CivilRuleResult:
    cutoff = time(cutoff_minutes // 60, cutoff_minutes % 60)
    cutoff_dt = _fixed_cutoff_dt(event.nepal_date, cutoff)
    assigned = event.nepal_date if event.datetime_nepal <= cutoff_dt else event.nepal_date + timedelta(days=1)
    distance = abs(_signed_minutes(event.datetime_nepal, cutoff_dt))
    return CivilRuleResult(
        rule_name=rule_name,
        sankranti_nepal_time=event.datetime_nepal,
        assigned_month_start_date=assigned,
        cutoff_used=f"{cutoff_minutes // 60:02d}:{cutoff_minutes % 60:02d}",
        boundary_distance_minutes=distance,
        rule_confidence=confidence,
    )


def _leave_one_year_cutoff(
    record: SourceMonthStart,
    official_records: list[SourceMonthStart],
) -> dict[str, Any]:
    training_records = [
        item
        for item in official_records
        if item.bs_year != record.bs_year and item.bs_month == record.bs_month
    ]
    if not training_records:
        training_records = [
            item
            for item in official_records
            if item.identity() != record.identity() and item.bs_month == record.bs_month
        ]
    surface = _fit_month_cutoffs(training_records).get(record.bs_month)
    if not surface or not surface["case_count"]:
        surface = _fit_month_cutoffs(official_records).get(record.bs_month, {})
        leakage_policy = "official_fallback_no_same_month_leave_one_year_sample"
    else:
        leakage_policy = "leave_one_year_out"
    return {
        "cutoff_minutes": int(surface.get("cutoff_minutes", 720)),
        "training_case_count": int(surface.get("case_count", 0)),
        "training_accuracy": float(surface.get("training_accuracy", 0.0)),
        "leakage_policy": leakage_policy,
    }


def solar_timing_features(record: SourceMonthStart, event: SolarIngressEvent) -> dict[str, Any]:
    sunrise, sunset, ephemeris_error = _sunrise_sunset(event.nepal_date)
    noon = _fixed_cutoff_dt(event.nepal_date, time(12, 0))
    fixed_cutoffs = {
        "06:00": _fixed_cutoff_dt(event.nepal_date, time(6, 0)),
        "12:00": noon,
        "18:00": _fixed_cutoff_dt(event.nepal_date, time(18, 0)),
    }
    if sunrise is not None:
        fixed_cutoffs["sunrise"] = sunrise
    if sunset is not None:
        fixed_cutoffs["sunset"] = sunset
    distances = {
        name: abs(_signed_minutes(event.datetime_nepal, cutoff_dt))
        for name, cutoff_dt in fixed_cutoffs.items()
    }
    nearest_cutoff = min(distances, key=distances.get)
    min_distance = distances[nearest_cutoff]
    decision_days = (record.observed_start - event.nepal_date).days
    return {
        "bs_year": record.bs_year,
        "bs_month": record.bs_month,
        "bs_month_name": month_name(record.bs_month),
        "observed_month_start_ad": record.observed_start.isoformat(),
        "solar_ingress_nepal_time": event.datetime_nepal.isoformat(),
        "solar_ingress_utc": event.datetime_utc.isoformat(),
        "solar_nepal_date": event.nepal_date.isoformat(),
        "minute_of_day": _minute_of_day(event.datetime_nepal),
        "weekday": event.datetime_nepal.strftime("%A"),
        "official_decision_days": decision_days,
        "sunrise_nepal_time": _iso(sunrise),
        "sunset_nepal_time": _iso(sunset),
        "signed_minutes_from_sunrise": _signed_minutes(event.datetime_nepal, sunrise) if sunrise else "",
        "signed_minutes_from_noon": _signed_minutes(event.datetime_nepal, noon),
        "signed_minutes_from_sunset": _signed_minutes(event.datetime_nepal, sunset) if sunset else "",
        "min_fixed_cutoff_distance_minutes": min_distance,
        "nearest_fixed_cutoff": nearest_cutoff,
        "boundary_risk": boundary_risk_label(min_distance),
        "ephemeris": event.ephemeris,
        "calculation_version": event.calculation_version,
        "publication_status": PUBLICATION_STATUS,
        "ephemeris_error": ephemeris_error or "",
    }


def _candidate_row(
    record: SourceMonthStart,
    *,
    candidate_type: str,
    candidate_rule: str,
    candidate_start_ad: date,
    leakage_policy: str,
) -> dict[str, Any]:
    return {
        "bs_year": record.bs_year,
        "bs_month": record.bs_month,
        "bs_month_name": month_name(record.bs_month),
        "candidate_type": candidate_type,
        "candidate_rule": candidate_rule,
        "candidate_start_ad": candidate_start_ad.isoformat(),
        "observed_month_start_ad": record.observed_start.isoformat(),
        "source_type": record.source_type,
        "verification_status": record.verification_status,
        "source_reference": record.source_reference,
        "extraction_method": "source_month_lengths_plus_baishakh1_anchor",
        "publication_status": PUBLICATION_STATUS,
        "leakage_policy": leakage_policy,
        "official_label_available": _bool(record.official_label_available),
    }


def _assignment_row(
    record: SourceMonthStart,
    assignment: CivilRuleResult,
    *,
    rule_name: str,
    leakage_policy: str,
) -> dict[str, Any]:
    error_days = (assignment.assigned_month_start_date - record.observed_start).days
    risk = boundary_risk_payload(assignment.boundary_distance_minutes)
    return {
        "bs_year": record.bs_year,
        "bs_month": record.bs_month,
        "rule_name": rule_name,
        "assigned_month_start_ad": assignment.assigned_month_start_date.isoformat(),
        "observed_month_start_ad": record.observed_start.isoformat(),
        "official_match": _bool(error_days == 0 and record.official_label_available),
        "error_days": error_days,
        "cutoff_used": assignment.cutoff_used,
        "boundary_distance_minutes": assignment.boundary_distance_minutes,
        "boundary_risk": risk["boundary_risk"],
        "rule_confidence": round(assignment.rule_confidence, 4),
        "leakage_policy": leakage_policy,
        "publication_status": PUBLICATION_STATUS,
    }


def _green_candidate(row: dict[str, Any], record: SourceMonthStart) -> bool:
    if not record.official_label_available:
        return False
    if row["leakage_policy"].startswith("official_fallback"):
        return False
    return (
        float(row["rule_confidence"]) >= 0.68
        and row["boundary_risk"] in {"low", "medium"}
        and int(row["error_days"]) == 0
    )


def _false_green_candidate(row: dict[str, Any], record: SourceMonthStart) -> bool:
    if not record.official_label_available:
        return False
    if row["leakage_policy"].startswith("official_fallback"):
        return False
    would_green = (
        float(row["rule_confidence"]) >= 0.68
        and row["boundary_risk"] in {"low", "medium"}
    )
    return bool(would_green and int(row["error_days"]) != 0)


def build_month_start_inversion_workbench(
    *,
    max_year: int = DEFAULT_MAX_YEAR,
    include_reference_targets: bool = True,
    top_target_limit: int = 100,
) -> dict[str, Any]:
    records = source_month_starts(
        max_year=max_year,
        include_reference_targets=include_reference_targets,
    )
    official_records = [record for record in records if record.official_label_available]
    all_official_surfaces = _fit_month_cutoffs(official_records)

    month_start_candidates: list[dict[str, Any]] = []
    solar_features: list[dict[str, Any]] = []
    civil_assignment_candidates: list[dict[str, Any]] = []
    official_match_labels: list[dict[str, Any]] = []
    false_green_memory: list[dict[str, Any]] = []
    record_rule_disagreements: dict[tuple[int, int], set[str]] = defaultdict(set)
    record_boundary_risk: dict[tuple[int, int], str] = {}

    for record in records:
        event = _event_for_month(record)
        features = solar_timing_features(record, event)
        solar_features.append(features)
        record_boundary_risk[record.identity()] = str(features["boundary_risk"])
        month_start_candidates.append(
            _candidate_row(
                record,
                candidate_type="observed_source_month_start",
                candidate_rule="source_evidence",
                candidate_start_ad=record.observed_start,
                leakage_policy="source_observed",
            )
        )

        assignments: list[tuple[CivilRuleResult, str, str]] = []
        for rule_name in FIXED_RULES:
            assignments.append((assign_with_rule(event, rule_name), "fixed_predeclared_rule", rule_name))

        loo = _leave_one_year_cutoff(record, official_records)
        loo_confidence = 0.64 + min(0.22, float(loo["training_accuracy"]) * 0.22)
        assignments.append(
            (
                _assign_cutoff(
                    event,
                    int(loo["cutoff_minutes"]),
                    "loo_month_cutoff_inversion",
                    round(loo_confidence, 4),
                ),
                str(loo["leakage_policy"]),
                "loo_month_cutoff_inversion",
            )
        )

        official_surface = all_official_surfaces.get(record.bs_month, {})
        assignments.append(
            (
                _assign_cutoff(
                    event,
                    int(official_surface.get("cutoff_minutes", 720)),
                    "all_official_month_cutoff_diagnostic",
                    0.5,
                ),
                "in_sample_diagnostic_not_for_green",
                "all_official_month_cutoff_diagnostic",
            )
        )

        for assignment, leakage_policy, rule_key in assignments:
            assignment_payload = _assignment_row(
                record,
                assignment,
                rule_name=rule_key,
                leakage_policy=leakage_policy,
            )
            civil_assignment_candidates.append(assignment_payload)
            record_rule_disagreements[record.identity()].add(
                str(assignment_payload["assigned_month_start_ad"])
            )
            month_start_candidates.append(
                _candidate_row(
                    record,
                    candidate_type="civil_rule_assignment",
                    candidate_rule=rule_key,
                    candidate_start_ad=assignment.assigned_month_start_date,
                    leakage_policy=leakage_policy,
                )
            )
            if record.official_label_available:
                official_match_labels.append(
                    {
                        "bs_year": record.bs_year,
                        "bs_month": record.bs_month,
                        "rule_name": rule_key,
                        "official_month_start_ad": record.observed_start.isoformat(),
                        "candidate_month_start_ad": assignment.assigned_month_start_date.isoformat(),
                        "official_match": _bool(int(assignment_payload["error_days"]) == 0),
                        "error_days": assignment_payload["error_days"],
                        "boundary_risk": assignment_payload["boundary_risk"],
                        "source_type": record.source_type,
                        "verification_status": record.verification_status,
                        "leakage_policy": leakage_policy,
                        "publication_status": PUBLICATION_STATUS,
                    }
                )
                if _false_green_candidate(assignment_payload, record):
                    false_green_memory.append(
                        {
                            "bs_year": record.bs_year,
                            "bs_month": record.bs_month,
                            "rule_name": rule_key,
                            "predicted_start_ad": assignment.assigned_month_start_date.isoformat(),
                            "official_start_ad": record.observed_start.isoformat(),
                            "error_days": assignment_payload["error_days"],
                            "boundary_risk": assignment_payload["boundary_risk"],
                            "rule_confidence": assignment_payload["rule_confidence"],
                            "memory_key": (
                                f"{record.bs_month:02d}:"
                                f"{rule_key}:"
                                f"{assignment_payload['boundary_risk']}:"
                                f"{assignment_payload['cutoff_used']}"
                            ),
                            "recommended_gate": "never_green_when_matching_false_green_memory",
                            "publication_status": PUBLICATION_STATUS,
                        }
                    )

    verification_targets = _build_verification_targets(
        records,
        record_rule_disagreements=record_rule_disagreements,
        record_boundary_risk=record_boundary_risk,
        limit=top_target_limit,
    )
    summary = _build_summary(
        records=records,
        official_records=official_records,
        official_match_labels=official_match_labels,
        false_green_memory=false_green_memory,
        cutoff_surfaces=all_official_surfaces,
        verification_targets=verification_targets,
    )
    return {
        "publication_status": PUBLICATION_STATUS,
        "source_policy": OFFICIAL_POLICY_NAME,
        "max_year": max_year,
        "historical_only": True,
        "generated_from": "source_labeled_month_lengths",
        "month_start_candidates": month_start_candidates,
        "solar_ingress_timing_features": solar_features,
        "civil_date_assignment_candidates": civil_assignment_candidates,
        "official_match_labels": official_match_labels,
        "boundary_risk_cases": _boundary_case_rows(solar_features),
        "rule_inversion_summary": summary,
        "false_green_memory": false_green_memory,
        "top_verification_targets": verification_targets,
    }


def _boundary_case_rows(solar_features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in solar_features
        if row["boundary_risk"] in {"critical", "high", "medium"} or int(row["bs_month"]) in {6, 7}
    ]
    return sorted(
        rows,
        key=lambda row: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(str(row["boundary_risk"]), 4),
            int(row["min_fixed_cutoff_distance_minutes"]),
            int(row["bs_year"]),
            int(row["bs_month"]),
        ),
    )


def _build_summary(
    *,
    records: list[SourceMonthStart],
    official_records: list[SourceMonthStart],
    official_match_labels: list[dict[str, Any]],
    false_green_memory: list[dict[str, Any]],
    cutoff_surfaces: dict[int, dict[str, Any]],
    verification_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in official_match_labels:
        if row["leakage_policy"] == "in_sample_diagnostic_not_for_green":
            continue
        by_rule[str(row["rule_name"])].append(row)

    rule_scores = []
    for rule_name, rows in sorted(by_rule.items()):
        total = len(rows)
        matched = sum(1 for row in rows if row["official_match"] == "true")
        errors = [abs(int(row["error_days"])) for row in rows]
        false_green_count = sum(
            1
            for item in false_green_memory
            if item["rule_name"] == rule_name
        )
        rule_scores.append(
            {
                "rule_name": rule_name,
                "official_cases": total,
                "exact_matches": matched,
                "match_rate": round(matched / total, 6) if total else 0.0,
                "mean_abs_error_days": round(mean(errors), 4) if errors else 0.0,
                "false_green_count": false_green_count,
                "claim_use": "diagnostic_only",
            }
        )
    rule_scores.sort(key=lambda row: (-float(row["match_rate"]), int(row["false_green_count"]), row["rule_name"]))

    source_counts = Counter(record.source_type for record in records)
    verification_counts = Counter(record.verification_status for record in records)
    return {
        "publication_status": PUBLICATION_STATUS,
        "workbench_status": "complete",
        "source_rows_loaded": len({record.bs_year for record in records}),
        "month_start_records": len(records),
        "official_label_months": len(official_records),
        "official_label_years": sorted({record.bs_year for record in official_records}),
        "source_type_distribution": dict(sorted(source_counts.items())),
        "verification_status_distribution": dict(sorted(verification_counts.items())),
        "active_ephemeris": active_ephemeris_label(),
        "rule_scores": rule_scores,
        "effective_cutoff_surfaces": {
            str(month): payload for month, payload in sorted(cutoff_surfaces.items())
        },
        "false_green_memory_count": len(false_green_memory),
        "top_verification_target_count": len(verification_targets),
        "claim_boundary": (
            "This workbench performs historical inversion diagnostics. It does not publish "
            "official future dates and does not establish broad future-calendar certainty."
        ),
        "corpus_bottleneck": {
            "official_label_months": len(official_records),
            "minimum_recommended_for_strong_inversion": 150,
            "status": "underpowered" if len(official_records) < 150 else "adequate_for_next_phase",
        },
    }


def _build_verification_targets(
    records: list[SourceMonthStart],
    *,
    record_rule_disagreements: dict[tuple[int, int], set[str]],
    record_boundary_risk: dict[tuple[int, int], str],
    limit: int,
) -> list[dict[str, Any]]:
    targets = []
    for record in records:
        if record.final_test_allowed:
            continue
        disagreement_count = max(0, len(record_rule_disagreements.get(record.identity(), set())) - 1)
        boundary = record_boundary_risk.get(record.identity(), "low")
        priority = 10
        reasons = []
        if record.source_type in {"third_party_reference", "scraped_reference"}:
            priority += 25
            reasons.append("current evidence is weak third-party or static reference")
        if record.verification_status != "verified":
            priority += 20
            reasons.append("verification status is not verified")
        if boundary == "critical":
            priority += 45
            reasons.append("solar ingress is critically near a civil cutoff")
        elif boundary == "high":
            priority += 35
            reasons.append("solar ingress is near a civil cutoff")
        elif boundary == "medium":
            priority += 20
            reasons.append("solar ingress has medium boundary risk")
        if record.bs_month in {6, 7}:
            priority += 25
            reasons.append("Ashwin/Kartik boundary month")
        if record.bs_year in {2076, 2077}:
            priority += 25
            reasons.append("existing archived Patro window needs promotion")
        if disagreement_count:
            priority += min(25, disagreement_count * 5)
            reasons.append("civil assignment rules disagree")
        issue_type = "official_or_printed_evidence_needed"
        if boundary in {"critical", "high"}:
            issue_type = "boundary_sensitive_month_start"
        if record.bs_year in {2076, 2077}:
            issue_type = "printed_archive_promotion"
        targets.append(
            {
                "priority": priority,
                "bs_year": record.bs_year,
                "bs_month": record.bs_month,
                "issue_type": issue_type,
                "current_source_type": record.source_type,
                "current_verification_status": record.verification_status,
                "boundary_risk": boundary,
                "rule_disagreement_count": disagreement_count,
                "reason": "; ".join(reasons) or "additional independent source would improve inversion coverage",
                "expected_information_gain": "high" if priority >= 80 else "medium" if priority >= 55 else "low",
                "recommended_manual_action": (
                    "Acquire official notice, printed Patro scan, or public masthead proving BS day 1."
                ),
                "source_reference": record.source_reference,
                "publication_status": PUBLICATION_STATUS,
            }
        )
    targets.sort(key=lambda row: (-int(row["priority"]), int(row["bs_year"]), int(row["bs_month"])))
    return targets[:limit]


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_month_start_inversion_artifacts(
    payload: dict[str, Any],
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = {
        "summary_json": output_dir / "rule_inversion_summary.json",
        "summary_md": output_dir / "rule_inversion_summary.md",
        "month_start_candidates_csv": output_dir / "month_start_candidates.csv",
        "solar_features_csv": output_dir / "solar_ingress_timing_features.csv",
        "civil_assignments_csv": output_dir / "civil_date_assignment_candidates.csv",
        "official_labels_csv": output_dir / "official_match_labels.csv",
        "boundary_risk_csv": output_dir / "boundary_risk_cases.csv",
        "false_green_memory_json": output_dir / "false_green_memory.json",
        "false_green_memory_csv": output_dir / "false_green_memory.csv",
        "top_verification_targets_csv": output_dir / "top_verification_targets.csv",
        "top_verification_targets_md": output_dir / "top_verification_targets.md",
        "workbench_payload_json": output_dir / "month_start_inversion_workbench.json",
    }
    _write_json(artifact_paths["workbench_payload_json"], payload)
    _write_json(artifact_paths["summary_json"], payload["rule_inversion_summary"])
    _write_csv(
        artifact_paths["month_start_candidates_csv"],
        payload["month_start_candidates"],
        MONTH_START_CANDIDATE_FIELDS,
    )
    _write_csv(
        artifact_paths["solar_features_csv"],
        payload["solar_ingress_timing_features"],
        SOLAR_FEATURE_FIELDS,
    )
    _write_csv(
        artifact_paths["civil_assignments_csv"],
        payload["civil_date_assignment_candidates"],
        ASSIGNMENT_FIELDS,
    )
    _write_csv(
        artifact_paths["official_labels_csv"],
        payload["official_match_labels"],
        OFFICIAL_LABEL_FIELDS,
    )
    _write_csv(
        artifact_paths["boundary_risk_csv"],
        payload["boundary_risk_cases"],
        SOLAR_FEATURE_FIELDS,
    )
    _write_json(
        artifact_paths["false_green_memory_json"],
        {
            "publication_status": PUBLICATION_STATUS,
            "false_green_memory": payload["false_green_memory"],
        },
    )
    _write_csv(
        artifact_paths["false_green_memory_csv"],
        payload["false_green_memory"],
        FALSE_GREEN_FIELDS,
    )
    _write_csv(
        artifact_paths["top_verification_targets_csv"],
        payload["top_verification_targets"],
        VERIFICATION_TARGET_FIELDS,
    )
    artifact_paths["summary_md"].write_text(
        render_rule_inversion_summary_md(payload["rule_inversion_summary"]),
        encoding="utf-8",
    )
    artifact_paths["top_verification_targets_md"].write_text(
        render_verification_targets_md(payload["top_verification_targets"]),
        encoding="utf-8",
    )
    return {name: str(path) for name, path in artifact_paths.items()}


def render_rule_inversion_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Month-Start Inversion Workbench",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "This workbench treats BS month start as the hidden variable and month length as a derived outcome.",
        "",
        "## Corpus",
        "",
        f"- Source years loaded: {summary['source_rows_loaded']}",
        f"- Month-start records: {summary['month_start_records']}",
        f"- Official label months: {summary['official_label_months']}",
        f"- Official label years: {', '.join(str(year) for year in summary['official_label_years'])}",
        f"- Active ephemeris: {summary['active_ephemeris']}",
        "",
        "## Rule Scores",
        "",
        "| Rule | Official cases | Exact matches | Match rate | False GREEN memory |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary["rule_scores"]:
        lines.append(
            f"| {row['rule_name']} | {row['official_cases']} | {row['exact_matches']} | "
            f"{row['match_rate']:.4f} | {row['false_green_count']} |"
        )
    lines.extend(
        [
            "",
            "## Effective Cutoff Surfaces",
            "",
            "| BS month | Cases | Best cutoff | Training accuracy | Status |",
            "|---:|---:|---:|---:|---|",
        ]
    )
    for month, surface in summary["effective_cutoff_surfaces"].items():
        lines.append(
            f"| {month} | {surface['case_count']} | {surface['cutoff_text']} | "
            f"{surface['training_accuracy']:.4f} | {surface['status']} |"
        )
    bottleneck = summary["corpus_bottleneck"]
    lines.extend(
        [
            "",
            "## Corpus Bottleneck",
            "",
            f"- Official label months: {bottleneck['official_label_months']}",
            f"- Minimum recommended for strong inversion: {bottleneck['minimum_recommended_for_strong_inversion']}",
            f"- Status: {bottleneck['status']}",
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def render_verification_targets_md(targets: list[dict[str, Any]]) -> str:
    lines = [
        "# Month-Start Verification Targets",
        "",
        "These targets prioritize historical source promotion for the inversion workbench.",
        "",
        "| Priority | BS year | Month | Issue | Boundary | Reason |",
        "|---:|---:|---:|---|---|---|",
    ]
    for row in targets[:100]:
        reason = str(row["reason"]).replace("|", "/")
        lines.append(
            f"| {row['priority']} | {row['bs_year']} | {row['bs_month']} | "
            f"{row['issue_type']} | {row['boundary_risk']} | {reason} |"
        )
    lines.append("")
    return "\n".join(lines)


def run_month_start_inversion_workbench(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    max_year: int = DEFAULT_MAX_YEAR,
    include_reference_targets: bool = True,
    top_target_limit: int = 100,
) -> dict[str, Any]:
    payload = build_month_start_inversion_workbench(
        max_year=max_year,
        include_reference_targets=include_reference_targets,
        top_target_limit=top_target_limit,
    )
    artifacts = write_month_start_inversion_artifacts(payload, output_dir=output_dir)
    return {
        "publication_status": PUBLICATION_STATUS,
        "output_dir": str(output_dir),
        "artifacts": artifacts,
        "summary": payload["rule_inversion_summary"],
    }
