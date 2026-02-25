"""Festival timeline aggregation for ribbon-style browsing."""

from __future__ import annotations

from collections import OrderedDict
from datetime import date

from app.calendar import get_bs_month_name, gregorian_to_bs
from app.festivals.repository import get_repository
from app.rules import get_rule_service
from app.rules.catalog_v4 import get_rule_v4, rule_has_algorithm, rule_quality_band
from app.services.ritual_normalization import ritual_preview

from .runtime_cache import cached

VALID_BANDS = {"computed", "provisional", "inventory", "all"}


def _match_region(festival, region: str | None) -> bool:
    if not region:
        return True
    region_l = region.strip().lower()
    return any(region_l in (entry or "").lower() for entry in (festival.regional_focus or []))


def _display_name(festival, *, lang: str) -> str:
    if lang == "ne" and festival.name_nepali:
        return festival.name_nepali
    return festival.name


def _match_search(festival, search: str | None) -> bool:
    if not search:
        return True
    q = search.strip().lower()
    if not q:
        return True
    haystacks = [
        festival.name,
        festival.name_nepali,
        festival.tagline,
        festival.description,
    ]
    for value in haystacks:
        if value and q in value.lower():
            return True
    return False


def _to_bs_struct(d: date) -> dict:
    bs_year, bs_month, bs_day = gregorian_to_bs(d)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": get_bs_month_name(bs_month),
        "formatted": f"{bs_year} {get_bs_month_name(bs_month)} {bs_day}",
    }


def build_festival_timeline(
    *,
    from_date: date,
    to_date: date,
    quality_band: str,
    category: str | None,
    region: str | None,
    search: str | None,
    lang: str,
) -> dict:
    if from_date > to_date:
        raise ValueError("'from' date must be <= 'to' date")

    normalized_band = (quality_band or "computed").strip().lower()
    if normalized_band not in VALID_BANDS:
        raise ValueError(f"Invalid quality_band '{quality_band}'")

    cache_key = (
        f"timeline:{from_date.isoformat()}:{to_date.isoformat()}:{normalized_band}:"
        f"{(category or '').lower()}:{(region or '').lower()}:{(search or '').lower()}:{lang}"
    )

    def _compute() -> dict:
        repo = get_repository()
        rule_service = get_rule_service()

        total_days = (to_date - from_date).days + 1
        upcoming = rule_service.upcoming(from_date, days=total_days)

        items: list[dict] = []
        for festival_id, dates in upcoming:
            festival = repo.get_by_id(festival_id)
            if not festival:
                continue
            if category and festival.category != category:
                continue
            if not _match_region(festival, region):
                continue
            if not _match_search(festival, search):
                continue

            rule = get_rule_v4(festival_id)
            band = rule_quality_band(rule) if rule else "inventory"
            if normalized_band != "all" and band != normalized_band:
                continue

            if dates.end_date < from_date or dates.start_date > to_date:
                continue

            bs_start = _to_bs_struct(dates.start_date)
            bs_end = _to_bs_struct(dates.end_date)

            items.append(
                {
                    "id": festival.id,
                    "name": festival.name,
                    "name_nepali": festival.name_nepali,
                    "display_name": _display_name(festival, lang=lang),
                    "category": festival.category,
                    "start_date": dates.start_date.isoformat(),
                    "end_date": dates.end_date.isoformat(),
                    "bs_start": bs_start,
                    "bs_end": bs_end,
                    "duration_days": dates.duration_days,
                    "quality_band": band,
                    "rule_status": getattr(rule, "status", "inventory"),
                    "algorithmic": bool(rule_has_algorithm(rule)) if rule else False,
                    "ritual_preview": ritual_preview(festival),
                }
            )

        items.sort(key=lambda row: (row["start_date"], -int(row.get("duration_days") or 1), row["name"]))

        groups: OrderedDict[str, dict] = OrderedDict()
        for item in items:
            month_key = item["start_date"][:7]
            month_label = date.fromisoformat(item["start_date"]).strftime("%B %Y")
            if month_key not in groups:
                groups[month_key] = {
                    "month_key": month_key,
                    "month_label": month_label,
                    "items": [],
                }
            groups[month_key]["items"].append(item)

        return {
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "quality_band": normalized_band,
            "category": category,
            "region": region,
            "search": search,
            "lang": lang,
            "total": len(items),
            "groups": list(groups.values()),
        }

    return cached(cache_key, ttl_seconds=240, compute=_compute)
