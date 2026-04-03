"""Regional observance variant support."""

from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.calendar.overrides import get_festival_override_info
from app.rules import get_rule_service

VARIANT_FILE = Path(__file__).resolve().parents[3] / "data" / "variants" / "regional_map.json"


@lru_cache(maxsize=1)
def _load_variant_payload() -> dict:
    if not VARIANT_FILE.exists():
        return {"profiles": [], "festival_variants": {}}
    return json.loads(VARIANT_FILE.read_text(encoding="utf-8"))


def list_profiles() -> list[dict]:
    return _load_variant_payload().get("profiles", [])


def _coerce_year(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _rule_applies_to_year(rule: dict[str, Any], year: int) -> bool:
    years = rule.get("years")
    if isinstance(years, list) and years:
        allowed_years: set[int] = set()
        for value in years:
            parsed_year = _coerce_year(value)
            if parsed_year is None:
                continue
            allowed_years = allowed_years | {parsed_year}
        if allowed_years and year not in allowed_years:
            return False

    start_year = rule.get("start_year")
    if start_year is not None:
        parsed_start_year = _coerce_year(start_year)
        if parsed_start_year is not None and year < parsed_start_year:
            return False

    end_year = rule.get("end_year")
    if end_year is not None:
        parsed_end_year = _coerce_year(end_year)
        if parsed_end_year is not None and year > parsed_end_year:
            return False

    return True


def _resolve_variant_window(primary, rule: dict[str, Any]) -> tuple:
    start = primary.start_date
    end = primary.end_date

    absolute_start = rule.get("absolute_date") or rule.get("date")
    absolute_end = rule.get("absolute_end_date") or rule.get("end_date")
    duration_days = rule.get("duration_days")

    if absolute_start:
        start = date.fromisoformat(str(absolute_start))
        if absolute_end:
            end = date.fromisoformat(str(absolute_end))
        elif duration_days is not None:
            try:
                end = start + timedelta(days=max(int(duration_days) - 1, 0))
            except (TypeError, ValueError):
                end = start + (primary.end_date - primary.start_date)
        else:
            end = start + (primary.end_date - primary.start_date)
        return start, end

    offset = int(rule.get("offset_days", 0))
    start = primary.start_date + timedelta(days=offset)
    end = primary.end_date + timedelta(days=offset)
    return start, end


def _derive_authority_variants(
    festival_id: str,
    year: int,
    profile_map: dict[str, dict],
    existing_profile_ids: set[str],
) -> list[dict]:
    info = get_festival_override_info(festival_id, year)
    if not info:
        return []

    profile_id = "published-holiday-listing"
    if profile_id in existing_profile_ids or profile_id not in profile_map:
        return []

    variants = []
    for alternate in info.get("alternates", []):
        start = alternate.get("start")
        if start is None:
            continue
        source = alternate.get("source")
        note = (
            f"Uses an alternate authority-backed listing candidate from "
            f"{source or 'the ground-truth dataset'}."
        )
        if alternate.get("notes"):
            note = f"{note} {alternate['notes']}"
        profile = profile_map.get(profile_id, {})
        variants.append(
            {
                "festival_id": festival_id,
                "year": year,
                "date": start.isoformat(),
                "end_date": start.isoformat(),
                "profile_id": profile_id,
                "tradition": profile.get("tradition"),
                "region": profile.get("region"),
                "confidence": alternate.get("confidence") or "high",
                "rule_used": "authority alternate candidate",
                "notes": note,
                "years": [year],
                "start_year": year,
                "end_year": year,
                "auto_generated": True,
                "source": source,
            }
        )
    return variants


def calculate_with_variants(festival_id: str, year: int) -> list[dict]:
    svc = get_rule_service()
    primary = svc.calculate(festival_id, year)
    if not primary:
        return []

    payload = _load_variant_payload()
    profile_map = {p["profile_id"]: p for p in payload.get("profiles", [])}
    rules = payload.get("festival_variants", {}).get(festival_id, [])

    variants = []
    for rule in rules:
        if not _rule_applies_to_year(rule, year):
            continue

        start, end = _resolve_variant_window(primary, rule)
        profile_id = rule.get("profile_id")
        profile = profile_map.get(profile_id, {})
        variants.append(
            {
                "festival_id": festival_id,
                "year": year,
                "date": start.isoformat(),
                "end_date": end.isoformat(),
                "profile_id": profile_id,
                "tradition": profile.get("tradition"),
                "region": profile.get("region"),
                "confidence": rule.get("confidence", "computed"),
                "rule_used": rule.get("rule_used"),
                "notes": rule.get("notes"),
                "years": rule.get("years"),
                "start_year": rule.get("start_year"),
                "end_year": rule.get("end_year"),
                "auto_generated": False,
            }
        )

    existing_profile_ids = {str(item.get("profile_id")) for item in variants if item.get("profile_id")}
    variants.extend(_derive_authority_variants(festival_id, year, profile_map, existing_profile_ids))

    if not variants:
        variants.append(
            {
                "festival_id": festival_id,
                "year": year,
                "date": primary.start_date.isoformat(),
                "end_date": primary.end_date.isoformat(),
                "profile_id": "np-mainstream",
                "tradition": "Nepali Mainstream",
                "region": "Nepal",
                "confidence": "computed",
                "rule_used": primary.method,
                "notes": "No alternate variant documented yet.",
                "auto_generated": False,
            }
        )

    return variants


def filter_variants_by_profile(variants: list[dict], profile_id: str | None) -> list[dict]:
    """Filter variants by profile id when provided."""
    if not profile_id:
        return variants
    return [v for v in variants if v.get("profile_id") == profile_id]
