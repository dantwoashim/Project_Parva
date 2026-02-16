"""Rule catalog utilities for canonical v4 festival rules."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from app.rules.schema_v4 import FestivalRuleCatalogV4, FestivalRuleV4

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CALENDAR_DIR = PROJECT_ROOT / "backend" / "app" / "calendar"
DATA_FESTIVALS_PATH = PROJECT_ROOT / "data" / "festivals" / "festivals.json"
REGIONAL_VARIANT_PATH = PROJECT_ROOT / "data" / "variants" / "regional_map.json"
RULES_V3_PATH = CALENDAR_DIR / "festival_rules_v3.json"
RULES_LEGACY_PATH = CALENDAR_DIR / "festival_rules.json"
CATALOG_V4_PATH = PROJECT_ROOT / "data" / "festivals" / "festival_rules_v4.json"
INGESTION_SEED_PATH = PROJECT_ROOT / "data" / "festivals" / "rule_ingestion_seed.json"
INGEST_REPORT_DIR = PROJECT_ROOT / "data" / "ingest_reports"

PAKSHA_TITLE = {
    "shukla": "Shukla",
    "krishna": "Krishna",
}

BS_MONTH_NUMBER_MAP = {
    "वैशाख": 1,
    "जेठ": 2,
    "असार": 3,
    "साउन": 4,
    "श्रावण": 4,
    "भदौ": 5,
    "भाद्र": 5,
    "असोज": 6,
    "आश्विन": 6,
    "कात्तिक": 7,
    "कार्तिक": 7,
    "मङ्सिर": 8,
    "मंसिर": 8,
    "पुस": 9,
    "पौष": 9,
    "माघ": 10,
    "माग": 10,
    "फागुन": 11,
    "फाल्गुण": 11,
    "चैत": 12,
    "चैत्र": 12,
}




def _to_repo_relative(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()

def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    import csv

    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _normalize_regions(rule_data: dict) -> List[str]:
    regions = rule_data.get("regions") or rule_data.get("regional_focus") or []
    if isinstance(regions, str):
        return [regions]
    if isinstance(regions, list):
        return [str(r) for r in regions if str(r).strip()]
    return []


def _resolve_rule_family(rule_type: str, payload: Dict[str, object]) -> str:
    if rule_type == "lunar":
        if payload.get("lunar_month"):
            return "lunar_month_tithi"
        return "lunar_bs_tithi"
    if rule_type == "solar":
        if payload.get("event"):
            return "solar_sankranti"
        if payload.get("solar_day"):
            return "solar_fixed"
        return "solar_month_rule"
    if rule_type == "relative":
        return "relative_offset"
    if rule_type == "transit":
        return "solar_transit"
    if rule_type == "override":
        return "official_override"
    return "unknown"


def _ingestion_seed() -> dict:
    return _load_json(INGESTION_SEED_PATH)


def _safe_int(value: object) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except Exception:
        return None


def _stable_ingested_id(prefix: str, raw: str) -> str:
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def _build_seed_rules(existing_ids: set[str]) -> Dict[str, FestivalRuleV4]:
    seed = _ingestion_seed()
    if not seed:
        return {}

    generated: Dict[str, FestivalRuleV4] = {}

    lunar_months = seed.get("lunar_months", [])
    bs_months = seed.get("bs_months", [])

    for family in seed.get("lunar_dual_paksha_families", []):
        tithi = _safe_int(family.get("tithi"))
        if tithi is None:
            continue
        for month in lunar_months:
            month_name = month.get("name")
            month_slug = month.get("slug")
            if not month_name or not month_slug:
                continue
            for paksha in ("shukla", "krishna"):
                festival_id = f"{family.get('id_prefix')}-{month_slug}-{paksha}"
                if festival_id in existing_ids or festival_id in generated:
                    continue
                generated[festival_id] = FestivalRuleV4(
                    festival_id=festival_id,
                    name_en=family.get("name_template", "{month} Observance").format(
                        month=month_name,
                        paksha=paksha,
                        paksha_title=PAKSHA_TITLE.get(paksha, paksha.title()),
                    ),
                    rule_type="lunar",
                    status="provisional",
                    confidence="low",
                    category=family.get("category", "hindu"),
                    importance="local",
                    tradition=family.get("tradition"),
                    regions=[],
                    rule_family=family.get("rule_family", "generated_lunar_recurring"),
                    source="rule_ingestion_seed_v1",
                    engine="catalog_ingestion_pipeline",
                    notes="Generated recurring observance rule from ingestion seed profile.",
                    tags=["generated", "seed-ingestion", "recurring"],
                    rule={
                        "lunar_month": month_name,
                        "paksha": paksha,
                        "tithi": tithi,
                        "adhik_policy": "skip",
                        "recurrence": "monthly",
                    },
                )

    for family in seed.get("lunar_single_families", []):
        tithi = _safe_int(family.get("tithi"))
        paksha = family.get("paksha")
        if tithi is None or paksha not in {"shukla", "krishna"}:
            continue
        for month in lunar_months:
            month_name = month.get("name")
            month_slug = month.get("slug")
            if not month_name or not month_slug:
                continue
            festival_id = f"{family.get('id_prefix')}-{month_slug}"
            if festival_id in existing_ids or festival_id in generated:
                continue
            generated[festival_id] = FestivalRuleV4(
                festival_id=festival_id,
                name_en=family.get("name_template", "{month} Observance").format(
                    month=month_name,
                    paksha=paksha,
                    paksha_title=PAKSHA_TITLE.get(paksha, paksha.title()),
                ),
                rule_type="lunar",
                status="provisional",
                confidence="low",
                category=family.get("category", "hindu"),
                importance="local",
                tradition=family.get("tradition"),
                regions=[],
                rule_family=family.get("rule_family", "generated_lunar_recurring"),
                source="rule_ingestion_seed_v1",
                engine="catalog_ingestion_pipeline",
                notes="Generated recurring lunar observance from ingestion seed profile.",
                tags=["generated", "seed-ingestion", "monthly"],
                rule={
                    "lunar_month": month_name,
                    "paksha": paksha,
                    "tithi": tithi,
                    "adhik_policy": "skip",
                    "recurrence": "monthly",
                },
            )

    for family in seed.get("solar_monthly_families", []):
        for month in bs_months:
            month_name = month.get("name")
            month_slug = month.get("slug")
            month_number = _safe_int(month.get("number"))
            if not month_name or not month_slug or month_number is None:
                continue
            festival_id = f"{family.get('id_prefix')}-{month_slug}"
            if festival_id in existing_ids or festival_id in generated:
                continue
            generated[festival_id] = FestivalRuleV4(
                festival_id=festival_id,
                name_en=family.get("name_template", "{month} Sankranti").format(month=month_name),
                rule_type="solar",
                status="provisional",
                confidence="low",
                category=family.get("category", "hindu"),
                importance="regional",
                tradition=family.get("tradition"),
                regions=[],
                rule_family=family.get("rule_family", "generated_solar_recurring"),
                source="rule_ingestion_seed_v1",
                engine="catalog_ingestion_pipeline",
                notes="Generated monthly solar observance rule from ingestion seed profile.",
                tags=["generated", "seed-ingestion", "solar"],
                rule={
                    "bs_month": month_number,
                    "event": "sankranti",
                    "recurrence": "monthly",
                },
            )

    for family in seed.get("weekly_monthly_families", []):
        weekday = str(family.get("weekday") or "").strip().lower()
        if not weekday:
            continue
        for month in bs_months:
            month_name = month.get("name")
            month_slug = month.get("slug")
            month_number = _safe_int(month.get("number"))
            if not month_name or not month_slug or month_number is None:
                continue
            festival_id = f"{family.get('id_prefix')}-{month_slug}"
            if festival_id in existing_ids or festival_id in generated:
                continue
            generated[festival_id] = FestivalRuleV4(
                festival_id=festival_id,
                name_en=family.get("name_template", "{month} Weekly Vrata").format(month=month_name),
                rule_type="override",
                status="provisional",
                confidence="low",
                category=family.get("category", "hindu"),
                importance="local",
                tradition=family.get("tradition"),
                regions=[],
                rule_family=family.get("rule_family", "generated_weekly_vrata"),
                source="rule_ingestion_seed_v1",
                engine="catalog_ingestion_pipeline",
                notes="Generated weekly observance inventory rule from ingestion seed profile.",
                tags=["generated", "seed-ingestion", "weekly"],
                rule={
                    "bs_month": month_number,
                    "weekday": weekday,
                    "recurrence": "weekly",
                },
            )

    return generated


def _build_moha_observance_candidates(existing_ids: set[str]) -> Dict[str, FestivalRuleV4]:
    """
    Ingest additional observance candidates from parsed MoHA rows.

    These rows are stored as provisional override rules so they can be curated
    into computed families later without losing source lineage.
    """
    generated: Dict[str, FestivalRuleV4] = {}
    parsed_files = sorted(INGEST_REPORT_DIR.glob("holidays_*_parsed.csv"))
    if not parsed_files:
        return generated

    matched_map: Dict[tuple[str, str], str] = {}
    for matched in sorted(INGEST_REPORT_DIR.glob("holidays_*_matched.csv")):
        rows = _read_csv_rows(matched)
        for row in rows:
            line = str(row.get("line") or "").strip()
            year = str(row.get("bs_year") or "").strip()
            match_id = str(row.get("match_id") or "").strip()
            if line and year and match_id:
                matched_map[(year, line)] = match_id

    for parsed in parsed_files:
        rows = _read_csv_rows(parsed)
        for row in rows:
            year = str(row.get("bs_year") or "").strip()
            line = str(row.get("line") or "").strip()
            if (year, line) in matched_map:
                continue

            raw_name = str(row.get("name_raw") or "").strip()
            month_raw = str(row.get("month_raw") or "").strip()
            day_raw = str(row.get("day_raw") or "").strip()
            if not raw_name:
                continue

            festival_id = _stable_ingested_id("moha-observance", raw_name)
            if festival_id in existing_ids or festival_id in generated:
                continue

            month_number = BS_MONTH_NUMBER_MAP.get(month_raw)
            day_number = _safe_int(day_raw)
            generated[festival_id] = FestivalRuleV4(
                festival_id=festival_id,
                name_en=f"MoHA Observance ({raw_name})",
                name_ne=raw_name,
                rule_type="override",
                status="provisional",
                confidence="low",
                category="national",
                importance="regional",
                tradition="mixed",
                regions=["nepal"],
                rule_family="moha_ingested_observance",
                source="moha_pdf_parsed_ingest",
                engine="catalog_ingestion_pipeline",
                notes="Auto-ingested candidate from parsed MoHA holiday line; awaiting curation.",
                tags=["generated", "moha-ingest", "needs-curation"],
                rule={
                    "bs_year": _safe_int(year),
                    "bs_month": month_number,
                    "bs_day": day_number,
                    "source_line": line,
                },
            )

    return generated


def _load_variant_profile_map() -> tuple[Dict[str, dict], Dict[str, List[str]]]:
    payload = _load_json(REGIONAL_VARIANT_PATH)
    profiles = payload.get("profiles", [])
    profile_map = {
        str(profile.get("profile_id")): profile
        for profile in profiles
        if profile.get("profile_id")
    }

    festival_profile_ids: Dict[str, List[str]] = {}
    for festival_id, variants in payload.get("festival_variants", {}).items():
        ids = sorted(
            {
                str(item.get("profile_id"))
                for item in variants
                if item.get("profile_id")
            }
        )
        festival_profile_ids[festival_id] = ids
    return profile_map, festival_profile_ids


def _add_content_only_rules(merged: Dict[str, FestivalRuleV4]) -> None:
    payload = _load_json(DATA_FESTIVALS_PATH).get("festivals", [])
    for festival in payload:
        festival_id = festival.get("id")
        if not festival_id or festival_id in merged:
            continue
        calendar_type = festival.get("calendar_type") or "lunar"
        merged[festival_id] = FestivalRuleV4(
            festival_id=festival_id,
            name_en=festival.get("name", festival_id),
            name_ne=festival.get("name_nepali"),
            rule_type="override",
            status="provisional",
            confidence="low",
            category=festival.get("category", "hindu"),
            importance="regional",
            tradition=festival.get("who_celebrates"),
            regions=_normalize_regions(festival),
            rule_family="content_inventory",
            source="festival_content_inventory",
            engine="manual",
            notes="Rule not yet encoded in calculator. Derived from festival content inventory.",
            tags=["content-only", "needs-rule-encoding"],
            rule={
                "calendar_type": calendar_type,
                "typical_month_bs": festival.get("typical_month_bs"),
                "duration_days": festival.get("duration_days"),
            },
        )


def _from_v3(festival_id: str, rule_data: dict) -> FestivalRuleV4:
    rule_type = rule_data.get("type", "lunar")
    payload: Dict[str, object]

    if rule_type == "solar":
        payload = {
            "bs_month": rule_data.get("bs_month"),
            "solar_day": rule_data.get("solar_day"),
        }
        if festival_id == "maghe-sankranti":
            payload["event"] = "makara_sankranti"
        elif festival_id == "bs-new-year":
            payload["event"] = "mesh_sankranti"
    else:
        payload = {
            "lunar_month": rule_data.get("lunar_month"),
            "tithi": rule_data.get("tithi"),
            "paksha": rule_data.get("paksha"),
            "adhik_policy": rule_data.get("adhik_policy", "skip"),
        }

    return FestivalRuleV4(
        festival_id=festival_id,
        name_en=rule_data.get("name_en", festival_id),
        name_ne=rule_data.get("name_ne"),
        rule_type=rule_type,
        status="computed",
        confidence="high",
        category=rule_data.get("category", "hindu"),
        importance=rule_data.get("importance", "national"),
        tradition=rule_data.get("tradition"),
        regions=_normalize_regions(rule_data),
        rule_family=_resolve_rule_family(rule_type, payload),
        source="festival_rules_v3",
        engine="v2_lunar_month",
        notes=rule_data.get("notes"),
        tags=["v3", "canonical"],
        rule=payload,
    )


def _from_legacy(festival_id: str, rule_data: dict) -> FestivalRuleV4:
    rule_type = rule_data.get("type", "lunar")
    payload: Dict[str, object]

    if rule_type == "solar":
        payload = {
            "bs_month": rule_data.get("bs_month"),
            "solar_day": rule_data.get("solar_day"),
        }
    else:
        payload = {
            "bs_month": rule_data.get("bs_month"),
            "tithi": rule_data.get("tithi"),
            "paksha": rule_data.get("paksha"),
        }

    return FestivalRuleV4(
        festival_id=festival_id,
        name_en=rule_data.get("name_en", festival_id),
        name_ne=rule_data.get("name_ne"),
        rule_type=rule_type,
        status="provisional",
        confidence="medium",
        category=rule_data.get("category", "hindu"),
        importance=rule_data.get("importance", "national"),
        tradition=rule_data.get("tradition"),
        regions=_normalize_regions(rule_data),
        rule_family=_resolve_rule_family(rule_type, payload),
        source="festival_rules_legacy",
        engine="v1_legacy",
        notes=rule_data.get("notes"),
        tags=["legacy"],
        rule=payload,
    )


def build_canonical_catalog() -> FestivalRuleCatalogV4:
    """Build v4 catalog from v3 + legacy sources.

    Merge strategy:
    - Prefer v3 entries when festival id appears in both.
    - Fill gaps from legacy rules.
    """

    legacy_payload = _load_json(RULES_LEGACY_PATH).get("festivals", {})
    v3_payload = _load_json(RULES_V3_PATH).get("festivals", {})

    merged: Dict[str, FestivalRuleV4] = {}

    for festival_id, rule_data in v3_payload.items():
        merged[festival_id] = _from_v3(festival_id, rule_data)

    for festival_id, rule_data in legacy_payload.items():
        if festival_id in merged:
            continue
        merged[festival_id] = _from_legacy(festival_id, rule_data)

    _add_content_only_rules(merged)
    seed_rules = _build_seed_rules(set(merged.keys()))
    merged.update(seed_rules)
    moha_candidates = _build_moha_observance_candidates(set(merged.keys()))
    merged.update(moha_candidates)

    profile_map, festival_profile_ids = _load_variant_profile_map()
    for festival_id, rule in merged.items():
        profile_ids = festival_profile_ids.get(festival_id, [])
        if profile_ids:
            rule.profile_ids = profile_ids
            rule.has_variant_profiles = True
            rule.tags = sorted(set(rule.tags + ["has-variants"]))
            if rule.rule_family == "unknown":
                rule.rule_family = "profile_variant"
        else:
            rule.profile_ids = []
            rule.has_variant_profiles = False

        if rule.tradition is None and rule.category and rule.category != "national":
            rule.tradition = rule.category

    source_paths = [
        RULES_V3_PATH,
        RULES_LEGACY_PATH,
        DATA_FESTIVALS_PATH,
        INGESTION_SEED_PATH,
    ]
    if profile_map:
        source_paths.append(REGIONAL_VARIANT_PATH)
    if moha_candidates:
        source_paths.append(INGEST_REPORT_DIR)

    source_files = sorted({_to_repo_relative(path) for path in source_paths})

    festivals = sorted(merged.values(), key=lambda item: item.festival_id)

    return FestivalRuleCatalogV4(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_rules=len(festivals),
        source_files=source_files,
        festivals=festivals,
    )


@lru_cache(maxsize=1)
def load_catalog_v4() -> FestivalRuleCatalogV4:
    """Load catalog from disk if present, otherwise build in-memory fallback."""
    if CATALOG_V4_PATH.exists():
        payload = _load_json(CATALOG_V4_PATH)
        try:
            return FestivalRuleCatalogV4.model_validate(payload)
        except Exception:
            pass
    return build_canonical_catalog()


def reload_catalog_v4() -> FestivalRuleCatalogV4:
    """Clear cache and reload catalog."""
    load_catalog_v4.cache_clear()
    return load_catalog_v4()


def list_rules_v4() -> List[FestivalRuleV4]:
    return load_catalog_v4().festivals


def get_rule_v4(festival_id: str) -> Optional[FestivalRuleV4]:
    for rule in list_rules_v4():
        if rule.festival_id == festival_id:
            return rule
    return None


def get_rules_coverage(target: int = 300) -> dict:
    """Compute rule coverage summary against plan target."""
    rules = list_rules_v4()

    type_counts = Counter(rule.rule_type for rule in rules)
    status_counts = Counter(rule.status for rule in rules)
    source_counts = Counter(rule.source for rule in rules)
    engine_counts = Counter(rule.engine for rule in rules)
    family_counts = Counter(rule.rule_family for rule in rules)
    profiled_rules = [rule for rule in rules if rule.has_variant_profiles]
    profile_ids = sorted({pid for rule in rules for pid in rule.profile_ids})

    total = len(rules)
    pct = round((total / target) * 100, 2) if target > 0 else 0.0
    profile_pct = round((len(profiled_rules) / total) * 100, 2) if total > 0 else 0.0

    return {
        "target_rules": target,
        "total_rules": total,
        "coverage_pct": pct,
        "remaining_to_target": max(target - total, 0),
        "by_type": dict(type_counts),
        "by_status": dict(status_counts),
        "by_source": dict(source_counts),
        "by_engine": dict(engine_counts),
        "by_rule_family": dict(family_counts),
        "computed_rules": status_counts.get("computed", 0),
        "override_rules": status_counts.get("override", 0),
        "provisional_rules": status_counts.get("provisional", 0),
        "rules_with_variant_profiles": len(profiled_rules),
        "variant_profile_coverage_pct": profile_pct,
        "variant_profiles_present": profile_ids,
        "sample_festival_ids": [rule.festival_id for rule in rules[:10]],
        "catalog_generated_at": load_catalog_v4().generated_at,
    }
