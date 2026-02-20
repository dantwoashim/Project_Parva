"""Month-8 release gates: computed coverage and claim-guard truthfulness."""

from app.rules.catalog_v4 import get_rules_scoreboard


def test_month8_computed_coverage_crosses_300():
    scoreboard = get_rules_scoreboard(target=300)
    assert scoreboard["computed"]["count"] >= 300
    assert scoreboard["claim_guard"]["safe_to_claim_300"] is True


def test_month8_provisional_is_not_algorithmic():
    scoreboard = get_rules_scoreboard(target=300)
    # Provisional rows are now reserved for override/inventory curation buckets.
    assert scoreboard["provisional"]["has_algorithm_count"] == 0
