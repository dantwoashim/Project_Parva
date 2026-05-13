"""Deterministic identifiers for public TimeGraph facts."""

from __future__ import annotations

from datetime import date


def _slug(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(":", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def format_bs_date(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def bs_date_slug(year: int, month: int, day: int) -> str:
    return f"{year:04d}_{month:02d}_{day:02d}"


def ad_date_slug(ad_date: str | date) -> str:
    value = ad_date.isoformat() if isinstance(ad_date, date) else ad_date
    return _slug(value)


def parse_bs_date(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    if len(parts) != 3:
        raise ValueError("BS date must be YYYY-MM-DD")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bs_ad_fact_id(year: int, month: int, day: int) -> str:
    return f"fact_bs_ad_{bs_date_slug(year, month, day)}"


def ad_bs_fact_id(ad_date: str | date) -> str:
    return f"fact_ad_bs_{ad_date_slug(ad_date)}"


def month_length_fact_id(year: int, month: int) -> str:
    return f"fact_month_length_bs_{year:04d}_{month:02d}"


def weekday_fact_id(ad_date: str | date) -> str:
    return f"fact_weekday_ad_{ad_date_slug(ad_date)}"


def fiscal_period_fact_id(year: int, month: int, day: int) -> str:
    return f"fact_fiscal_period_bs_{bs_date_slug(year, month, day)}"


def profile_policy_fact_id(profile_id: str) -> str:
    return f"fact_profile_policy_{_slug(profile_id)}"


def working_day_fact_id(profile_id: str, year: int, month: int, day: int) -> str:
    return f"fact_working_day_{_slug(profile_id)}_{bs_date_slug(year, month, day)}"


def source_claim_fact_id(source_id: str) -> str:
    return f"fact_source_claim_{_slug(source_id)}"


def release_membership_fact_id(release_id: str, member_id: str) -> str:
    return f"fact_release_membership_{_slug(release_id)}_{_slug(member_id)}"
