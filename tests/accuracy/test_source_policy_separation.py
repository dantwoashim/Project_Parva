from app.research.future_bs.source_policy import policy_metrics


def test_source_policy_metrics_are_separated():
    official = policy_metrics("official_strict")
    medium = policy_metrics("medium_high_training")
    experimental = policy_metrics("all_witness_experimental")
    assert official["month_cases"] <= medium["month_cases"] <= experimental["month_cases"]
    assert official["tier_5_6_allowed"] is False
    assert medium["tier_5_6_allowed"] is False
    assert experimental["tier_5_6_allowed"] is True
