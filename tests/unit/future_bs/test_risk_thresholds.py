from app.research.future_bs.risk_thresholds import classify_prediction_risk


def test_wide_prediction_set_cannot_be_green():
    label = classify_prediction_risk(
        {"confidence_score": 0.999, "risk_flags": []},
        prediction_set_95=[29, 30],
        flip_rate=0,
        year_total_valid=True,
    )
    assert label == "YELLOW"


def test_invalid_year_total_is_red():
    label = classify_prediction_risk(
        {"confidence_score": 0.999, "risk_flags": []},
        prediction_set_95=[30],
        flip_rate=0,
        year_total_valid=False,
    )
    assert label == "RED"
