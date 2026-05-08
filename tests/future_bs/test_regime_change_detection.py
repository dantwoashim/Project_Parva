from app.future_bs.regime.regime_model import detect_regime_changes


def test_regime_change_detection_assigns_regimes():
    payload = detect_regime_changes()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["regime_counts"]
    assert payload["assignments"]
