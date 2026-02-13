"""
Locations Repository
====================

Data access layer for temples and locations.
"""

import json
from pathlib import Path
from typing import Optional, List
from functools import lru_cache

from .models import Temple, TempleSummary, Coordinates


# Path to data files
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "festivals"


@lru_cache(maxsize=1)
def _load_temples_data() -> dict:
    """Load temples from JSON file with caching."""
    temples_file = DATA_DIR / "temples.json"
    if temples_file.exists():
        with open(temples_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"temples": []}


@lru_cache(maxsize=1)
def _load_location_mappings() -> dict:
    """Load festival-location mappings from JSON file."""
    mappings_file = DATA_DIR / "festival_locations.json"
    if mappings_file.exists():
        with open(mappings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mappings": {}}


def reload_data():
    """Clear caches and reload data."""
    _load_temples_data.cache_clear()
    _load_location_mappings.cache_clear()


def get_all_temples() -> list[Temple]:
    """Get all temples."""
    data = _load_temples_data()
    temples = []
    for t in data.get("temples", []):
        temples.append(Temple(
            id=t["id"],
            name=t["name"],
            name_ne=t.get("name_ne"),
            type=t["type"],
            deity=t.get("deity"),
            coordinates=Coordinates(**t["coordinates"]),
            significance=t.get("significance"),
            festivals=t.get("festivals", []),
            description=t.get("description"),
            visiting_hours=t.get("visiting_hours"),
            entry_fee=t.get("entry_fee"),
        ))
    return temples


def get_temple_by_id(temple_id: str) -> Optional[Temple]:
    """Get a single temple by ID."""
    temples = get_all_temples()
    for t in temples:
        if t.id == temple_id:
            return t
    return None


def get_temples_by_festival(festival_id: str) -> list[Temple]:
    """Get all temples associated with a festival."""
    mappings = _load_location_mappings()
    festival_mapping = mappings.get("mappings", {}).get(festival_id, {})
    primary_ids = festival_mapping.get("primary", [])
    
    temples = get_all_temples()
    result = []
    for t in temples:
        if t.id in primary_ids or festival_id in t.festivals:
            result.append(t)
    return result


def get_temples_in_bounds(
    min_lat: float, min_lng: float,
    max_lat: float, max_lng: float
) -> list[Temple]:
    """Get temples within geographic bounds."""
    temples = get_all_temples()
    result = []
    for t in temples:
        if (min_lat <= t.coordinates.lat <= max_lat and
            min_lng <= t.coordinates.lng <= max_lng):
            result.append(t)
    return result


def get_temple_summaries() -> list[TempleSummary]:
    """Get summary list of all temples."""
    temples = get_all_temples()
    return [
        TempleSummary(
            id=t.id,
            name=t.name,
            name_ne=t.name_ne,
            type=t.type,
            deity=t.deity,
            coordinates=t.coordinates,
            festival_count=len(t.festivals),
            festivals=t.festivals,
        )
        for t in temples
    ]


def get_location_role(festival_id: str, temple_id: str) -> Optional[str]:
    """Get the role/description of a temple for a specific festival."""
    mappings = _load_location_mappings()
    festival_mapping = mappings.get("mappings", {}).get(festival_id, {})
    return festival_mapping.get("roles", {}).get(temple_id)


def get_festivals_at_temple(temple_id: str) -> list[str]:
    """Get list of festival IDs celebrated at a temple."""
    temple = get_temple_by_id(temple_id)
    if temple:
        return temple.festivals
    return []
