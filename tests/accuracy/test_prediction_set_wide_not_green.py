from app.services.calendar_model_risk_service import prediction_payload


def test_wide_prediction_set_not_green_for_2083_ashwin():
    payload = prediction_payload(2083, 6)
    if len(payload["prediction_set_95"]) > 1:
        assert payload["risk_label"] != "GREEN"
    assert payload["publication_status"] == "computed_prediction_not_official"
