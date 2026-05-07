from app.future_bs.claim_readiness import claim_readiness_report


def test_claim_readiness_is_honest_and_fast_shape():
    payload = claim_readiness_report()
    assert payload["publication_status_required"] == "computed_prediction_not_official"
    assert payload["claim_ready_99_overall"] is False
    assert payload["safe_claims"]
    assert payload["unsafe_claims"]
    assert "invalid_future_year_totals" in payload
