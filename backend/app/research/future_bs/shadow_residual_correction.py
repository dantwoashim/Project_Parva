"""Shadow-calibrated residual rules for broad 2000-2099 diagnostics.

This module is deliberately not part of official_strict claim-readiness. It can
use broad mixed/shadow evidence to study whether late-regime residual patterns
would improve agreement against all available witnesses.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .corpus import corpus_rows
from .models import MONTH_DAY_VALUES
from .solar_ingress_predictor import predict_solar_ingress_year
from .source_policy import policy_rows

PUBLICATION_STATUS = "computed_prediction_not_official"
SHADOW_RULE_VERSION = "late_regime_mod4_residual_v1"
DEFAULT_TRAIN_START = 2050
DEFAULT_TRAIN_END = 2083
DEFAULT_RESIDUAL_START = 2084
DEFAULT_RESIDUAL_END = 2099
DEFAULT_MIN_SUPPORT = 4


def reference_months(start: int = 2000, end: int = 2099) -> dict[int, list[int]]:
    return {
        row.bs_year: list(row.months)
        for row in corpus_rows()
        if start <= row.bs_year <= end
    }


def base_solar_months(
    bs_year: int,
    *,
    train_start: int = DEFAULT_TRAIN_START,
    train_end: int = DEFAULT_TRAIN_END,
    source_policy: str = "medium_high_training",
) -> list[int]:
    effective_policy = source_policy
    if source_policy in {"official_strict", "medium_high_training", "all_witness_experimental"} and not policy_rows(source_policy):
        effective_policy = "all_reference"
    return list(
        predict_solar_ingress_year(
            bs_year,
            train_start=train_start,
            train_end=train_end,
            source_policy=effective_policy,
        )["months"]
    )


def residual_key(bs_year: int, bs_month: int, base_days: int) -> str:
    return f"month={bs_month}|year_mod4={bs_year % 4}|base={base_days}"


def parse_residual_key(key: str) -> tuple[int, int, int]:
    parts = dict(part.split("=", 1) for part in key.split("|"))
    return int(parts["month"]), int(parts["year_mod4"]), int(parts["base"])


def train_shadow_residual_rules(
    *,
    residual_start: int = DEFAULT_RESIDUAL_START,
    residual_end: int = DEFAULT_RESIDUAL_END,
    min_support: int = DEFAULT_MIN_SUPPORT,
    source_policy: str = "medium_high_training",
) -> dict[str, Any]:
    actual_by_year = reference_months(residual_start, residual_end)
    grouped: dict[str, list[int]] = defaultdict(list)
    support_examples: dict[str, list[dict[str, int]]] = defaultdict(list)
    for bs_year, actual in actual_by_year.items():
        base = base_solar_months(bs_year, source_policy=source_policy)
        for month_index, (base_days, actual_days) in enumerate(zip(base, actual), start=1):
            residual = actual_days - base_days
            key = residual_key(bs_year, month_index, base_days)
            grouped[key].append(residual)
            if residual != 0:
                support_examples[key].append(
                    {
                        "bs_year": bs_year,
                        "bs_month": month_index,
                        "base_days": base_days,
                        "actual_days": actual_days,
                        "residual": residual,
                    }
                )

    rules: dict[str, dict[str, Any]] = {}
    for key, residuals in grouped.items():
        residual, count = Counter(residuals).most_common(1)[0]
        if residual == 0 or count < min_support:
            continue
        month, year_mod4, base_days = parse_residual_key(key)
        rules[key] = {
            "bs_month": month,
            "year_mod4": year_mod4,
            "base_days": base_days,
            "residual": residual,
            "support_count": count,
            "sample_count": len(residuals),
            "empirical_precision": round(count / len(residuals), 6),
            "examples": support_examples[key][:10],
        }

    return {
        "publication_status": PUBLICATION_STATUS,
        "rule_version": SHADOW_RULE_VERSION,
        "calibration_scope": "all_available_shadow_reference_not_official_claim",
        "calibration_years": [residual_start, residual_end],
        "min_support": min_support,
        "source_policy": source_policy,
        "official_claim_usable": False,
        "rules": rules,
    }


def apply_shadow_residual_rules(
    bs_year: int,
    base_months: list[int],
    rules_payload: dict[str, Any],
    *,
    residual_start: int = DEFAULT_RESIDUAL_START,
) -> tuple[list[int], list[dict[str, Any]]]:
    if bs_year < residual_start:
        return list(base_months), []
    rules = rules_payload.get("rules", {})
    corrected: list[int] = []
    applied: list[dict[str, Any]] = []
    for month_index, base_days in enumerate(base_months, start=1):
        key = residual_key(bs_year, month_index, base_days)
        rule = rules.get(key)
        if not rule:
            corrected.append(base_days)
            continue
        final_days = base_days + int(rule["residual"])
        if final_days not in MONTH_DAY_VALUES:
            corrected.append(base_days)
            continue
        corrected.append(final_days)
        applied.append(
            {
                "bs_month": month_index,
                "from_days": base_days,
                "to_days": final_days,
                "rule_key": key,
                "support_count": rule["support_count"],
                "empirical_precision": rule["empirical_precision"],
            }
        )
    return corrected, applied


def predict_shadow_corrected_year(
    bs_year: int,
    rules_payload: dict[str, Any],
    *,
    source_policy: str = "medium_high_training",
) -> dict[str, Any]:
    base = base_solar_months(bs_year, source_policy=source_policy)
    months, applied = apply_shadow_residual_rules(bs_year, base, rules_payload)
    risk_flags = []
    if sum(months) not in {365, 366}:
        months = list(base)
        applied = []
        risk_flags.append("invalid_shadow_corrected_year_total_reverted_to_base")
    if applied:
        risk_flags.append("shadow_residual_correction_applied")
    return {
        "publication_status": PUBLICATION_STATUS,
        "model": "solar_civil_shadow_residual_corrected",
        "rule_version": rules_payload["rule_version"],
        "bs_year": bs_year,
        "months": months,
        "year_total": sum(months),
        "base_months": base,
        "applied_rules": applied,
        "risk_flags": risk_flags,
        "official_claim_usable": False,
        "claim_boundary": (
            "Uses shadow/reference residual calibration for diagnostic agreement only; "
            "not official publication proof."
        ),
    }


__all__ = [
    "PUBLICATION_STATUS",
    "SHADOW_RULE_VERSION",
    "apply_shadow_residual_rules",
    "base_solar_months",
    "predict_shadow_corrected_year",
    "reference_months",
    "train_shadow_residual_rules",
]
