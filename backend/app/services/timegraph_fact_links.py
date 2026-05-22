"""Fact-id extraction helpers shared by TimeGraph and trust evidence packets."""

from __future__ import annotations

from typing import Any

from app.timegraph.fact_ids import (
    ad_bs_fact_id,
    bs_ad_fact_id,
    fiscal_period_fact_id,
    profile_policy_fact_id,
    working_day_fact_id,
)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def fact_ids_for_date_conversion_result(result: dict[str, Any]) -> list[str]:
    fact_ids: list[str] = []
    gregorian = result.get("gregorian")
    if isinstance(gregorian, str):
        fact_ids.append(ad_bs_fact_id(gregorian))
    bs = result.get("bikram_sambat") or result.get("bs")
    if isinstance(bs, dict):
        try:
            year = int(bs["year"])
            month = int(bs["month"])
            day = int(bs["day"])
            fact_ids.append(bs_ad_fact_id(year, month, day))
            fact_ids.append(fiscal_period_fact_id(year, month, day))
        except (KeyError, TypeError, ValueError):
            pass
    return _dedupe(fact_ids)


def fact_ids_for_compliance_result(result: dict[str, Any]) -> list[str]:
    profile_id = str(result.get("profile_id") or "")
    date_block = result.get("date") if isinstance(result.get("date"), dict) else {}
    bs_date = date_block.get("bs") if isinstance(date_block, dict) else None
    if not profile_id or not isinstance(bs_date, str):
        return []
    try:
        year, month, day = (int(part) for part in bs_date.split("-"))
    except ValueError:
        return [profile_policy_fact_id(profile_id)]
    return [
        profile_policy_fact_id(profile_id),
        working_day_fact_id(profile_id, year, month, day),
        fiscal_period_fact_id(year, month, day),
        bs_ad_fact_id(year, month, day),
    ]
