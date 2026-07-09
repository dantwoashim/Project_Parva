from app.research.future_bs.committee_rule_posterior import committee_rule_posterior


def test_committee_posterior_is_computed_and_normalized():
    payload = committee_rule_posterior(2084, 6)
    posterior = payload["committee_rule_posterior"]
    assert set(posterior) >= {"month_specific_cutoff", "precedent_rule", "same_day"}
    assert round(sum(posterior.values()), 4) == 1.0
    assert payload["evidence"]["historical_cases_used"] > 0


def test_committee_posterior_changes_by_training_window():
    early = committee_rule_posterior(2050, 6, train_end=2049)
    late = committee_rule_posterior(2084, 6, train_end=2083)
    assert early["committee_rule_posterior"] != late["committee_rule_posterior"]
