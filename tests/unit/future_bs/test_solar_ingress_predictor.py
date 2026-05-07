"""Unit coverage for the future BS solar-ingress predictor."""

from __future__ import annotations

import pytest
from app.future_bs import ensemble
from app.future_bs.backtest import backtest_model
from app.future_bs.solar_ingress_predictor import predict_solar_ingress_year


@pytest.mark.parametrize("bs_year", [2084, 2099, 2200])
def test_computational_predictor_returns_valid_year_shape(bs_year: int):
    prediction = predict_solar_ingress_year(bs_year)

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
