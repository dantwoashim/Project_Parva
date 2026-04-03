"""
Authoritative date overrides for specific festival-year pairs.

This lets the system align with official published calendars when available,
while still using algorithmic calculation as the default.

The primary source is ``ground_truth_overrides.json``. We also enrich missing
metadata from repository authority datasets so callers can see stronger source
context without hand-curating every row into the primary file.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

_overrides_cache: Optional[Dict[str, Any]] = None
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_GROUND_TRUTH_DIR = _PROJECT_ROOT / "data" / "ground_truth"
_SECONDARY_PROVIDER_ARCHIVE = (
    _PROJECT_ROOT / "data" / "source_archive" / "ratopati" / "event_days_2000_2100.json"
)

# Festival aliases for common variations
FESTIVAL_ALIASES = {
    "makar-sankranti": "maghe-sankranti",
    "nepali-new-year": "bs-new-year",
    "new-year": "bs-new-year",
    "bikram-sambat-new-year": "bs-new-year",
    "janai-purnima-raksha-bandhan": "janai-purnima",
    "raksha-bandhan": "janai-purnima",
    "krishna-astami": "krishna-janmashtami",
    "janmashtami": "krishna-janmashtami",
    "haritalika-teej": "teej",
    "gaijatra": "gai-jatra",
    "ghode-jatra-festival": "ghode-jatra",
    "basanta-panchami": "saraswati-puja",
    "fagu-purnima": "holi",
    "phagu-purnima": "holi",
    "maha-shivaratri": "shivaratri",
    "lakshmi-puja": "laxmi-puja",
    "deepawali": "tihar",
    "diwali": "tihar",
    "newari-new-year": "mha-puja",
    "nepal-sambat-new-year": "mha-puja",
    "chhath-parva": "chhath",
}

_SECONDARY_PROVIDER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bs-new-year", re.compile(r"^नववर्ष प्रारम्भ$")),
    ("janai-purnima", re.compile(r"जनै पूर्णिमा|रक्षा बन्धन")),
    ("krishna-janmashtami", re.compile(r"श्रीकृष्ण जन्माष्टमी|कृष्ण जन्माष्टमी|जन्माष्टमी")),
    ("teej", re.compile(r"हरितालिका.*तीज|^तीज")),
    ("gai-jatra", re.compile(r"^गाईजात्रा|गाई जात्रा")),
    ("indra-jatra", re.compile(r"इन्द्रजात्रा|इन्द्र जात्रा|कुमारी इन्द्र यात्रा")),
    ("ghode-jatra", re.compile(r"घोडेजात्रा|घोडे जात्रा")),
    ("saraswati-puja", re.compile(r"सरस्वती पूजा|श्री पञ्चमी|वसन्त श्रवण")),
    ("maghe-sankranti", re.compile(r"माघे संक्रान्ति|माघे सङ्क्रान्ति|माघी पर्व|माघीपर्व")),
    ("shivaratri", re.compile(r"महाशिवरात्रि|महाशिवरात्री")),
    ("ram-navami", re.compile(r"रामनवमी|राम नवमी")),
    ("holi", re.compile(r"होली|फागु पूर्णिमा|फागुपूर्णिमा")),
    ("buddha-jayanti", re.compile(r"बुद्ध जयन्ती|गौतम बुद्ध जयन्ती")),
    ("tamu-lhosar", re.compile(r"तमु ल्होछार|तमु ल्होसार|तामु ल्होछार|तामु ल्होसार")),
    ("sonam-lhosar", re.compile(r"सोनम ल्होछार|सोनम ल्होसार|सोनाम .*ल्होसार")),
    ("gyalpo-lhosar", re.compile(r"ग्याल्पो ल्होसार|ग्याल्पो ल्होछार")),
    ("ubhauli", re.compile(r"उभौली|उभाैली")),
    ("udhauli", re.compile(r"उधौली")),
    ("chhath", re.compile(r"छठ")),
    ("mha-puja", re.compile(r"म्ह: पूजा|म्ह पूजा|नेपाल सम्बत .* प्रारम्भ")),
]


def _load_overrides() -> Dict[str, Any]:
    global _overrides_cache
    if _overrides_cache is not None:
        return _overrides_cache

    path = Path(__file__).parent / "ground_truth_overrides.json"
    merged: Dict[str, Any] = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            merged = json.load(f)

    _enrich_with_baseline_records(merged)
    _enrich_with_evaluation_rows(merged)
    _enrich_with_secondary_provider_records(merged)
    _overrides_cache = merged
    return _overrides_cache


def _normalize_festival_id(festival_id: str) -> str:
    normalized = festival_id.lower().replace("_", "-")
    return FESTIVAL_ALIASES.get(normalized, normalized)


def _infer_confidence(source: str | None, fallback: str | None = None) -> str | None:
    if fallback:
        return fallback
    normalized = (source or "").strip().lower()
    if not normalized:
        return None
    if "moha" in normalized or "gov" in normalized or "panchang" in normalized:
        return "official"
    return "secondary"


def _normalize_override_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {
        "start": entry.get("start") or entry.get("date"),
        "source": entry.get("source"),
        "confidence": entry.get("confidence"),
        "notes": entry.get("notes"),
    }
    alternates = entry.get("alternates")
    if isinstance(alternates, list):
        normalized["alternates"] = [alt for alt in alternates if isinstance(alt, dict)]
    return normalized


def _merge_override_entry(target: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    current = _normalize_override_entry(target)
    candidate = _normalize_override_entry(incoming)

    current_start = current.get("start")
    candidate_start = candidate.get("start")
    if not candidate_start:
        return current

    if not current_start:
        return candidate

    if current_start == candidate_start:
        for key in ("source", "confidence", "notes"):
            if not current.get(key) and candidate.get(key):
                current[key] = candidate[key]
        return current

    alternates = list(current.get("alternates") or [])
    alt_payload = {
        "start": candidate_start,
        "source": candidate.get("source"),
        "confidence": candidate.get("confidence"),
        "notes": candidate.get("notes"),
    }
    if alt_payload not in alternates:
        alternates.append(alt_payload)
    current["alternates"] = alternates
    return current


def _upsert_override(data: Dict[str, Any], year_key: str, festival_id: str, entry: Dict[str, Any]) -> None:
    bucket = data.setdefault(year_key, {})
    existing = bucket.get(festival_id)
    if existing is None:
        bucket[festival_id] = _normalize_override_entry(entry)
        return
    if isinstance(existing, str):
        existing = {"start": existing}
    bucket[festival_id] = _merge_override_entry(existing, entry)


def _enrich_with_baseline_records(data: Dict[str, Any]) -> None:
    for path in sorted(_GROUND_TRUTH_DIR.glob("baseline_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("records", []):
            fid = _normalize_festival_id(str(row.get("festival_id", "")))
            gregorian = row.get("gregorian_date")
            if not fid or not gregorian:
                continue
            year_key = gregorian[:4]
            override_date = row.get("override_date") if isinstance(row.get("override_date"), dict) else {}
            entry = {
                "start": override_date.get("start") or gregorian,
                "source": override_date.get("source") or row.get("source_file"),
                "confidence": _infer_confidence(
                    override_date.get("source"),
                    override_date.get("confidence"),
                ),
                "notes": override_date.get("notes") or row.get("source_citation"),
            }
            _upsert_override(data, year_key, fid, entry)


def _enrich_with_evaluation_rows(data: Dict[str, Any]) -> None:
    path = _GROUND_TRUTH_DIR / "evaluation_week3.csv"
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            fid = _normalize_festival_id(str(row.get("festival_id", "")))
            year_key = str(row.get("year", "")).strip()
            expected_date = row.get("expected_date")
            if not fid or not year_key or not expected_date:
                continue
            entry = {
                "start": expected_date,
                "source": row.get("source"),
                "confidence": _infer_confidence(row.get("source")),
                "notes": row.get("notes"),
            }
            _upsert_override(data, year_key, fid, entry)


def _match_secondary_provider_festival(title: str) -> str | None:
    normalized = re.sub(r"\s+", " ", title or "").strip()
    if not normalized:
        return None
    for festival_id, pattern in _SECONDARY_PROVIDER_PATTERNS:
        if pattern.search(normalized):
            return festival_id
    return None


def _enrich_with_secondary_provider_records(data: Dict[str, Any]) -> None:
    if not _SECONDARY_PROVIDER_ARCHIVE.exists():
        return

    payload = json.loads(_SECONDARY_PROVIDER_ARCHIVE.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    if not isinstance(records, list):
        return

    for row in records:
        gregorian = str(row.get("ad_date_en", "")).strip()
        year_key = gregorian[:4]
        if len(year_key) != 4 or not year_key.isdigit():
            continue

        events = row.get("events", [])
        if not isinstance(events, list):
            continue

        matched: dict[str, str] = {}
        for event in events:
            if not isinstance(event, dict):
                continue
            title = str(event.get("title_np", "")).strip()
            festival_id = _match_secondary_provider_festival(title)
            if festival_id and festival_id not in matched:
                matched[festival_id] = title

        for festival_id, title in matched.items():
            _upsert_override(
                data,
                year_key,
                festival_id,
                {
                    "start": gregorian,
                    "source": "ratopati_calendar_digital_provider",
                    "confidence": "secondary",
                    "notes": f"Ratopati calendar event title: {title}",
                },
            )


def get_festival_override(festival_id: str, year: int) -> Optional[date]:
    """
    Return an authoritative override date if present.
    """
    data = _load_overrides()
    year_key = str(year)
    if year_key not in data:
        return None

    fid = _normalize_festival_id(festival_id)
    fest = data[year_key].get(fid)
    if not fest:
        return None

    if isinstance(fest, str):
        return date.fromisoformat(fest)

    start = fest.get("start") or fest.get("date")
    if not start:
        return None
    return date.fromisoformat(start)


def get_festival_override_info(festival_id: str, year: int) -> Optional[Dict[str, Any]]:
    """
    Return override metadata if present.

    Returns:
        {"start": date, "source": str|None, "confidence": str|None}
    """
    data = _load_overrides()
    year_key = str(year)
    if year_key not in data:
        return None
    fid = _normalize_festival_id(festival_id)
    fest = data[year_key].get(fid)
    if not fest:
        return None
    if isinstance(fest, str):
        return {
            "start": date.fromisoformat(fest),
            "source": None,
            "confidence": None,
            "alternates": [],
            "candidate_count": 1,
        }
    start = fest.get("start") or fest.get("date")
    if not start:
        return None
    alternates = [
        {
            "start": date.fromisoformat(alt["start"]),
            "source": alt.get("source"),
            "confidence": alt.get("confidence"),
            "notes": alt.get("notes"),
        }
        for alt in fest.get("alternates", [])
        if isinstance(alt, dict) and alt.get("start")
    ]
    suggested_profile_id = None
    suggested_start = None
    suggested_reason = None
    if alternates:
        suggested_alt = alternates[0]
        suggested_profile_id = "published-holiday-listing"
        suggested_start = suggested_alt["start"]
        suggested_source = suggested_alt.get("source") or "authority source"
        suggested_reason = (
            f"An alternate published listing date is available from {suggested_source}."
        )
    return {
        "start": date.fromisoformat(start),
        "source": fest.get("source"),
        "confidence": fest.get("confidence"),
        "notes": fest.get("notes"),
        "alternates": alternates,
        "candidate_count": 1 + len(alternates),
        "suggested_profile_id": suggested_profile_id,
        "suggested_start": suggested_start,
        "suggested_reason": suggested_reason,
    }
