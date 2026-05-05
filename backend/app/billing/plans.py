"""Commercial plan definitions for Parva API access."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanDefinition:
    slug: str
    name: str
    currency: str
    price_minor: int
    monthly_limit: int
    daily_limit: int | None
    support: str
    features: tuple[str, ...]


FREE_DAILY_LIMIT = 100

PLAN_DEFINITIONS: tuple[PlanDefinition, ...] = (
    PlanDefinition(
        slug="free",
        name="Free",
        currency="NPR",
        price_minor=0,
        monthly_limit=0,
        daily_limit=FREE_DAILY_LIMIT,
        support="None",
        features=("Public endpoints",),
    ),
    PlanDefinition(
        slug="starter",
        name="Starter",
        currency="NPR",
        price_minor=50_000,
        monthly_limit=5_000,
        daily_limit=None,
        support="Email",
        features=("API key", "Email support", "Public API access"),
    ),
    PlanDefinition(
        slug="professional",
        name="Professional",
        currency="NPR",
        price_minor=200_000,
        monthly_limit=50_000,
        daily_limit=None,
        support="Priority email",
        features=("API key", "Priority support", "Webhook festival notifications"),
    ),
    PlanDefinition(
        slug="enterprise",
        name="Enterprise",
        currency="NPR",
        price_minor=0,
        monthly_limit=10_000_000,
        daily_limit=None,
        support="SLA",
        features=("Custom endpoints", "Private deployment option", "SLA"),
    ),
)

PLANS_BY_SLUG = {plan.slug: plan for plan in PLAN_DEFINITIONS}

