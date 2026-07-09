from app.research.future_bs.claim_readiness import claim_readiness_report


def test_invalid_future_totals_are_not_claimable():
    payload = claim_readiness_report()
    for row in payload["invalid_future_year_totals"]["years"]:
        assert row["risk_label"] == "RED"
        assert row["claimable"] is False
