from __future__ import annotations

from app.billing.plans import FREE_DAILY_LIMIT, FREE_MONTHLY_LIMIT, PLANS_BY_SLUG


def test_free_plan_invites_public_beta_development_without_enterprise_support():
    free = PLANS_BY_SLUG["free"]

    assert FREE_MONTHLY_LIMIT == 10_000
    assert FREE_DAILY_LIMIT == 1_000
    assert free.monthly_limit == FREE_MONTHLY_LIMIT
    assert free.daily_limit == FREE_DAILY_LIMIT
    assert free.support == "None"
    assert "SLA" not in free.features
    assert "Private deployment option" not in free.features
    assert free.features == (
        "Public API access",
        "Benchmark and development usage",
        "Source-aware responses",
    )


def test_paid_plan_limits_remain_stable():
    assert PLANS_BY_SLUG["starter"].monthly_limit == 5_000
    assert PLANS_BY_SLUG["professional"].monthly_limit == 50_000
    assert PLANS_BY_SLUG["enterprise"].monthly_limit == 10_000_000
