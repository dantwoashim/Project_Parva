"""Civil month-start rule tests."""

from app.research.future_bs.civil_rules import ASSIGNMENT_RULES, assign_with_rule
from app.research.future_bs.solar_ingress_engine import events_around_bs_year


def test_civil_rules_return_dates_and_metadata():
    event = events_around_bs_year(2084)[0]

    result = assign_with_rule(event, "learned_cutoff")

    assert result.assigned_month_start_date
    assert result.cutoff_used
    assert result.rule_confidence > 0


def test_required_rule_candidates_are_registered():
    for rule_name in [
        "same_nepal_civil_date",
        "sunrise_rule",
        "next_day_if_after_noon",
        "fixed_cutoff_18_00",
        "month_specific_cutoff",
        "learned_cutoff",
        "boundary_sensitive_rule",
    ]:
        assert rule_name in ASSIGNMENT_RULES
