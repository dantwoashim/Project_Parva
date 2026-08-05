"""Canonical, leakage-safe Future BS predictor.

The physical ingress calculation and the published Nepali civil calendar are
related evidence, but they are not interchangeable. This module keeps a broad
historical solar-civil tower and a source-strict authority tower separate,
then reconciles their month-start decisions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, timedelta
from typing import Any

from app.calendar.constants import BS_MIN_YEAR

from .accuracy import source_policy_allows
from .corpus import corpus_rows
from .models import MONTH_DAY_VALUES
from .solar_ingress_predictor import KNN_NEIGHBORS, predict_solar_ingress_year

UNIFIED_MODEL_ID = "parva_authority_aware_solar_civil_v7"
REFERENCE_SOURCE_POLICY = "all_reference"
AUTHORITY_SOURCE_POLICY = "official_only"
REFERENCE_TOWER_WEIGHT = 1.0
AUTHORITY_TOWER_WEIGHT = 1.0
MIN_AUTHORITY_YEARS = KNN_NEIGHBORS + 1


def _validate_training_boundary(bs_year: int, train_start: int, train_end: int) -> None:
    if train_start > train_end:
        raise ValueError("Training range must be ascending.")
    if train_end >= bs_year:
        raise ValueError(
            "Future BS prediction requires a strictly past-only training window: "
            f"train_end={train_end}, target_bs_year={bs_year}."
        )


def _eligible_years(train_start: int, train_end: int, source_policy: str) -> list[int]:
    return [
        row.bs_year
        for row in corpus_rows()
        if train_start <= row.bs_year <= train_end
        and source_policy_allows(row.source_type, row.verification_status, source_policy)
    ]


def _tower_outputs(
    payload: dict[str, Any],
    *,
    tower: str,
    tower_weight: float,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    base_total = sum(
        float(output.get("rule_weight", 1.0))
        for output in payload["model_outputs"]
    ) or 1.0
    for raw in payload["model_outputs"]:
        output = deepcopy(raw)
        base_rule = str(output["model"])
        base_weight = float(output.get("rule_weight", 1.0))
        output.update(
            {
                "model": f"{tower}:{base_rule}",
                "base_rule": base_rule,
                "source_tower": tower,
                "base_rule_weight": round(base_weight, 6),
                "tower_weight": tower_weight,
                "rule_weight": round((base_weight / base_total) * tower_weight, 6),
            }
        )
        outputs.append(output)
    return outputs


def _boundaries(output: dict[str, Any]) -> list[date]:
    starts = [date.fromisoformat(value) for value in output["month_starts"]]
    if len(starts) != 12 or len(output["months"]) != 12:
        raise ValueError(f"Model {output['model']} did not return twelve BS months.")
    return [*starts, starts[-1] + timedelta(days=int(output["months"][-1]))]


def _select_boundaries(outputs: list[dict[str, Any]]) -> tuple[list[date], list[dict[str, Any]]]:
    output_boundaries = [(output, _boundaries(output)) for output in outputs]
    selected: list[date] = []
    audit: list[dict[str, Any]] = []
    for index in range(13):
        total_support: defaultdict[date, float] = defaultdict(float)
        authority_support: defaultdict[date, float] = defaultdict(float)
        reference_support: defaultdict[date, float] = defaultdict(float)
        voters: defaultdict[date, list[str]] = defaultdict(list)
        for output, boundaries in output_boundaries:
            boundary = boundaries[index]
            weight = float(output["rule_weight"])
            total_support[boundary] += weight
            voters[boundary].append(str(output["model"]))
            if output["source_tower"] == "authority":
                authority_support[boundary] += weight
            else:
                reference_support[boundary] += weight

        # Source authority resolves a numerical tie; the final date fallback is
        # deterministic and is reached only when every stronger criterion ties.
        chosen = max(
            total_support,
            key=lambda value: (
                round(total_support[value], 12),
                round(authority_support[value], 12),
                round(reference_support[value], 12),
                -value.toordinal(),
            ),
        )
        selected.append(chosen)
        audit.append(
            {
                "boundary": index + 1,
                "selected_start_ad": chosen.isoformat(),
                "candidates": [
                    {
                        "start_ad": candidate.isoformat(),
                        "weighted_support": round(total_support[candidate], 6),
                        "authority_support": round(authority_support[candidate], 6),
                        "reference_support": round(reference_support[candidate], 6),
                        "voters": sorted(voters[candidate]),
                    }
                    for candidate in sorted(total_support)
                ],
            }
        )
    return selected, audit


def _month_support(
    outputs: list[dict[str, Any]],
    final_months: list[int],
) -> tuple[list[dict[str, float]], list[str]]:
    probabilities: list[dict[str, float]] = []
    agreement: list[str] = []
    for index, final_days in enumerate(final_months):
        weighted: defaultdict[int, float] = defaultdict(float)
        raw: Counter[int] = Counter()
        for output in outputs:
            days = int(output["months"][index])
            weighted[days] += float(output["rule_weight"])
            raw[days] += 1
        total = sum(weighted.values()) or 1.0
        probabilities.append(
            {
                f"{days}_days": round(weighted.get(days, 0.0) / total, 4)
                for days in MONTH_DAY_VALUES
            }
        )
        agreement.append(f"{raw[final_days]}/{len(outputs)}")
    return probabilities, agreement


def predict_unified_future_bs_year(
    bs_year: int,
    *,
    train_start: int = BS_MIN_YEAR,
    train_end: int = 2083,
) -> dict[str, Any]:
    """Predict one BS year using strictly earlier, source-stratified evidence."""

    _validate_training_boundary(bs_year, train_start, train_end)
    reference = predict_solar_ingress_year(
        bs_year,
        train_start=train_start,
        train_end=train_end,
        source_policy=REFERENCE_SOURCE_POLICY,
    )
    outputs = _tower_outputs(
        reference,
        tower="reference",
        tower_weight=REFERENCE_TOWER_WEIGHT,
    )

    authority_years = _eligible_years(train_start, train_end, AUTHORITY_SOURCE_POLICY)
    authority_ready = len(authority_years) >= MIN_AUTHORITY_YEARS
    authority: dict[str, Any] | None = None
    if authority_ready:
        authority = predict_solar_ingress_year(
            bs_year,
            train_start=train_start,
            train_end=train_end,
            source_policy=AUTHORITY_SOURCE_POLICY,
        )
        outputs.extend(
            _tower_outputs(
                authority,
                tower="authority",
                tower_weight=AUTHORITY_TOWER_WEIGHT,
            )
        )

    boundaries, boundary_audit = _select_boundaries(outputs)
    months = [(boundaries[index + 1] - boundaries[index]).days for index in range(12)]
    if any(days not in MONTH_DAY_VALUES for days in months) or sum(months) not in {365, 366}:
        raise ValueError(
            f"Unified boundary reconciliation produced an invalid BS {bs_year} sequence: {months}."
        )

    probabilities, model_agreement = _month_support(outputs, months)
    disagreement = any(len(item["candidates"]) > 1 for item in boundary_audit)
    risk_flags = {flag for output in outputs for flag in output.get("risk_flags", [])}
    if disagreement:
        risk_flags.add("authority_reference_boundary_disagreement")

    return {
        "publication_status": "computed_prediction_not_official",
        "model_id": UNIFIED_MODEL_ID,
        "model_family": "authority_aware_solar_civil_ensemble",
        "model_subfamily": "source_stratified_month_start_reconciliation",
        "training_source_policy": "source_stratified",
        "training_source_policies": {
            "reference": REFERENCE_SOURCE_POLICY,
            "authority": AUTHORITY_SOURCE_POLICY,
        },
        "training_range": {"start_bs_year": train_start, "end_bs_year": train_end},
        "leakage_guard": {
            "past_only": True,
            "target_bs_year": bs_year,
            "maximum_training_bs_year": train_end,
            "target_and_future_rows_excluded": train_end < bs_year,
        },
        "authority_tower": {
            "active": authority_ready,
            "minimum_years": MIN_AUTHORITY_YEARS,
            "eligible_years": authority_years,
            "role": "published civil-decision evidence; never an authority replacement",
        },
        "rule_selection_policy": "source_stratified_weighted_boundary_vote",
        "probability_semantics": "normalized_model_support_not_calibrated_probability",
        "months": months,
        "month_starts": [value.isoformat() for value in boundaries[:-1]],
        "probabilities": probabilities,
        "model_agreement": model_agreement,
        "risk_flags": sorted(risk_flags),
        "sequence_guard_model": None,
        "model_outputs": outputs,
        "selected_prediction_rules": [str(output["model"]) for output in outputs],
        "boundary_decisions": boundary_audit,
        "tower_outputs": {
            "reference": reference,
            "authority": authority,
        },
        "errors": [],
    }


__all__ = [
    "AUTHORITY_SOURCE_POLICY",
    "MIN_AUTHORITY_YEARS",
    "REFERENCE_SOURCE_POLICY",
    "UNIFIED_MODEL_ID",
    "predict_unified_future_bs_year",
]
