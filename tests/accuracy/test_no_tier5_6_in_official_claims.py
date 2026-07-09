from app.research.future_bs.source_policy import policy_rows


def test_tier_5_6_rows_do_not_enter_official_claims():
    for row in policy_rows("official_strict"):
        assert int(row["best_source_tier"]) < 5
        assert row["usable_for_official_claim"] == "true"
