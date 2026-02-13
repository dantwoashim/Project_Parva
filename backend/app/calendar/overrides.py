"""
Authoritative date overrides for specific festival-year pairs.

This lets the system align with official published calendars when available,
while still using algorithmic calculation as the default.
"""

from datetime import date
from pathlib import Path
from typing import Optional, Dict, Any
import json

_overrides_cache: Optional[Dict[str, Any]] = None

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


def _load_overrides() -> Dict[str, Any]:
    global _overrides_cache
    if _overrides_cache is not None:
        return _overrides_cache
    
    path = Path(__file__).parent / "ground_truth_overrides.json"
    if not path.exists():
        _overrides_cache = {}
        return _overrides_cache
    
    with open(path, "r", encoding="utf-8") as f:
        _overrides_cache = json.load(f)
    return _overrides_cache


def _normalize_festival_id(festival_id: str) -> str:
    normalized = festival_id.lower().replace("_", "-")
    return FESTIVAL_ALIASES.get(normalized, normalized)


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
        return {"start": date.fromisoformat(fest), "source": None, "confidence": None}
    start = fest.get("start") or fest.get("date")
    if not start:
        return None
    return {
        "start": date.fromisoformat(start),
        "source": fest.get("source"),
        "confidence": fest.get("confidence"),
    }
