from __future__ import annotations

import pytest
from app.research.future_bs.backtest import rolling_validation
from app.research.future_bs.corpus import get_corpus_row
from app.research.future_bs.unified_predictor import (
    MIN_AUTHORITY_YEARS,
    UNIFIED_MODEL_ID,
    predict_unified_future_bs_year,
)


def test_unified_engine_is_strictly_past_only() -> None:
    with pytest.raises(ValueError, match="strictly past-only"):
        predict_unified_future_bs_year(2084, train_start=2000, train_end=2084)

    prediction = predict_unified_future_bs_year(2084, train_start=2000, train_end=2083)
    assert prediction["leakage_guard"] == {
        "past_only": True,
        "target_bs_year": 2084,
        "maximum_training_bs_year": 2083,
        "target_and_future_rows_excluded": True,
    }


def test_authority_tower_activates_only_after_minimum_support() -> None:
    before_threshold = predict_unified_future_bs_year(2081, train_start=2000, train_end=2080)
    at_threshold = predict_unified_future_bs_year(2082, train_start=2000, train_end=2081)

    assert before_threshold["authority_tower"]["active"] is False
    assert at_threshold["authority_tower"]["active"] is True
    assert len(at_threshold["authority_tower"]["eligible_years"]) == MIN_AUTHORITY_YEARS


def test_source_stratified_boundary_vote_resolves_2082_without_a_year_patch() -> None:
    prediction = predict_unified_future_bs_year(2082, train_start=2000, train_end=2081)

    assert prediction["months"] == get_corpus_row(2082).months
    assert prediction["months"][2:4] == [32, 31]
    assert prediction["model_id"] == UNIFIED_MODEL_ID
    assert prediction["rule_selection_policy"] == "source_stratified_weighted_boundary_vote"


def test_unified_engine_scores_72_of_72_on_frozen_rolling_official_window() -> None:
    result = rolling_validation(
        2000,
        2078,
        2083,
        source_policy="official_only",
        training_source_policy="source_stratified",
        model=UNIFIED_MODEL_ID,
    )

    assert result["exact_matches"] == 72
    assert result["months_tested"] == 72
    assert result["leakage_safe"] is True
    assert result["training_source_policy"] == "source_stratified"
    assert all(run["train_end"] < run["test_start"] for run in result["runs"])
    assert all(not run["mismatch_details"] for run in result["runs"])


@pytest.mark.parametrize("bs_year", [2084, 2099, 2200])
def test_unified_public_forecasts_remain_structurally_valid(bs_year: int) -> None:
    prediction = predict_unified_future_bs_year(bs_year, train_start=2000, train_end=2083)

    assert len(prediction["months"]) == 12
    assert all(29 <= days <= 32 for days in prediction["months"])
    assert sum(prediction["months"]) in {365, 366}
    assert prediction["probability_semantics"] == "normalized_model_support_not_calibrated_probability"
