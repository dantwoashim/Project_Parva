from app.research.future_bs.data_acquisition import source_policy


def test_source_trust_scoring_orders_official_above_weak_sources():
    assert source_policy("official_verified")["tier"] == 1
    assert source_policy("official_verified")["weight"] > source_policy("software_table_reference")["weight"]
    assert source_policy("third_party_reference")["official"] is False
    assert source_policy("needs_review")["training"] is False
