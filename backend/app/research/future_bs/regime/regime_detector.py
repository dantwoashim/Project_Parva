"""Regime detector for source-policy separated future-BS predictions."""

from __future__ import annotations

from typing import Any

PUBLICATION_STATUS = "computed_prediction_not_official"


def detect_regime(
    *,
    bs_year: int,
    bs_month: int,
    solar_civil_prediction: int,
    legacy_static_prediction: int,
    hamropatro_shadow_prediction: int | None,
    best_source_tier: int | None = None,
    source_conflict: bool = False,
    boundary_sensitive: bool = False,
) -> dict[str, Any]:
    """Assign a regime label from tower disagreement and source strength."""

    market_values = {legacy_static_prediction}
    if hamropatro_shadow_prediction is not None:
        market_values.add(hamropatro_shadow_prediction)
    market_agrees = solar_civil_prediction in market_values
    market_disagrees = not market_agrees

    if source_conflict:
        regime = "source_conflict"
    elif best_source_tier == 1 and bs_year >= 2078:
        regime = "modern_official_solar_civil"
    elif bs_year > 2083:
        regime = "future_uncertain" if market_disagrees or boundary_sensitive else "modern_official_solar_civil"
    elif market_disagrees and best_source_tier and best_source_tier <= 4:
        regime = "mixed_transition"
    elif market_disagrees:
        regime = "legacy_market_continuity"
    else:
        regime = "legacy_market_continuity" if best_source_tier and best_source_tier >= 5 else "modern_official_solar_civil"

    return {
        "publication_status": PUBLICATION_STATUS,
        "bs_year": int(bs_year),
        "bs_month": int(bs_month),
        "regime_assignment": regime,
        "market_agrees_with_solar": market_agrees,
        "market_disagrees_with_solar": market_disagrees,
        "source_conflict": source_conflict,
        "boundary_sensitive": boundary_sensitive,
        "best_source_tier": best_source_tier,
    }


__all__ = ["PUBLICATION_STATUS", "detect_regime"]
