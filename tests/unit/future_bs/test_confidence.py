"""Probability and confidence tests."""

from app.research.future_bs.boundary_risk import boundary_risk_payload
from app.research.future_bs.confidence import confidence_label, score_confidence
from app.research.future_bs.probability import weighted_probability, winning_days


def test_probability_selects_weighted_winner():
    probability = weighted_probability([(29, 1.0), (30, 0.25), (29, 0.5)])

    assert winning_days(probability) == 29
    assert probability["29_days"] > probability["30_days"]


def test_confidence_label_and_score():
    score = score_confidence(
        max_probability=0.9,
        model_agreement_ratio=0.8,
        source_quality=0.7,
        boundary_factor=1.0,
        future_horizon_factor=0.8,
    )

    assert score > 0.7
    assert confidence_label(score) in {"computed_medium", "computed_high"}


def test_boundary_risk_flags_critical_distance():
    payload = boundary_risk_payload(18)

    assert payload["boundary_risk"] == "critical"
    assert "manual_review_recommended" in payload["risk_flags"]
