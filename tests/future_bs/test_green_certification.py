from app.future_bs.risk.green_certification import certify_green_predictions


def test_green_certification_rejects_wide_sets():
    payload = certify_green_predictions()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload.get("wide_prediction_set_green_violation_count", 0) == 0
