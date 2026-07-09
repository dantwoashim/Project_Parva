"""Prediction set helper tests."""

from app.research.future_bs.prediction_sets import prediction_set_payload


def test_prediction_sets_include_second_candidate_when_needed():
    payload = prediction_set_payload(
        {
            "probability": {"30_days": 0.72, "31_days": 0.28},
            "confidence_score": 0.72,
            "risk_flags": ["manual_review_recommended"],
        }
    )

    assert payload["probabilities"]["30"] == 0.72
    assert payload["prediction_set_80"] == [30, 31]
    assert payload["prediction_set_95"] == [30, 31]
    assert payload["point_prediction_claimable"] is False
