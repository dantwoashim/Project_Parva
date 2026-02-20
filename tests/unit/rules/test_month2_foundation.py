"""Rule foundation tests: DSL executability, promotion baseline, validation cases."""

from app.rules import get_rule_v4
from app.rules.catalog_v4 import get_rules_scoreboard
from app.rules.dsl import rule_to_dsl_document
from app.rules.execution import calculate_rule_occurrence_with_fallback, validation_cases_for_rule


def test_scoreboard_reaches_computed_baseline():
    scoreboard = get_rules_scoreboard(target=300)
    assert scoreboard["computed"]["count"] >= 200
    assert scoreboard["claim_guard"]["safe_to_claim_300"] == (scoreboard["computed"]["count"] >= 300)


def test_seed_rule_is_promoted_with_executable_dsl():
    rule = get_rule_v4("amavasya-observance-ashadh")
    assert rule is not None
    assert rule.status == "computed"

    dsl = rule_to_dsl_document(rule)
    assert dsl.executable is True
    assert dsl.execution_template == "lunar_tithi_window_v1"


def test_seed_rule_has_deterministic_validation_cases():
    rule = get_rule_v4("amavasya-observance-ashadh")
    assert rule is not None

    cases = validation_cases_for_rule(rule)
    passed = [case for case in cases if case["status"] == "passed"]

    assert len(cases) == 3
    assert passed
    assert all(case["expected_start_date"] for case in passed)


def test_legacy_rule_executes_via_fallback_or_direct_path():
    rule = get_rule_v4("bisket-jatra")
    assert rule is not None
    assert rule.status == "computed"

    result = calculate_rule_occurrence_with_fallback(rule, 2026)
    assert result is not None
    assert result.start_date.year in {2026, 2027}
