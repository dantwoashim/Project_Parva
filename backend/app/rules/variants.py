"""Regional observance variant support."""

from __future__ import annotations

from datetime import timedelta
from functools import lru_cache
from pathlib import Path
import json

from app.rules import get_rule_service


VARIANT_FILE = Path(__file__).resolve().parents[3] / "data" / "variants" / "regional_map.json"


@lru_cache(maxsize=1)
def _load_variant_payload() -> dict:
    if not VARIANT_FILE.exists():
        return {"profiles": [], "festival_variants": {}}
    return json.loads(VARIANT_FILE.read_text(encoding="utf-8"))


def list_profiles() -> list[dict]:
    return _load_variant_payload().get("profiles", [])


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
        offset = int(rule.get("offset_days", 0))
        start = primary.start_date + timedelta(days=offset)
        end = primary.end_date + timedelta(days=offset)
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
            }
        )

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
            }
        )

    return variants


def filter_variants_by_profile(variants: list[dict], profile_id: str | None) -> list[dict]:
    """Filter variants by profile id when provided."""
    if not profile_id:
        return variants
    return [v for v in variants if v.get("profile_id") == profile_id]
