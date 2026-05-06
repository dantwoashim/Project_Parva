"""Computational BS month-length prediction from solar ingress events."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS

from .boundary_risk import boundary_risk_payload
from .civil_rules import ASSIGNMENT_RULES, assign_with_rule
from .models import MONTH_DAY_VALUES, RulePrediction, SolarIngressEvent
from .solar_ingress_engine import events_around_bs_year


def _rule_month_starts(
    bs_year: int,
    rule_name: str,
) -> tuple[list[SolarIngressEvent], list, list[dict[str, Any]]]:
    assign = ASSIGNMENT_RULES[rule_name]
    events = events_around_bs_year(bs_year)
    mesh_events = [event for event in events if event.bs_month == 1]
    if len(mesh_events) < 2:
        raise ValueError(f"Expected two Mesh sankranti events around BS {bs_year}.")

    mesh_start = assign(mesh_events[0])
    mesh_next = assign(mesh_events[1])
    scoped: list[tuple[SolarIngressEvent, Any, dict[str, Any]]] = []
    for event in events:
        start_date = assign(event)
        if mesh_start <= start_date < mesh_next:
            scoped.append((event, start_date, assign_with_rule(event, rule_name).payload()))
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


@lru_cache(maxsize=512)
def predict_with_rule(bs_year: int, rule_name: str, rule_weight: float = 1.0) -> RulePrediction:
    events, starts_with_next_mesh, assignments = _rule_month_starts(bs_year, rule_name)
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


def _score_rule(rule_name: str, train_start: int, train_end: int) -> float:
    exact_matches = 0
    months_tested = 0
    for year in range(train_start, train_end + 1):
        if year not in BS_MONTH_LENGTHS:
            continue
        try:
            predicted = predict_with_rule(year, rule_name).months
        except ValueError:
            continue
        actual = BS_MONTH_LENGTHS[year]
        exact_matches += sum(a == b for a, b in zip(predicted, actual))
        months_tested += 12
    return exact_matches / months_tested if months_tested else 0.0


@lru_cache(maxsize=64)
def calibrated_rule_weights(train_start: int = BS_MIN_YEAR, train_end: int = BS_MAX_YEAR) -> dict[str, float]:
    scores = {rule_name: _score_rule(rule_name, train_start, train_end) for rule_name in ASSIGNMENT_RULES}
    if not any(scores.values()):
        return {rule_name: 1.0 for rule_name in ASSIGNMENT_RULES}
    floor = 0.05
    return {rule_name: max(score, floor) for rule_name, score in scores.items()}


def predict_solar_ingress_year(
    bs_year: int,
    *,
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
) -> dict[str, Any]:
    weights = calibrated_rule_weights(train_start, train_end)
    outputs: list[RulePrediction] = []
    errors: list[dict[str, str]] = []
    for rule_name, weight in weights.items():
        try:
            outputs.append(predict_with_rule(bs_year, rule_name, rule_weight=weight))
        except ValueError as exc:
            errors.append({"model": rule_name, "error": str(exc)})

    if not outputs:
        raise ValueError(f"No computational solar-ingress model could predict BS {bs_year}.")

    final_months: list[int] = []
    probabilities: list[dict[str, float]] = []
    model_agreement: list[str] = []
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
        probabilities.append(
            {
                f"{days}_days": round(weighted_votes.get(days, 0.0) / total_weight, 4)
                for days in MONTH_DAY_VALUES
            }
        )
        model_agreement.append(f"{raw_votes[final_days]}/{len(outputs)}")

    risk_flags = sorted({flag for output in outputs for flag in output.risk_flags})
    if any(len({output.months[index] for output in outputs}) > 1 for index in range(12)):
        risk_flags.append("civil_rule_disagreement")

    return {
        "model_family": "computational_solar_ingress",
        "months": final_months,
        "probabilities": probabilities,
        "model_agreement": model_agreement,
        "risk_flags": sorted(set(risk_flags)),
        "model_outputs": [output.payload() for output in outputs],
        "calibrated_rule_weights": {
            rule_name: round(weight * 100, 2) for rule_name, weight in weights.items()
        },
        "errors": errors,
    }
