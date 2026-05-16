"""Unit coverage for the future BS solar-ingress predictor."""

from __future__ import annotations

import pytest
from app.future_bs import ensemble
from app.future_bs.backtest import backtest_model
from app.future_bs.solar_ingress_predictor import (
    predict_solar_ingress_year,
    solar_civil_training_summary,
)

pytestmark = pytest.mark.research_artifact


@pytest.mark.parametrize("bs_year", [2084, 2099, 2200])
def test_computational_predictor_returns_valid_year_shape(bs_year: int):
    prediction = predict_solar_ingress_year(bs_year)

    assert prediction["publication_status"] == "computed_prediction_not_official"
    assert prediction["model_family"] == "computational_solar_ingress"
    assert len(prediction["months"]) == 12
    assert len(prediction["probabilities"]) == 12
    assert prediction["model_outputs"]
    assert all(29 <= days <= 32 for days in prediction["months"])


def test_known_year_backtest_runs_against_corpus():
    result = backtest_model(2070, 2075, 2076, 2076)

    assert result["mode"] == "computational_solar_ingress_holdout"
    assert result["months_tested"] == 12
    assert 0 <= result["accuracy"] <= 100
    assert result["yearly_predictions"][0]["models"]


def test_ensemble_flags_disagreement_when_diagnostic_baseline_differs(monkeypatch: pytest.MonkeyPatch):
    bs_year = 2112
    solar_months = predict_solar_ingress_year(bs_year)["months"]
    baseline_months = list(solar_months)
    baseline_months[0] = 29 if baseline_months[0] != 29 else 30

    def fake_baseline(_bs_year: int, _train_start: int, _train_end: int):
        return (
            baseline_months,
            [
                {
                    "model": "injected_diagnostic_baseline_disagreement",
                    "source_year": 2077,
                    "training_score": 0.0,
                    "months": baseline_months,
                }
            ],
        )

    monkeypatch.setattr(ensemble, "predict_from_training", fake_baseline)

    prediction = ensemble.compute_year_live(bs_year)

    assert "diagnostic_baseline_disagreement" in prediction["risk_flags"]
    assert "manual_review_recommended" in prediction["month_details"][0]["risk_flags"]
    assert (
        prediction["month_details"][0]["computational_days"]
        != prediction["month_details"][0]["diagnostic_baseline_days"]
    )


def test_medium_high_reconstructed_policy_trains_from_tier_1_to_4_rows_only():
    summary = solar_civil_training_summary(2050, 2083, source_policy="medium_high_training")

    assert summary["publication_status"] == "computed_prediction_not_official"
    assert summary["training_source_policy"] == "medium_high_training"
    if summary["reconstructed_training_rows"] == 0:
        assert summary["reconstructed_complete_year_count"] == 0
        assert summary["best_tier_distribution"] == {}
        assert summary["official_claim_usable"] is False
        return
    assert summary["reconstructed_training_rows"] >= 360
    assert summary["reconstructed_complete_year_count"] >= 25
    assert set(summary["best_tier_distribution"]).issubset({"1", "2", "3", "4"})
    assert summary["official_claim_usable"] is False
    assert sum(summary["cutoff_training_samples_by_month"].values()) > 0


def test_medium_high_reconstructed_policy_can_predict_future_year():
    prediction = predict_solar_ingress_year(
        2084,
        train_start=2050,
        train_end=2083,
        source_policy="medium_high_training",
    )

    assert prediction["publication_status"] == "computed_prediction_not_official"
    assert prediction["training_source_policy"] == "medium_high_training"
    assert len(prediction["months"]) == 12
    assert sum(prediction["months"]) in {365, 366}


def test_medium_high_rule_selection_fixes_recent_mangsir_poush_boundary():
    summary = solar_civil_training_summary(2050, 2079, source_policy="medium_high_training")
    if summary["reconstructed_training_rows"] == 0:
        pytest.skip("private reconstructed medium/high corpus is not present")
    prediction = predict_solar_ingress_year(
        2080,
        train_start=2050,
        train_end=2079,
        source_policy="medium_high_training",
    )

    assert prediction["months"] == [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]
    assert set(prediction["selected_prediction_rules"]) >= {
        "calibrated_reference_cutoff",
        "calibrated_recent_cutoff",
    }


def test_solar_civil_sequence_guard_prevents_invalid_hybrid_year_total():
    summary = solar_civil_training_summary(2050, 2083, source_policy="medium_high_training")
    if summary["reconstructed_training_rows"] == 0:
        pytest.skip("private reconstructed medium/high corpus is not present")
    prediction = predict_solar_ingress_year(
        2056,
        train_start=2050,
        train_end=2083,
        source_policy="medium_high_training",
    )

    assert sum(prediction["months"]) in {365, 366}
    assert prediction["sequence_guard_model"] is not None
    assert "year_total_sequence_guard_applied" in prediction["risk_flags"]


def test_hamropatro_shadow_policy_cannot_train_solar_civil():
    with pytest.raises(ValueError, match="HamroPatro shadow data is not allowed"):
        solar_civil_training_summary(2000, 2070, source_policy="hamropatro_shadow_experimental")
