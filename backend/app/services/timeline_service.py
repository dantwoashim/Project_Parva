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
VALID_SORTS = {"chronological", "recommended", "popular"}
SORT_ALIASES = {
    "upcoming": "chronological",
}

POPULARITY_RANKS = {
    "dashain": 100,
    "tihar": 98,
    "diwali": 97,
    "holi": 95,
    "shivaratri": 93,
    "buddha-jayanti": 92,
    "buddha_jayanti": 92,
    "teej": 90,
    "janai-purnima": 88,
    "indra-jatra": 86,
    "indra_jatra": 86,
}

CATEGORY_PRIORITIES = {
    "national": 4,
    "newari": 3,
    "buddhist": 3,
    "regional": 2,
    "hindu": 1,
}


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


def _serialize_timeline_item(*, festival, dates, lang: str, band: str, rule) -> dict:
    return {
        "id": festival.id,
        "name": festival.name,
        "name_nepali": festival.name_nepali,
        "display_name": _display_name(festival, lang=lang),
        "category": festival.category,
        "start_date": dates.start_date.isoformat(),
        "end_date": dates.end_date.isoformat(),
        "bs_start": _to_bs_struct(dates.start_date),
        "bs_end": _to_bs_struct(dates.end_date),
        "duration_days": dates.duration_days,
        "quality_band": band,
        "rule_status": getattr(rule, "status", "inventory"),
        "algorithmic": bool(rule_has_algorithm(rule)) if rule else False,
        "ritual_preview": ritual_preview(festival),
        "summary": festival.tagline or festival.description or ritual_preview(festival),
        "regional_focus": festival.regional_focus or [],
    }


def _build_facets(items: list[dict]) -> dict:
    category_counts: OrderedDict[str, int] = OrderedDict()
    month_counts: OrderedDict[str, dict] = OrderedDict()
    region_counts: OrderedDict[str, int] = OrderedDict()

    for item in items:
        category = item.get("category") or "other"
        category_counts[category] = category_counts.get(category, 0) + 1

        month_key = item["start_date"][:7]
        month_entry = month_counts.get(month_key)
        if not month_entry:
            month_entry = {
                "value": month_key,
                "label": date.fromisoformat(item["start_date"]).strftime("%B"),
                "count": 0,
            }
            month_counts[month_key] = month_entry
        month_entry["count"] += 1

        for region in item.get("regional_focus") or []:
            region_counts[region] = region_counts.get(region, 0) + 1

    return {
        "categories": [
            {"value": value, "label": value.replace("_", " ").title(), "count": count}
            for value, count in category_counts.items()
        ],
        "months": list(month_counts.values()),
        "regions": [
            {"value": value, "label": value, "count": count}
            for value, count in region_counts.items()
        ],
    }


def _sort_items(items: list[dict], sort: str) -> list[dict]:
    if sort == "popular":
        return sorted(
            items,
            key=lambda row: (
                -POPULARITY_RANKS.get(row["id"], 0),
                row["start_date"],
                row["display_name"],
            ),
        )

    if sort == "recommended":
        return sorted(
            items,
            key=lambda row: (
                -int(bool(row.get("algorithmic"))),
                -CATEGORY_PRIORITIES.get(row.get("category"), 0),
                -int(row.get("duration_days") or 1),
                row["start_date"],
                row["display_name"],
            ),
        )

    return sorted(
        items,
        key=lambda row: (row["start_date"], -int(row.get("duration_days") or 1), row["display_name"]),
    )


def build_festival_timeline(
    *,
    from_date: date,
    to_date: date,
    quality_band: str,
    category: str | None,
    region: str | None,
    search: str | None,
    lang: str,
    sort: str = "chronological",
) -> dict:
    if from_date > to_date:
        raise ValueError("'from' date must be <= 'to' date")

    normalized_band = (quality_band or "computed").strip().lower()
    if normalized_band not in VALID_BANDS:
        raise ValueError(f"Invalid quality_band '{quality_band}'")

    normalized_sort = (sort or "chronological").strip().lower()
    normalized_sort = SORT_ALIASES.get(normalized_sort, normalized_sort)
    if normalized_sort not in VALID_SORTS:
        raise ValueError(f"Invalid sort '{sort}'")

    cache_key = (
        f"timeline:{from_date.isoformat()}:{to_date.isoformat()}:{normalized_band}:"
        f"{(category or '').lower()}:{(region or '').lower()}:{(search or '').lower()}:{lang}:{normalized_sort}"
    )

    def _compute() -> dict:
        repo = get_repository()
        rule_service = get_rule_service()

        total_days = (to_date - from_date).days + 1
        upcoming = rule_service.upcoming(from_date, days=total_days)

        base_items: list[dict] = []
        for festival_id, dates in upcoming:
            festival = repo.get_by_id(festival_id)
            if not festival:
                continue
            if not _match_search(festival, search):
                continue

            rule = get_rule_v4(festival_id)
            band = rule_quality_band(rule) if rule else "inventory"
            if normalized_band != "all" and band != normalized_band:
                continue

            if dates.end_date < from_date or dates.start_date > to_date:
                continue

            base_items.append(
                _serialize_timeline_item(
                    festival=festival,
                    dates=dates,
                    lang=lang,
                    band=band,
                    rule=rule,
                )
            )

        facets = _build_facets(base_items)

        filtered_items = [
            item for item in base_items
            if (not category or item.get("category") == category)
            and (
                not region
                or any(region.strip().lower() in entry.lower() for entry in (item.get("regional_focus") or []))
            )
        ]
        items = _sort_items(filtered_items, normalized_sort)

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
            "sort": normalized_sort,
            "total": len(items),
            "groups": list(groups.values()),
            "facets": facets,
        }

    return cached(cache_key, ttl_seconds=240, compute=_compute)
