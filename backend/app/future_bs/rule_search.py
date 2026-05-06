"""Civil-rule search helpers."""

from __future__ import annotations

from typing import Any

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR

from .solar_ingress_predictor import calibrated_rule_weights


def ranked_rules(train_start: int = BS_MIN_YEAR, train_end: int = BS_MAX_YEAR) -> list[dict[str, Any]]:
    weights = calibrated_rule_weights(train_start, train_end)
    return [
        {"rule_name": name, "score": round(weight, 4)}
        for name, weight in sorted(weights.items(), key=lambda item: item[1], reverse=True)
    ]
