"""
Festival Rules Loader for Project Parva v2.0

Loads festival rules from festival_rules.json and converts them to CalendarRule objects.
This replaces the hardcoded FESTIVAL_RULES in calculator.py.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Literal

from pydantic import BaseModel, ConfigDict


class CalendarRule(BaseModel):
    """Rule for calculating festival dates (matches calculator.py)."""
    calendar_type: Literal["solar", "lunar"]
    bs_month: int
    tithi: Optional[int] = None
    paksha: Optional[Literal["shukla", "krishna"]] = None
    solar_day: Optional[int] = None
    duration: int = 1
    notes: Optional[str] = None
    
    model_config = ConfigDict(frozen=True)


# Cache for loaded rules
_cached_rules: Optional[Dict[str, CalendarRule]] = None


def _get_rules_path() -> Path:
    """Get path to festival_rules.json."""
    return Path(__file__).parent / "festival_rules.json"


def load_festival_rules() -> Dict[str, CalendarRule]:
    """
    Load festival rules from JSON file.
    
    Returns:
        Dictionary of festival_id -> CalendarRule
    
    Uses caching to avoid repeated file reads.
    """
    global _cached_rules
    
    if _cached_rules is not None:
        return _cached_rules
    
    rules_path = _get_rules_path()
    
    if not rules_path.exists():
        raise FileNotFoundError(f"Festival rules not found: {rules_path}")
    
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rules = {}
    for festival_id, rule_data in data.get("festivals", {}).items():
        # Convert JSON format to CalendarRule
        rules[festival_id] = CalendarRule(
            calendar_type=rule_data.get("type", "lunar"),
            bs_month=rule_data.get("bs_month", 1),
            tithi=rule_data.get("tithi"),
            paksha=rule_data.get("paksha"),
            solar_day=rule_data.get("solar_day"),
            duration=rule_data.get("duration_days", 1),
            notes=rule_data.get("notes"),
        )
    
    _cached_rules = rules
    return rules


def get_festival_rule(festival_id: str) -> CalendarRule:
    """
    Get the calculation rule for a specific festival.
    
    Args:
        festival_id: Festival identifier (e.g., "dashain", "tihar")
    
    Returns:
        CalendarRule for the festival
    
    Raises:
        KeyError: If festival not found
    """
    rules = load_festival_rules()
    
    if festival_id not in rules:
        raise KeyError(f"Unknown festival: {festival_id}")
    
    return rules[festival_id]


def list_festivals() -> list:
    """
    List all available festival IDs.
    
    Returns:
        List of festival ID strings
    """
    rules = load_festival_rules()
    return list(rules.keys())


def reload_rules():
    """Force reload of festival rules from disk."""
    global _cached_rules
    _cached_rules = None
    return load_festival_rules()


def get_festival_metadata(festival_id: str) -> Dict[str, Any]:
    """
    Get full metadata for a festival from JSON.
    
    Returns more info than just the CalendarRule (names, category, etc.)
    """
    rules_path = _get_rules_path()
    
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    festivals = data.get("festivals", {})
    
    if festival_id not in festivals:
        raise KeyError(f"Unknown festival: {festival_id}")
    
    return festivals[festival_id]
