"""Vedic kundali calculations (D1, D9, lagna, aspects, yogas, dosha, dasha v2)."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import swisseph as swe

from app.calendar.graha import RASHI_NAMES, get_all_graha_positions
from app.calendar.ephemeris.swiss_eph import _ensure_initialized, get_ayanamsa, get_julian_day

DASHA_SEQUENCE = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
DASHA_YEARS = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}

SIGN_LORD = {
    1: "mars",
    2: "venus",
    3: "mercury",
    4: "moon",
    5: "sun",
    6: "mercury",
    7: "venus",
    8: "mars",
    9: "jupiter",
    10: "saturn",
    11: "saturn",
    12: "jupiter",
}

EXALTATION_SIGNS = {
    "sun": 1,
    "moon": 2,
    "mars": 10,
    "mercury": 6,
    "jupiter": 4,
    "venus": 12,
    "saturn": 7,
    "rahu": 2,
    "ketu": 8,
}

DEBILITATION_SIGNS = {
    "sun": 7,
    "moon": 8,
    "mars": 4,
    "mercury": 12,
    "jupiter": 10,
    "venus": 6,
    "saturn": 1,
    "rahu": 8,
    "ketu": 2,
}

OWN_SIGNS = {
    "sun": {5},
    "moon": {4},
    "mars": {1, 8},
    "mercury": {3, 6},
    "jupiter": {9, 12},
    "venus": {2, 7},
    "saturn": {10, 11},
    "rahu": set(),
    "ketu": set(),
}

GRAHA_ASPECTS = {
    "sun": [7],
    "moon": [7],
    "mars": [4, 7, 8],
    "mercury": [7],
    "jupiter": [5, 7, 9],
    "venus": [7],
    "saturn": [3, 7, 10],
    "rahu": [5, 7, 9],
    "ketu": [5, 7, 9],
}

PRIMARY_GRAHAS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]


def _ensure_datetime_with_tz(dt: datetime, tz_name: str) -> datetime:
    if dt.tzinfo is not None:
        return dt
    return dt.replace(tzinfo=ZoneInfo(tz_name))


def _lagna(dt: datetime, *, lat: float, lon: float) -> dict[str, Any]:
    _ensure_initialized()
    utc_dt = dt.astimezone(ZoneInfo("UTC"))
    jd = get_julian_day(utc_dt)

    cusps, ascmc = swe.houses(jd, lat, lon, b"W")
    tropical_asc = ascmc[0]
    sidereal_asc = (tropical_asc - get_ayanamsa(utc_dt)) % 360

    rashi_idx = int(sidereal_asc / 30)
    rashi_sanskrit, rashi_english = RASHI_NAMES[rashi_idx]

    return {
        "longitude": round(sidereal_asc, 6),
        "rashi_number": rashi_idx + 1,
        "rashi_sanskrit": rashi_sanskrit,
        "rashi_english": rashi_english,
        "degree_in_rashi": round(sidereal_asc % 30, 4),
        "method": "swiss_ephemeris_sidereal",
    }


def _whole_sign_houses(lagna_rashi: int, grahas: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    houses: list[dict[str, Any]] = []
    for i in range(12):
        rashi_idx = (lagna_rashi - 1 + i) % 12
        occupants = [
            name for name, pos in grahas.items() if isinstance(pos, dict) and pos.get("rashi_number") == rashi_idx + 1
        ]
        houses.append(
            {
                "house_number": i + 1,
                "rashi_number": rashi_idx + 1,
                "rashi_sanskrit": RASHI_NAMES[rashi_idx][0],
                "rashi_english": RASHI_NAMES[rashi_idx][1],
                "occupants": occupants,
            }
        )
    return houses


def _d9_chart(grahas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    d9: dict[str, dict[str, Any]] = {}
    for name, pos in grahas.items():
        longitude = float(pos["longitude"])
        navamsa_sign = int((longitude * 9) // 30) % 12
        d9[name] = {
            "longitude": longitude,
            "navamsa_rashi_number": navamsa_sign + 1,
            "navamsa_rashi_sanskrit": RASHI_NAMES[navamsa_sign][0],
            "navamsa_rashi_english": RASHI_NAMES[navamsa_sign][1],
        }
    return d9


def _dignity_for_graha(graha_id: str, rashi_number: int) -> dict[str, Any]:
    if rashi_number == EXALTATION_SIGNS.get(graha_id):
        return {"state": "exalted", "strength": "strong"}
    if rashi_number == DEBILITATION_SIGNS.get(graha_id):
        return {"state": "debilitated", "strength": "weak"}
    if rashi_number in OWN_SIGNS.get(graha_id, set()):
        return {"state": "own_sign", "strength": "strong"}
    return {"state": "neutral", "strength": "moderate"}


def _augment_dignities(grahas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for graha_id, row in grahas.items():
        dignity = _dignity_for_graha(graha_id, int(row["rashi_number"]))
        out[graha_id] = {**row, "dignity": dignity}
    return out


def _angular_diff(a: float, b: float) -> float:
    d = abs((a - b) % 360)
    return min(d, 360 - d)


def _target_angle(sign_distance: int) -> float:
    return ((sign_distance - 1) * 30) % 360


def _compute_aspects(grahas: dict[str, dict[str, Any]], *, orb_degrees: float = 6.0) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in PRIMARY_GRAHAS:
        src = grahas[source]
        src_long = float(src["longitude"])
        for target in PRIMARY_GRAHAS:
            if target == source:
                continue
            tgt = grahas[target]
            tgt_long = float(tgt["longitude"])
            rel = (tgt_long - src_long) % 360

            for aspect_house in GRAHA_ASPECTS[source]:
                aspect_angle = _target_angle(aspect_house)
                delta = _angular_diff(rel, aspect_angle)
                if delta <= orb_degrees:
                    strength = round(max(0.0, 1.0 - (delta / orb_degrees)), 4)
                    rows.append(
                        {
                            "from": source,
                            "to": target,
                            "aspect_house": aspect_house,
                            "aspect_angle": aspect_angle,
                            "orb": round(delta, 4),
                            "strength": strength,
                            "nature": "supportive" if source in {"jupiter", "venus", "moon", "mercury"} else "challenging",
                        }
                    )
                    break
    return sorted(rows, key=lambda item: (-item["strength"], item["from"], item["to"]))


def _house_from_lagna(lagna_rashi: int, graha_rashi: int) -> int:
    return ((graha_rashi - lagna_rashi) % 12) + 1


def _is_conj(g1: dict[str, Any], g2: dict[str, Any], *, orb: float = 10.0) -> bool:
    return _angular_diff(float(g1["longitude"]), float(g2["longitude"])) <= orb


def _detect_yogas(grahas: dict[str, dict[str, Any]], lagna_rashi: int) -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []

    moon_house = _house_from_lagna(lagna_rashi, int(grahas["moon"]["rashi_number"]))
    jupiter_house = _house_from_lagna(lagna_rashi, int(grahas["jupiter"]["rashi_number"]))
    rel = ((jupiter_house - moon_house) % 12) + 1
    if rel in {1, 4, 7, 10}:
        yogas.append(
            {
                "id": "gaja_kesari",
                "name": "Gaja Kesari Yoga",
                "status": "present",
                "reason": "Jupiter is in kendra from Moon.",
            }
        )

    if _is_conj(grahas["sun"], grahas["mercury"], orb=12.0):
        yogas.append(
            {
                "id": "budha_aditya",
                "name": "Budha Aditya Yoga",
                "status": "present",
                "reason": "Sun and Mercury are conjunct.",
            }
        )

    if _is_conj(grahas["moon"], grahas["mars"], orb=10.0):
        yogas.append(
            {
                "id": "chandra_mangala",
                "name": "Chandra Mangala Yoga",
                "status": "present",
                "reason": "Moon and Mars are conjunct.",
            }
        )

    lord_9 = SIGN_LORD[((lagna_rashi + 8 - 1) % 12) + 1]
    lord_10 = SIGN_LORD[((lagna_rashi + 9 - 1) % 12) + 1]
    if _is_conj(grahas[lord_9], grahas[lord_10], orb=10.0):
        yogas.append(
            {
                "id": "dharma_karmadhipati",
                "name": "Dharma Karmadhipati Yoga",
                "status": "present",
                "reason": "9th and 10th lord are in conjunction.",
            }
        )

    return yogas


def _all_between_nodes(grahas: dict[str, dict[str, Any]]) -> bool:
    rahu = float(grahas["rahu"]["longitude"])
    ketu = float(grahas["ketu"]["longitude"])

    def _between(start: float, end: float, value: float) -> bool:
        if start <= end:
            return start <= value <= end
        return value >= start or value <= end

    planets = [float(grahas[p]["longitude"]) for p in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]]

    forward = all(_between(rahu, ketu, p) for p in planets)
    backward = all(_between(ketu, rahu, p) for p in planets)
    return forward or backward


def _detect_doshas(grahas: dict[str, dict[str, Any]], lagna_rashi: int) -> list[dict[str, Any]]:
    doshas: list[dict[str, Any]] = []

    mars_house = _house_from_lagna(lagna_rashi, int(grahas["mars"]["rashi_number"]))
    if mars_house in {1, 2, 4, 7, 8, 12}:
        doshas.append(
            {
                "id": "manglik",
                "name": "Manglik Dosha",
                "status": "present",
                "severity": "moderate",
                "reason": f"Mars is in house {mars_house} from lagna.",
            }
        )

    saturn_house = _house_from_lagna(lagna_rashi, int(grahas["saturn"]["rashi_number"]))
    if saturn_house == 8:
        doshas.append(
            {
                "id": "shani_ashtama",
                "name": "Shani Ashtama",
                "status": "present",
                "severity": "moderate",
                "reason": "Saturn is in the 8th house from lagna.",
            }
        )

    if _all_between_nodes(grahas):
        doshas.append(
            {
                "id": "kaal_sarpa",
                "name": "Kaal Sarpa Pattern",
                "status": "present",
                "severity": "high",
                "reason": "All classical planets lie between Rahu and Ketu axis.",
            }
        )

    if _is_conj(grahas["sun"], grahas["rahu"], orb=9.0) or _is_conj(grahas["sun"], grahas["ketu"], orb=9.0):
        doshas.append(
            {
                "id": "pitra",
                "name": "Pitra Dosha Marker",
                "status": "present",
                "severity": "moderate",
                "reason": "Sun is closely conjunct Rahu/Ketu.",
            }
        )

    return doshas


def _major_dasha(grahas: dict[str, dict[str, Any]], birth_datetime: datetime) -> list[dict[str, Any]]:
    moon_long = float(grahas["moon"]["longitude"])
    nakshatra_index = int(moon_long / (360 / 27))
    start_lord = DASHA_SEQUENCE[nakshatra_index % len(DASHA_SEQUENCE)]
    start_idx = DASHA_SEQUENCE.index(start_lord)

    timeline = []
    cursor = birth_datetime
    for offset in range(len(DASHA_SEQUENCE)):
        lord = DASHA_SEQUENCE[(start_idx + offset) % len(DASHA_SEQUENCE)]
        years = DASHA_YEARS[lord]
        days = years * 365.2425
        end = cursor + timedelta(days=days)
        timeline.append(
            {
                "lord": lord,
                "start": cursor.isoformat(),
                "end": end.isoformat(),
                "duration_years": years,
            }
        )
        cursor = end
    return timeline


def _antar_dasha_for_major(major_lord: str, major_start: datetime, major_end: datetime) -> list[dict[str, Any]]:
    total_days = (major_end - major_start).total_seconds() / 86400
    major_years = DASHA_YEARS[major_lord]

    start_idx = DASHA_SEQUENCE.index(major_lord)
    cursor = major_start
    rows: list[dict[str, Any]] = []
    for i in range(len(DASHA_SEQUENCE)):
        sub_lord = DASHA_SEQUENCE[(start_idx + i) % len(DASHA_SEQUENCE)]
        proportion = DASHA_YEARS[sub_lord] / 120.0
        sub_days = total_days * proportion
        end = cursor + timedelta(days=sub_days)
        rows.append(
            {
                "lord": sub_lord,
                "start": cursor.isoformat(),
                "end": end.isoformat(),
                "duration_years": round((major_years * DASHA_YEARS[sub_lord]) / 120.0, 4),
            }
        )
        cursor = end

    if rows:
        rows[-1]["end"] = major_end.isoformat()
    return rows


def _dasha_v2(grahas: dict[str, dict[str, Any]], birth_datetime: datetime) -> dict[str, Any]:
    major = _major_dasha(grahas, birth_datetime)
    layered = []
    for row in major:
        start = datetime.fromisoformat(row["start"])
        end = datetime.fromisoformat(row["end"])
        layered.append(
            {
                **row,
                "antar_dasha": _antar_dasha_for_major(row["lord"], start, end),
            }
        )

    return {
        "system": "vimshottari_major_antar",
        "timeline": layered,
        "total_major_periods": len(layered),
    }


def _chart_consistency(grahas: dict[str, dict[str, Any]], d9: dict[str, dict[str, Any]], houses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append(
        {
            "id": "graha_count",
            "status": "pass" if len(grahas) == 9 else "fail",
            "detail": f"graha_count={len(grahas)}",
        }
    )
    checks.append(
        {
            "id": "house_count",
            "status": "pass" if len(houses) == 12 else "fail",
            "detail": f"house_count={len(houses)}",
        }
    )

    d9_ok = all(1 <= int(row["navamsa_rashi_number"]) <= 12 for row in d9.values())
    checks.append(
        {
            "id": "d9_range",
            "status": "pass" if d9_ok else "fail",
            "detail": "D9 navamsa rashi numbers are in [1, 12].",
        }
    )

    occupancy_total = sum(len(house["occupants"]) for house in houses)
    checks.append(
        {
            "id": "occupancy_consistency",
            "status": "pass" if occupancy_total == 9 else "fail",
            "detail": f"house occupancy total={occupancy_total}",
        }
    )

    return checks


def compute_kundali(
    birth_datetime: datetime,
    *,
    lat: float,
    lon: float,
    tz_name: str = "Asia/Kathmandu",
) -> dict[str, Any]:
    localized_dt = _ensure_datetime_with_tz(birth_datetime, tz_name)
    base_grahas = get_all_graha_positions(localized_dt, sidereal=True)
    grahas = _augment_dignities(base_grahas)
    lagna = _lagna(localized_dt, lat=lat, lon=lon)
    houses = _whole_sign_houses(lagna["rashi_number"], grahas)
    d9 = _d9_chart(grahas)

    aspects = _compute_aspects(grahas)
    yogas = _detect_yogas(grahas, lagna["rashi_number"])
    doshas = _detect_doshas(grahas, lagna["rashi_number"])
    dasha = _dasha_v2(grahas, localized_dt)
    consistency_checks = _chart_consistency(grahas, d9, houses)

    return {
        "birth_datetime": localized_dt.isoformat(),
        "location": {"latitude": lat, "longitude": lon, "timezone": tz_name},
        "lagna": lagna,
        "grahas": grahas,
        "houses": houses,
        "d9": d9,
        "aspects": aspects,
        "yogas": yogas,
        "doshas": doshas,
        "dasha": dasha,
        "consistency_checks": consistency_checks,
        "house_system": "whole_sign",
        "ayanamsa": "lahiri",
        "engine": "swiss_ephemeris",
    }
