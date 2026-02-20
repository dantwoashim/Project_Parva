"""Unit tests for canonical v4 rule catalog."""

from app.rules.catalog_v4 import (
    get_rule_v4,
    get_rules_coverage,
    get_rules_scoreboard,
    load_catalog_v4,
    reload_catalog_v4,
    rule_has_algorithm,
    rule_quality_band,
)


def test_catalog_loads_with_expected_minimum_size():
    catalog = load_catalog_v4()
    assert catalog.version == 4
    assert catalog.total_rules >= 300
    assert len(catalog.festivals) == catalog.total_rules


def test_dashain_rule_prefers_v3_source():
    rule = get_rule_v4("dashain")
    assert rule is not None
    assert rule.source == "festival_rules_v3"
    assert rule.status == "computed"
    assert rule.rule_type == "lunar"
    assert rule.rule.get("lunar_month") == "Ashwin"


def test_coverage_math_is_consistent():
    coverage = get_rules_coverage(target=300)
    assert coverage["total_rules"] >= 300
    assert coverage["computed_rules"] + coverage["provisional_rules"] + coverage["override_rules"] == coverage["total_rules"]
    assert coverage["remaining_to_target"] == max(300 - coverage["total_rules"], 0)
    assert coverage["by_source"].get("rule_ingestion_seed_v1", 0) > 0


def test_reload_catalog_is_idempotent():
    first = reload_catalog_v4()
    second = reload_catalog_v4()
    assert first.total_rules == second.total_rules


def test_scoreboard_uses_computed_as_headline():
    scoreboard = get_rules_scoreboard(target=300)
    assert scoreboard["computed"]["count"] >= 20
    assert scoreboard["claim_guard"]["headline_metric"] == "computed"


def test_rule_quality_helpers_are_consistent():
    dashain = get_rule_v4("dashain")
    assert dashain is not None
    assert rule_quality_band(dashain) == "computed"
    assert rule_has_algorithm(dashain) is True

    inventory = get_rule_v4("bhoto-jatra")
    assert inventory is not None
    assert rule_quality_band(inventory) == "inventory"
    assert rule_has_algorithm(inventory) is False
