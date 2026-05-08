from app.future_bs.model_search.regime_candidate_runner import RegimeCandidate, candidate_prediction


def test_solar_market_disagreement_increases_risk():
    candidate = RegimeCandidate(candidate_id="test_regime_gate")

    for year in range(2084, 2100):
        for month in range(1, 13):
            record = candidate_prediction(candidate, year, month)
            if record["agreement_status"] == "disagree":
                assert record["risk_label"] in {"YELLOW", "RED"}
                assert record["risk_label"] != "GREEN"
                return
    raise AssertionError("Expected at least one solar/market disagreement in 2084-2099")
