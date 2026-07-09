from app.research.future_bs.claim_readiness import claim_readiness_report


def test_false_green_rate_is_reported():
    payload = claim_readiness_report()
    assert 0.0 <= payload["false_green_rate"] <= 1.0
