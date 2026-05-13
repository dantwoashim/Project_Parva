from __future__ import annotations

from app.future_bs.rule_inversion.effective_cutoff import estimate_effective_cutoffs


def test_effective_cutoff_estimator_marks_minute_level_cutoff_as_limited():
    payload = estimate_effective_cutoffs(
        [
            {"bs_month": 1, "month_length": 31},
            {"bs_month": 1, "month_length": 32},
            {"bs_month": 2, "month_length": 31},
        ]
    )

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["surfaces"]["1"]["median_observed_month_length"] == 32
    assert payload["surfaces"]["1"]["cutoff_status"] == "requires_solar_ingress_cache_for_minute_level_cutoff"
    assert "solar-ingress minute offsets require trusted ephemeris cache" in payload["limitation"]
