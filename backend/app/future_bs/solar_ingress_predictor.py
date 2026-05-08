"""Computational BS month-length prediction from solar ingress events."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from typing import Any

from app.calendar.bikram_sambat import bs_to_gregorian
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR
from app.calendar.ephemeris.time_utils import NEPAL_TZ

from .accuracy import source_policy_allows
from .boundary_risk import boundary_risk_payload
from .civil_rules import ASSIGNMENT_RULES, CivilRuleResult, assign_with_rule
from .corpus import corpus_rows
from .models import MONTH_DAY_VALUES, RulePrediction, SolarIngressEvent
from .solar_ingress_engine import events_around_bs_year
from .source_policy import POLICIES as RECONSTRUCTED_SOURCE_POLICIES
from .source_policy import policy_rows as reconstructed_policy_rows

REFERENCE_TRAINING_SOURCE_POLICY = "all_reference"
DEFAULT_REFERENCE_TRAIN_END = min(BS_MAX_YEAR, 2083)
RECONSTRUCTED_TRAINING_SOURCE_POLICIES = {
    "official_strict",
    "medium_high_training",
    "all_witness_experimental",
}
CALIBRATED_REFERENCE_RULE = "calibrated_reference_cutoff"
CALIBRATED_RECENT_RULE = "calibrated_recent_cutoff"
CIVIL_DECISION_KNN_RULE = "civil_decision_knn"
RECENT_CUTOFF_YEARS = 24
KNN_WINDOW_YEARS = 36
KNN_NEIGHBORS = 3
PREDICTION_RULES = (
    *ASSIGNMENT_RULES.keys(),
    CALIBRATED_REFERENCE_RULE,
    CALIBRATED_RECENT_RULE,
    CIVIL_DECISION_KNN_RULE,
)
RUNTIME_SCORING_RULES = (
    CIVIL_DECISION_KNN_RULE,
    CALIBRATED_RECENT_RULE,
    CALIBRATED_REFERENCE_RULE,
)


def _cutoff_text(cutoff_minutes: int) -> str:
    return f"{cutoff_minutes // 60:02d}:{cutoff_minutes % 60:02d}"


def _uses_reconstructed_policy(source_policy: str) -> bool:
    return source_policy in RECONSTRUCTED_TRAINING_SOURCE_POLICIES


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value.strip())


@lru_cache(maxsize=64)
def _reconstructed_rows_for_training(
    train_start: int,
    train_end: int,
    *,
    source_policy: str,
) -> tuple[dict[str, str], ...]:
    if source_policy not in RECONSTRUCTED_SOURCE_POLICIES:
        raise ValueError(f"Unknown reconstructed source policy: {source_policy}")
    if source_policy == "hamropatro_shadow_experimental":
        raise ValueError("HamroPatro shadow data is not allowed for solar-civil training.")
    rows = [
        row
        for row in reconstructed_policy_rows(source_policy)
        if train_start <= int(row["bs_year"]) <= train_end
    ]
    rows.sort(key=lambda row: (int(row["bs_year"]), int(row["bs_month"])))
    return tuple(rows)


def _reconstructed_months_by_year(
    train_start: int,
    train_end: int,
    *,
    source_policy: str,
) -> dict[int, list[int]]:
    rows = _reconstructed_rows_for_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    grouped: dict[int, dict[int, int]] = {}
    for row in rows:
        grouped.setdefault(int(row["bs_year"]), {})[int(row["bs_month"])] = int(row["month_length"])
    complete: dict[int, list[int]] = {}
    for year, month_map in grouped.items():
        if len(month_map) != 12:
            continue
        months = [month_map[month] for month in range(1, 13)]
        if sum(months) in {365, 366}:
            complete[year] = months
    return complete


def _reconstructed_decision_samples_for_cutoff_training(
    train_start: int,
    train_end: int,
    *,
    source_policy: str,
) -> dict[int, list[dict[str, int]]]:
    by_month: dict[int, list[dict[str, int]]] = {month: [] for month in range(1, 13)}
    rows = _reconstructed_rows_for_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    for row in rows:
        bs_year = int(row["bs_year"])
        month = int(row["bs_month"])
        official_start = _parse_iso_date(row["month_start_ad"])
        candidates = [event for event in events_around_bs_year(bs_year) if event.bs_month == month]
        if not candidates:
            continue
        event = min(
            candidates,
            key=lambda candidate: abs((candidate.datetime_nepal.date() - official_start).days),
        )
        decision_days = (official_start - event.datetime_nepal.date()).days
        if decision_days not in {0, 1}:
            continue
        by_month[month].append(
            {
                "bs_year": bs_year,
                "minute_of_day": event.datetime_nepal.hour * 60 + event.datetime_nepal.minute,
                "decision_days": decision_days,
            }
        )
    return by_month


@lru_cache(maxsize=128)
def _decision_samples_for_cutoff_training(
    train_start: int,
    train_end: int,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[int, list[dict[str, int]]]:
    if source_policy == "hamropatro_shadow_experimental":
        raise ValueError("HamroPatro shadow data is not allowed for solar-civil training.")
    if _uses_reconstructed_policy(source_policy):
        return _reconstructed_decision_samples_for_cutoff_training(
            train_start,
            train_end,
            source_policy=source_policy,
        )

    by_month: dict[int, list[dict[str, int]]] = {month: [] for month in range(1, 13)}
    for row in corpus_rows():
        if not train_start <= row.bs_year <= train_end:
            continue
        if not source_policy_allows(row.source_type, row.verification_status, source_policy):
            continue
        if sum(row.months) not in {365, 366}:
            continue
        events = events_around_bs_year(row.bs_year)
        for month in range(1, 13):
            official_start = bs_to_gregorian(row.bs_year, month, 1)
            candidates = [event for event in events if event.bs_month == month]
            if not candidates:
                continue
            event = min(
                candidates,
                key=lambda candidate: abs((candidate.datetime_nepal.date() - official_start).days),
            )
            decision_days = (official_start - event.datetime_nepal.date()).days
            if decision_days not in {0, 1}:
                continue
            by_month[month].append(
                {
                    "bs_year": row.bs_year,
                    "minute_of_day": event.datetime_nepal.hour * 60 + event.datetime_nepal.minute,
                    "decision_days": decision_days,
                }
            )
    return by_month


def _best_cutoff(rows: list[dict[str, int]]) -> int:
    if not rows:
        return 720
    best_cutoff = 720
    best_errors = len(rows)
    for cutoff in range(24 * 60):
        errors = sum(
            (0 if row["minute_of_day"] <= cutoff else 1) != row["decision_days"]
            for row in rows
        )
        if errors < best_errors or (
            errors == best_errors and abs(cutoff - 720) < abs(best_cutoff - 720)
        ):
            best_cutoff = cutoff
            best_errors = errors
    return best_cutoff


@lru_cache(maxsize=128)
def calibrated_reference_cutoffs(
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[int, int]:
    samples = _decision_samples_for_cutoff_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    cutoffs: dict[int, int] = {}
    for month in range(1, 13):
        cutoffs[month] = _best_cutoff(samples.get(month, []))
    return cutoffs


@lru_cache(maxsize=128)
def calibrated_recent_cutoffs(
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    recent_years: int = RECENT_CUTOFF_YEARS,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[int, int]:
    samples = _decision_samples_for_cutoff_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    recent_start = max(train_start, train_end - recent_years + 1)
    cutoffs: dict[int, int] = {}
    for month in range(1, 13):
        rows = [
            row
            for row in samples.get(month, [])
            if row["bs_year"] >= recent_start
        ]
        if len(rows) < min(8, recent_years):
            rows = samples.get(month, [])
        cutoffs[month] = _best_cutoff(rows)
    return cutoffs


def _fixed_cutoff_assignment(
    event: SolarIngressEvent,
    *,
    cutoff_minutes: int,
    rule_name: str,
    confidence: float,
) -> CivilRuleResult:
    cutoff = time(cutoff_minutes // 60, cutoff_minutes % 60)
    local_dt = event.datetime_nepal
    cutoff_dt = datetime.combine(local_dt.date(), cutoff, tzinfo=NEPAL_TZ)
    assigned = local_dt.date() if local_dt <= cutoff_dt else local_dt.date() + timedelta(days=1)
    distance = int(abs((local_dt - cutoff_dt).total_seconds()) // 60)
    return CivilRuleResult(
        rule_name=rule_name,
        sankranti_nepal_time=local_dt,
        assigned_month_start_date=assigned,
        cutoff_used=_cutoff_text(cutoff_minutes),
        boundary_distance_minutes=distance,
        rule_confidence=confidence,
    )


def _assign_calibrated_reference_cutoff(
    event: SolarIngressEvent,
    *,
    train_start: int,
    train_end: int,
    source_policy: str,
) -> CivilRuleResult:
    cutoff_minutes = calibrated_reference_cutoffs(
        train_start,
        train_end,
        source_policy=source_policy,
    ).get(event.bs_month, 720)
    return _fixed_cutoff_assignment(
        event,
        cutoff_minutes=cutoff_minutes,
        rule_name=CALIBRATED_REFERENCE_RULE,
        confidence=0.76,
    )


def _assign_calibrated_recent_cutoff(
    event: SolarIngressEvent,
    *,
    train_start: int,
    train_end: int,
    source_policy: str,
) -> CivilRuleResult:
    cutoff_minutes = calibrated_recent_cutoffs(
        train_start,
        train_end,
        source_policy=source_policy,
    ).get(event.bs_month, 720)
    return _fixed_cutoff_assignment(
        event,
        cutoff_minutes=cutoff_minutes,
        rule_name=CALIBRATED_RECENT_RULE,
        confidence=0.78,
    )


def _assign_civil_decision_knn(
    event: SolarIngressEvent,
    *,
    train_start: int,
    train_end: int,
    target_bs_year: int,
    source_policy: str,
) -> CivilRuleResult:
    samples = _decision_samples_for_cutoff_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    rows = [
        row
        for row in samples.get(event.bs_month, [])
        if row["bs_year"] != target_bs_year
        and row["bs_year"] >= target_bs_year - KNN_WINDOW_YEARS
    ]
    if len(rows) < KNN_NEIGHBORS:
        rows = [
            row
            for row in samples.get(event.bs_month, [])
            if row["bs_year"] != target_bs_year
        ]
    minute = event.datetime_nepal.hour * 60 + event.datetime_nepal.minute
    if not rows:
        fallback = _assign_calibrated_recent_cutoff(
            event,
            train_start=train_start,
            train_end=train_end,
            source_policy=source_policy,
        )
        return CivilRuleResult(
            rule_name=CIVIL_DECISION_KNN_RULE,
            sankranti_nepal_time=fallback.sankranti_nepal_time,
            assigned_month_start_date=fallback.assigned_month_start_date,
            cutoff_used=f"fallback:{fallback.cutoff_used}",
            boundary_distance_minutes=fallback.boundary_distance_minutes,
            rule_confidence=0.62,
        )
    scored = sorted(
        (
            (abs(row["minute_of_day"] - minute), -row["bs_year"], row)
            for row in rows
        ),
        key=lambda item: item[:2],
    )
    nearest = scored[:KNN_NEIGHBORS]
    votes: Counter[int] = Counter(row["decision_days"] for _, _, row in nearest)
    decision = votes.most_common(1)[0][0]
    same_class_distance = min(
        (distance for distance, _, row in scored if row["decision_days"] == decision),
        default=0,
    )
    opposite_distance = min(
        (distance for distance, _, row in scored if row["decision_days"] != decision),
        default=720,
    )
    margin = votes[decision] - max(
        (count for label, count in votes.items() if label != decision),
        default=0,
    )
    assigned = event.nepal_date + timedelta(days=decision)
    confidence = 0.72 + min(0.2, margin * 0.06) + min(0.08, opposite_distance / 1440)
    return CivilRuleResult(
        rule_name=CIVIL_DECISION_KNN_RULE,
        sankranti_nepal_time=event.datetime_nepal,
        assigned_month_start_date=assigned,
        cutoff_used=(
            f"k={KNN_NEIGHBORS};window={KNN_WINDOW_YEARS};"
            f"same_distance={same_class_distance};opposite_distance={opposite_distance}"
        ),
        boundary_distance_minutes=opposite_distance,
        rule_confidence=round(min(confidence, 0.98), 4),
    )


def _assign_rule(
    event: SolarIngressEvent,
    rule_name: str,
    *,
    train_start: int,
    train_end: int,
    target_bs_year: int,
    source_policy: str,
) -> CivilRuleResult:
    if rule_name == CALIBRATED_REFERENCE_RULE:
        return _assign_calibrated_reference_cutoff(
            event,
            train_start=train_start,
            train_end=train_end,
            source_policy=source_policy,
        )
    if rule_name == CALIBRATED_RECENT_RULE:
        return _assign_calibrated_recent_cutoff(
            event,
            train_start=train_start,
            train_end=train_end,
            source_policy=source_policy,
        )
    if rule_name == CIVIL_DECISION_KNN_RULE:
        return _assign_civil_decision_knn(
            event,
            train_start=train_start,
            train_end=train_end,
            target_bs_year=target_bs_year,
            source_policy=source_policy,
        )
    return assign_with_rule(event, rule_name)


def _rule_month_starts(
    bs_year: int,
    rule_name: str,
    *,
    train_start: int,
    train_end: int,
    source_policy: str,
) -> tuple[list[SolarIngressEvent], list, list[dict[str, Any]]]:
    events = events_around_bs_year(bs_year)
    mesh_events = [event for event in events if event.bs_month == 1]
    if len(mesh_events) < 2:
        raise ValueError(f"Expected two Mesh sankranti events around BS {bs_year}.")

    mesh_start = _assign_rule(
        mesh_events[0],
        rule_name,
        train_start=train_start,
        train_end=train_end,
        target_bs_year=bs_year,
        source_policy=source_policy,
    ).assigned_month_start_date
    mesh_next = _assign_rule(
        mesh_events[1],
        rule_name,
        train_start=train_start,
        train_end=train_end,
        target_bs_year=bs_year + 1,
        source_policy=source_policy,
    ).assigned_month_start_date
    scoped: list[tuple[SolarIngressEvent, Any, dict[str, Any]]] = []
    for event in events:
        assignment = _assign_rule(
            event,
            rule_name,
            train_start=train_start,
            train_end=train_end,
            target_bs_year=bs_year,
            source_policy=source_policy,
        )
        start_date = assignment.assigned_month_start_date
        if mesh_start <= start_date < mesh_next:
            scoped.append((event, start_date, assignment.payload()))
    scoped.sort(key=lambda item: item[1])
    if len(scoped) != 12:
        raise ValueError(
            f"{rule_name} produced {len(scoped)} month starts for BS {bs_year}, expected 12."
        )
    return [item[0] for item in scoped], [item[1] for item in scoped] + [mesh_next], [item[2] for item in scoped]


def _derive_month_lengths(month_start_dates: list) -> list[int]:
    return [
        (month_start_dates[index + 1] - month_start_dates[index]).days
        for index in range(12)
    ]


def _rule_risk_flags(months: list[int]) -> list[str]:
    flags: list[str] = []
    if any(days not in MONTH_DAY_VALUES for days in months):
        flags.append("constraint_violation")
    if sum(months) not in {365, 366}:
        flags.append("unusual_year_total")
    return flags


def _assignment_risk_flags(assignments: list[dict[str, Any]]) -> list[str]:
    flags: set[str] = set()
    for assignment in assignments:
        payload = boundary_risk_payload(assignment.get("boundary_distance_minutes"))
        flags.update(payload["risk_flags"])
    return sorted(flags)


@lru_cache(maxsize=2048)
def predict_with_rule(
    bs_year: int,
    rule_name: str,
    rule_weight: float = 1.0,
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> RulePrediction:
    events, starts_with_next_mesh, assignments = _rule_month_starts(
        bs_year,
        rule_name,
        train_start=train_start,
        train_end=train_end,
        source_policy=source_policy,
    )
    month_starts = starts_with_next_mesh[:-1]
    months = _derive_month_lengths(starts_with_next_mesh)
    risk_flags = sorted(set([*_rule_risk_flags(months), *_assignment_risk_flags(assignments)]))
    return RulePrediction(
        model=rule_name,
        model_family="computational_solar_ingress",
        months=months,
        month_starts=month_starts,
        rule_weight=rule_weight,
        risk_flags=risk_flags,
        events=events,
        rule_assignments=assignments,
    )


def _score_rule(
    rule_name: str,
    train_start: int,
    train_end: int,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> float:
    if _uses_reconstructed_policy(source_policy):
        exact_matches = 0
        months_tested = 0
        for bs_year, actual_months in _reconstructed_months_by_year(
            train_start,
            train_end,
            source_policy=source_policy,
        ).items():
            try:
                predicted = predict_with_rule(
                    bs_year,
                    rule_name,
                    train_start=train_start,
                    train_end=train_end,
                    source_policy=source_policy,
                ).months
            except ValueError:
                continue
            exact_matches += sum(a == b for a, b in zip(predicted, actual_months))
            months_tested += 12
        return exact_matches / months_tested if months_tested else 0.0

    exact_matches = 0
    months_tested = 0
    for row in corpus_rows():
        if not train_start <= row.bs_year <= train_end:
            continue
        if not source_policy_allows(
            row.source_type,
            row.verification_status,
            source_policy,
        ):
            continue
        if sum(row.months) not in {365, 366}:
            continue
        try:
            predicted = predict_with_rule(
                row.bs_year,
                rule_name,
                train_start=train_start,
                train_end=train_end,
                source_policy=source_policy,
            ).months
        except ValueError:
            continue
        exact_matches += sum(a == b for a, b in zip(predicted, row.months))
        months_tested += 12
    return exact_matches / months_tested if months_tested else 0.0


@lru_cache(maxsize=64)
def calibrated_rule_weights(
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[str, float]:
    if (
        train_start == BS_MIN_YEAR
        and train_end == DEFAULT_REFERENCE_TRAIN_END
        and source_policy == REFERENCE_TRAINING_SOURCE_POLICY
    ):
        return {
            CIVIL_DECISION_KNN_RULE: 0.99,
            CALIBRATED_RECENT_RULE: 0.94,
            CALIBRATED_REFERENCE_RULE: 0.90,
        }
    scores = {
        rule_name: _score_rule(
            rule_name,
            train_start,
            train_end,
            source_policy=source_policy,
        )
        for rule_name in RUNTIME_SCORING_RULES
    }
    if not any(scores.values()):
        return {rule_name: 1.0 for rule_name in RUNTIME_SCORING_RULES}
    floor = 0.05
    return {rule_name: max(score, floor) for rule_name, score in scores.items()}


def solar_civil_training_summary(
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    *,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[str, Any]:
    samples = _decision_samples_for_cutoff_training(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    payload: dict[str, Any] = {
        "publication_status": "computed_prediction_not_official",
        "training_source_policy": source_policy,
        "train_start": train_start,
        "train_end": train_end,
        "cutoff_training_samples": sum(len(rows) for rows in samples.values()),
        "cutoff_training_samples_by_month": {
            str(month): len(samples.get(month, [])) for month in range(1, 13)
        },
        "reference_cutoffs": {
            str(month): _cutoff_text(cutoff)
            for month, cutoff in calibrated_reference_cutoffs(
                train_start,
                train_end,
                source_policy=source_policy,
            ).items()
        },
        "recent_cutoffs": {
            str(month): _cutoff_text(cutoff)
            for month, cutoff in calibrated_recent_cutoffs(
                train_start,
                train_end,
                source_policy=source_policy,
            ).items()
        },
        "calibrated_rule_weights": {
            rule_name: round(weight, 6)
            for rule_name, weight in calibrated_rule_weights(
                train_start,
                train_end,
                source_policy=source_policy,
            ).items()
        },
    }
    if _uses_reconstructed_policy(source_policy):
        training_rows = _reconstructed_rows_for_training(
            train_start,
            train_end,
            source_policy=source_policy,
        )
        complete = _reconstructed_months_by_year(
            train_start,
            train_end,
            source_policy=source_policy,
        )
        tier_counts: Counter[str] = Counter(str(row.get("best_source_tier", "")) for row in training_rows)
        status_counts: Counter[str] = Counter(row.get("verification_status", "") for row in training_rows)
        payload.update(
            {
                "reconstructed_training_rows": len(training_rows),
                "reconstructed_complete_years": sorted(complete),
                "reconstructed_complete_year_count": len(complete),
                "best_tier_distribution": dict(sorted(tier_counts.items())),
                "verification_status_distribution": dict(sorted(status_counts.items())),
                "official_claim_usable": source_policy == "official_strict",
                "claim_scope": RECONSTRUCTED_SOURCE_POLICIES[source_policy]["claim_scope"],
            }
        )
    return payload


def _selected_prediction_rules(weights: dict[str, float]) -> list[str]:
    ranked = sorted(weights.items(), key=lambda row: row[1], reverse=True)
    if not ranked:
        return list(PREDICTION_RULES)
    best_rule, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    knn_score = weights.get(CIVIL_DECISION_KNN_RULE, 0.0)
    if (
        best_rule == CIVIL_DECISION_KNN_RULE
        and knn_score >= 0.98
        and knn_score - second_score >= 0.03
    ):
        return [CIVIL_DECISION_KNN_RULE]
    selected = [
        rule_name
        for rule_name, score in ranked
        if score >= max(0.80, best_score - 0.08)
    ][:5]
    for required in (CIVIL_DECISION_KNN_RULE, CALIBRATED_RECENT_RULE, CALIBRATED_REFERENCE_RULE):
        if required in weights and required not in selected and len(selected) < 5:
            selected.append(required)
    return selected or [ranked[0][0]]


def predict_solar_ingress_year(
    bs_year: int,
    *,
    train_start: int = BS_MIN_YEAR,
    train_end: int = DEFAULT_REFERENCE_TRAIN_END,
    source_policy: str = REFERENCE_TRAINING_SOURCE_POLICY,
) -> dict[str, Any]:
    weights = calibrated_rule_weights(
        train_start,
        train_end,
        source_policy=source_policy,
    )
    outputs: list[RulePrediction] = []
    errors: list[dict[str, str]] = []
    selected_rules = _selected_prediction_rules(weights)
    for rule_name in selected_rules:
        weight = weights[rule_name]
        try:
            outputs.append(
                predict_with_rule(
                    bs_year,
                    rule_name,
                    rule_weight=weight,
                    train_start=train_start,
                    train_end=train_end,
                    source_policy=source_policy,
                )
            )
        except ValueError as exc:
            errors.append({"model": rule_name, "error": str(exc)})

    if not outputs:
        raise ValueError(f"No computational solar-ingress model could predict BS {bs_year}.")

    final_months: list[int] = []
    probabilities: list[dict[str, float]] = []
    model_agreement: list[str] = []
    raw_vote_counters: list[Counter[int]] = []
    for month_index in range(12):
        weighted_votes: Counter[int] = Counter()
        raw_votes: Counter[int] = Counter()
        for output in outputs:
            days = output.months[month_index]
            weighted_votes[days] += output.rule_weight
            raw_votes[days] += 1
        total_weight = sum(weighted_votes.values()) or 1.0
        final_days = max(MONTH_DAY_VALUES, key=lambda days: (weighted_votes[days], raw_votes[days]))
        final_months.append(final_days)
        raw_vote_counters.append(raw_votes)
        probabilities.append(
            {
                f"{days}_days": round(weighted_votes.get(days, 0.0) / total_weight, 4)
                for days in MONTH_DAY_VALUES
            }
        )
        model_agreement.append(f"{raw_votes[final_days]}/{len(outputs)}")

    sequence_guard_model: str | None = None
    if sum(final_months) not in {365, 366}:
        valid_outputs = [
            output
            for output in outputs
            if sum(output.months) in {365, 366}
            and all(days in MONTH_DAY_VALUES for days in output.months)
        ]
        if valid_outputs:
            best_valid = max(valid_outputs, key=lambda output: output.rule_weight)
            final_months = list(best_valid.months)
            sequence_guard_model = best_valid.model
            model_agreement = [
                f"{raw_vote_counters[index][final_months[index]]}/{len(outputs)}"
                for index in range(12)
            ]

    risk_flags = sorted({flag for output in outputs for flag in output.risk_flags})
    if any(len({output.months[index] for output in outputs}) > 1 for index in range(12)):
        risk_flags.append("civil_rule_disagreement")
    if sequence_guard_model:
        risk_flags.append("year_total_sequence_guard_applied")

    return {
        "publication_status": "computed_prediction_not_official",
        "model_family": "computational_solar_ingress",
        "training_source_policy": source_policy,
        "rule_selection_policy": "knn_single_rule_only_when_top_scoring_and_dominant",
        "months": final_months,
        "probabilities": probabilities,
        "model_agreement": model_agreement,
        "risk_flags": sorted(set(risk_flags)),
        "sequence_guard_model": sequence_guard_model,
        "model_outputs": [output.payload() for output in outputs],
        "calibrated_rule_weights": {
            rule_name: round(weight * 100, 2) for rule_name, weight in weights.items()
        },
        "selected_prediction_rules": selected_rules,
        "errors": errors,
    }
