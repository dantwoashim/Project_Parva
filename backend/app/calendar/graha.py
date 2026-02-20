"""Navagraha position helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import swisseph as swe

from app.engine.ephemeris_config import get_ephemeris_config
from app.calendar.ephemeris.swiss_eph import _ensure_initialized, get_julian_day

RASHI_NAMES = [
    ("Mesha", "Aries"),
    ("Vrishabha", "Taurus"),
    ("Mithuna", "Gemini"),
    ("Karka", "Cancer"),
    ("Simha", "Leo"),
    ("Kanya", "Virgo"),
    ("Tula", "Libra"),
    ("Vrischika", "Scorpio"),
    ("Dhanu", "Sagittarius"),
    ("Makara", "Capricorn"),
    ("Kumbha", "Aquarius"),
    ("Meena", "Pisces"),
]

PLANET_ORDER = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
}

GRAHA_LABELS = {
    "sun": {"sanskrit": "Surya", "english": "Sun"},
    "moon": {"sanskrit": "Chandra", "english": "Moon"},
    "mars": {"sanskrit": "Mangal", "english": "Mars"},
    "mercury": {"sanskrit": "Budha", "english": "Mercury"},
    "jupiter": {"sanskrit": "Guru", "english": "Jupiter"},
    "venus": {"sanskrit": "Shukra", "english": "Venus"},
    "saturn": {"sanskrit": "Shani", "english": "Saturn"},
    "rahu": {"sanskrit": "Rahu", "english": "North Node"},
    "ketu": {"sanskrit": "Ketu", "english": "South Node"},
}



def _format_position(longitude: float, speed: float, *, graha_id: str) -> dict[str, Any]:
    rashi_idx = int(longitude / 30)
    rashi_sanskrit, rashi_english = RASHI_NAMES[rashi_idx]
    labels = GRAHA_LABELS[graha_id]
    return {
        "id": graha_id,
        "name_sanskrit": labels["sanskrit"],
        "name_english": labels["english"],
        "longitude": round(longitude, 6),
        "degree_in_rashi": round(longitude % 30, 4),
        "rashi_number": rashi_idx + 1,
        "rashi_sanskrit": rashi_sanskrit,
        "rashi_english": rashi_english,
        "speed": round(speed, 8),
        "is_retrograde": speed < 0,
    }



def get_all_graha_positions(dt: datetime, *, sidereal: bool = True) -> dict[str, Any]:
    """Return 9 graha positions for the given datetime."""
    _ensure_initialized()
    jd = get_julian_day(dt)
    cfg = get_ephemeris_config()

    flags = swe.FLG_SPEED
    if sidereal:
        swe.set_sid_mode(cfg.ayanamsa_code)
        flags |= swe.FLG_SIDEREAL

    positions: dict[str, Any] = {}

    for graha_id, swe_body in PLANET_ORDER.items():
        result = swe.calc_ut(jd, swe_body, flags)
        longitude = result[0][0] % 360
        speed = result[0][3]
        positions[graha_id] = _format_position(longitude, speed, graha_id=graha_id)

    node = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu_long = node[0][0] % 360
    rahu_speed = node[0][3]
    positions["rahu"] = _format_position(rahu_long, rahu_speed, graha_id="rahu")
    positions["rahu"]["is_retrograde"] = True

    ketu_long = (rahu_long + 180.0) % 360
    positions["ketu"] = _format_position(ketu_long, rahu_speed, graha_id="ketu")
    positions["ketu"]["is_retrograde"] = True

    return positions



def get_graha_position(dt: datetime, graha_id: str, *, sidereal: bool = True) -> dict[str, Any]:
    """Return single graha position."""
    positions = get_all_graha_positions(dt, sidereal=sidereal)
    if graha_id not in positions:
        raise ValueError(f"Unknown graha '{graha_id}'")
    return positions[graha_id]
