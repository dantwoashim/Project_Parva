"""Muhurta and kala windows from sunrise/sunset with v2 ranking layers."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Any

from app.calendar.ephemeris.swiss_eph import calculate_sunrise, calculate_sunset
from app.calendar.panchanga import get_panchanga

NPT = timezone(timedelta(hours=5, minutes=45))

# 30 classical muhurta labels retained for continuity with prior API contracts.
MUHURTA_NAMES = [
    "Rudra", "Ahi", "Mitra", "Pitru", "Vasu", "Vara", "Vishvedeva", "Vidhi", "Satamukhi", "Puruhuta",
    "Vahini", "Naktankara", "Varuna", "Aryaman", "Bhaga", "Girisha", "Ajapada", "Ahirbudhnya", "Pushya", "Ashvini",
    "Yama", "Agni", "Vidhatri", "Chanda", "Aditi", "Jiva", "Vishnu", "Dyumadgadyuti", "Brahma", "Samudra",
]

ABHIJIT_INDEX = 7

RAHU_SEGMENT_BY_WEEKDAY = {0: 1, 1: 6, 2: 4, 3: 5, 4: 3, 5: 2, 6: 7}
YAMAGANDA_SEGMENT_BY_WEEKDAY = {0: 3, 1: 2, 2: 1, 3: 0, 4: 6, 5: 5, 6: 4}
GULIKA_SEGMENT_BY_WEEKDAY = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0, 6: 6}

PLANETARY_HORA_ORDER = ["sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars"]
WEEKDAY_HORA_LORD = {
    0: "moon",     # Monday
    1: "mars",     # Tuesday
    2: "mercury",  # Wednesday
    3: "jupiter",  # Thursday
    4: "venus",    # Friday
    5: "saturn",   # Saturday
    6: "sun",      # Sunday
}

HORA_LORD_DISPLAY = {
    "sun": "Sun",
    "moon": "Moon",
    "mars": "Mars",
    "mercury": "Mercury",
    "jupiter": "Jupiter",
    "venus": "Venus",
    "saturn": "Saturn",
}

HORA_LORD_QUALITY = {
    "sun": "neutral",
    "moon": "auspicious",
    "mars": "inauspicious",
    "mercury": "auspicious",
    "jupiter": "auspicious",
    "venus": "auspicious",
    "saturn": "inauspicious",
}

# Widely used chaughadia name cycle representation (day/night tables by weekday).
CHAUGHADIA_DAY_BY_WEEKDAY = {
    0: ["amrit", "kal", "shubh", "rog", "udveg", "char", "labh", "amrit"],
    1: ["rog", "udveg", "char", "labh", "amrit", "kal", "shubh", "rog"],
    2: ["labh", "amrit", "kal", "shubh", "rog", "udveg", "char", "labh"],
    3: ["shubh", "rog", "udveg", "char", "labh", "amrit", "kal", "shubh"],
    4: ["char", "labh", "amrit", "kal", "shubh", "rog", "udveg", "char"],
    5: ["kal", "shubh", "rog", "udveg", "char", "labh", "amrit", "kal"],
    6: ["udveg", "char", "labh", "amrit", "kal", "shubh", "rog", "udveg"],
}

CHAUGHADIA_NIGHT_BY_WEEKDAY = {
    0: ["char", "rog", "kal", "labh", "udveg", "shubh", "amrit", "char"],
    1: ["labh", "udveg", "shubh", "amrit", "char", "rog", "kal", "labh"],
    2: ["amrit", "char", "rog", "kal", "labh", "udveg", "shubh", "amrit"],
    3: ["kal", "labh", "udveg", "shubh", "amrit", "char", "rog", "kal"],
    4: ["rog", "kal", "labh", "udveg", "shubh", "amrit", "char", "rog"],
    5: ["udveg", "shubh", "amrit", "char", "rog", "kal", "labh", "udveg"],
    6: ["shubh", "amrit", "char", "rog", "kal", "labh", "udveg", "shubh"],
}

CHAUGHADIA_QUALITY = {
    "amrit": "auspicious",
    "shubh": "auspicious",
    "labh": "auspicious",
    "char": "neutral",
    "udveg": "inauspicious",
    "kal": "inauspicious",
    "rog": "inauspicious",
}

CEREMONY_PROFILES = {
    "general": {
        "preferred_hora_lords": {"jupiter", "venus", "moon", "mercury"},
        "avoid_hora_lords": {"saturn", "mars"},
        "preferred_chaughadia": {"amrit", "shubh", "labh"},
        "avoid_chaughadia": {"rog", "kal", "udveg"},
        "minimum_score": 40,
    },
    "vivah": {
        "preferred_hora_lords": {"jupiter", "venus", "moon"},
        "avoid_hora_lords": {"saturn", "mars", "sun"},
        "preferred_chaughadia": {"amrit", "shubh", "labh"},
        "avoid_chaughadia": {"rog", "kal", "udveg"},
        "minimum_score": 55,
    },
    "griha_pravesh": {
        "preferred_hora_lords": {"jupiter", "venus", "mercury"},
        "avoid_hora_lords": {"saturn", "mars"},
        "preferred_chaughadia": {"amrit", "shubh", "labh", "char"},
        "avoid_chaughadia": {"rog", "kal"},
        "minimum_score": 50,
    },
    "travel": {
        "preferred_hora_lords": {"moon", "mercury", "jupiter"},
        "avoid_hora_lords": {"saturn"},
        "preferred_chaughadia": {"labh", "char", "amrit"},
        "avoid_chaughadia": {"rog", "kal", "udveg"},
        "minimum_score": 35,
    },
    "upanayana": {
        "preferred_hora_lords": {"jupiter", "sun", "moon"},
        "avoid_hora_lords": {"saturn", "mars"},
        "preferred_chaughadia": {"shubh", "amrit", "labh"},
        "avoid_chaughadia": {"rog", "kal"},
        "minimum_score": 50,
    },
}

ASSUMPTION_SETS = {
    "np-mainstream-v2": {
        "quality_weights": {"auspicious": 45, "neutral": 18, "inauspicious": -35},
        "hora_preferred_bonus": 18,
        "hora_avoid_penalty": -16,
        "chaughadia_preferred_bonus": 16,
        "chaughadia_avoid_penalty": -22,
        "tara_favorable_bonus": 14,
        "tara_unfavorable_penalty": -18,
        "avoidance_overlap_penalty": -80,
    },
    "diaspora-practical-v2": {
        "quality_weights": {"auspicious": 38, "neutral": 20, "inauspicious": -28},
        "hora_preferred_bonus": 14,
        "hora_avoid_penalty": -12,
        "chaughadia_preferred_bonus": 12,
        "chaughadia_avoid_penalty": -15,
        "tara_favorable_bonus": 10,
        "tara_unfavorable_penalty": -10,
        "avoidance_overlap_penalty": -65,
    },
}

# 27 nakshatras for tara-bala distance mapping.
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

TARA_SEQUENCE = [
    "janma",
    "sampat",
    "vipat",
    "kshema",
    "pratyari",
    "sadhaka",
    "naidhana",
    "mitra",
    "param_mitra",
]

TARA_QUALITY = {
    "janma": "neutral",
    "sampat": "auspicious",
    "vipat": "inauspicious",
    "kshema": "auspicious",
    "pratyari": "inauspicious",
    "sadhaka": "auspicious",
    "naidhana": "inauspicious",
    "mitra": "auspicious",
    "param_mitra": "auspicious",
}


def _timezone(tz_name: str | None) -> ZoneInfo:
    if tz_name:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            pass
    return ZoneInfo("Asia/Kathmandu")


def _default_sun_times(
    target_date: date,
    *,
    lat: float,
    lon: float,
    tz_name: str,
) -> tuple[datetime, datetime, datetime]:
    tz = _timezone(tz_name)
    try:
        sunrise = calculate_sunrise(target_date, latitude=lat, longitude=lon).astimezone(tz)
        sunset = calculate_sunset(target_date, latitude=lat, longitude=lon).astimezone(tz)
        next_sunrise = calculate_sunrise(target_date + timedelta(days=1), latitude=lat, longitude=lon).astimezone(tz)

        # Ensure monotonic ordering even if timezone conversion crosses midnight boundaries.
        if sunset <= sunrise:
            sunset += timedelta(days=1)
        if next_sunrise <= sunset:
            next_sunrise += timedelta(days=1)
        return sunrise, sunset, next_sunrise
    except Exception:
        return (
            datetime(target_date.year, target_date.month, target_date.day, 6, 15, tzinfo=tz),
            datetime(target_date.year, target_date.month, target_date.day, 18, 0, tzinfo=tz),
            datetime(target_date.year, target_date.month, target_date.day, 6, 15, tzinfo=tz) + timedelta(days=1),
        )


def _quality(index: int) -> str:
    if index in {0, 20, 23}:
        return "inauspicious"
    if index in {2, 4, 7, 18, 19, 25, 26, 28}:
        return "auspicious"
    return "neutral"


def _segment_window(start: datetime, segment_seconds: float, segment_index: int) -> dict[str, Any]:
    window_start = start + timedelta(seconds=segment_index * segment_seconds)
    window_end = window_start + timedelta(seconds=segment_seconds)
    return {
        "segment": segment_index + 1,
        "start": window_start.isoformat(),
        "end": window_end.isoformat(),
        "duration_minutes": round(segment_seconds / 60, 1),
    }


def _split_muhurtas(start: datetime, end: datetime, *, count: int, index_offset: int, period: str) -> list[dict[str, Any]]:
    segment_seconds = (end - start).total_seconds() / count
    rows: list[dict[str, Any]] = []
    for i in range(count):
        idx = index_offset + i
        window_start = start + timedelta(seconds=i * segment_seconds)
        window_end = start + timedelta(seconds=(i + 1) * segment_seconds)
        rows.append(
            {
                "number": idx + 1,
                "index": idx,
                "name": MUHURTA_NAMES[idx],
                "period": period,
                "start": window_start.isoformat(),
                "end": window_end.isoformat(),
                "duration_minutes": round(segment_seconds / 60, 1),
                "quality": _quality(idx),
                "is_abhijit": idx == ABHIJIT_INDEX,
            }
        )
    return rows


def _build_horas(sunrise: datetime, sunset: datetime, next_sunrise: datetime, weekday: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    day_seconds = (sunset - sunrise).total_seconds()
    night_seconds = (next_sunrise - sunset).total_seconds()

    day_segment = day_seconds / 12
    night_segment = night_seconds / 12

    start_lord = WEEKDAY_HORA_LORD[weekday]
    start_idx = PLANETARY_HORA_ORDER.index(start_lord)

    day_horas: list[dict[str, Any]] = []
    for i in range(12):
        lord = PLANETARY_HORA_ORDER[(start_idx + i) % len(PLANETARY_HORA_ORDER)]
        start = sunrise + timedelta(seconds=i * day_segment)
        end = sunrise + timedelta(seconds=(i + 1) * day_segment)
        day_horas.append(
            {
                "hora_number": i + 1,
                "period": "day",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "lord": lord,
                "lord_display": HORA_LORD_DISPLAY[lord],
                "quality": HORA_LORD_QUALITY[lord],
                "duration_minutes": round(day_segment / 60, 1),
            }
        )

    night_horas: list[dict[str, Any]] = []
    for i in range(12):
        lord = PLANETARY_HORA_ORDER[(start_idx + 12 + i) % len(PLANETARY_HORA_ORDER)]
        start = sunset + timedelta(seconds=i * night_segment)
        end = sunset + timedelta(seconds=(i + 1) * night_segment)
        night_horas.append(
            {
                "hora_number": i + 1,
                "period": "night",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "lord": lord,
                "lord_display": HORA_LORD_DISPLAY[lord],
                "quality": HORA_LORD_QUALITY[lord],
                "duration_minutes": round(night_segment / 60, 1),
            }
        )

    return day_horas, night_horas


def _build_chaughadia(start: datetime, end: datetime, *, names: list[str], period: str) -> list[dict[str, Any]]:
    segment_seconds = (end - start).total_seconds() / 8
    rows: list[dict[str, Any]] = []
    for i in range(8):
        window_start = start + timedelta(seconds=i * segment_seconds)
        window_end = start + timedelta(seconds=(i + 1) * segment_seconds)
        name = names[i]
        rows.append(
            {
                "segment": i + 1,
                "period": period,
                "name": name,
                "name_display": name.replace("_", " ").title(),
                "quality": CHAUGHADIA_QUALITY.get(name, "neutral"),
                "start": window_start.isoformat(),
                "end": window_end.isoformat(),
                "duration_minutes": round(segment_seconds / 60, 1),
            }
        )
    return rows


def _nakshatra_number(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 27 else None

    raw = str(value).strip()
    if not raw:
        return None
    if raw.isdigit():
        num = int(raw)
        return num if 1 <= num <= 27 else None

    lower_map = {name.lower(): idx + 1 for idx, name in enumerate(NAKSHATRA_NAMES)}
    return lower_map.get(raw.lower())


def _tara_bala_profile(*, target_date: date, lat: float, lon: float, birth_nakshatra: str | int | None) -> dict[str, Any]:
    panchanga = get_panchanga(target_date, latitude=lat, longitude=lon)
    current_num = int(panchanga["nakshatra"]["number"])
    current_name = panchanga["nakshatra"]["name"]

    birth_num = _nakshatra_number(birth_nakshatra)
    if birth_num is None:
        return {
            "available": False,
            "current_nakshatra": {"number": current_num, "name": current_name},
            "birth_nakshatra": None,
            "tara": None,
            "quality": "unknown",
            "favorable": None,
            "note": "Provide birth_nakshatra (1-27 or name) for tara-bala scoring.",
        }

    distance = ((current_num - birth_num) % 27) + 1
    tara_index = ((distance - 1) % 9) + 1
    tara_name = TARA_SEQUENCE[tara_index - 1]
    quality = TARA_QUALITY[tara_name]

    return {
        "available": True,
        "current_nakshatra": {"number": current_num, "name": current_name},
        "birth_nakshatra": {
            "number": birth_num,
            "name": NAKSHATRA_NAMES[birth_num - 1],
        },
        "tara": {
            "index": tara_index,
            "name": tara_name,
            "distance": distance,
        },
        "quality": quality,
        "favorable": quality == "auspicious",
        "note": "Tara-bala is an auxiliary compatibility signal and should be used with local ritual guidance.",
    }


def _window_midpoint(window: dict[str, Any]) -> datetime:
    start = datetime.fromisoformat(window["start"])
    end = datetime.fromisoformat(window["end"])
    return start + (end - start) / 2


def _find_window_for_time(target: datetime, windows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in windows:
        start = datetime.fromisoformat(row["start"])
        end = datetime.fromisoformat(row["end"])
        if start <= target < end:
            return row
    return windows[-1] if windows else None


def _overlaps(a: dict[str, Any], b: dict[str, Any]) -> bool:
    a_start = datetime.fromisoformat(a["start"])
    a_end = datetime.fromisoformat(a["end"])
    b_start = datetime.fromisoformat(b["start"])
    b_end = datetime.fromisoformat(b["end"])
    return a_start < b_end and b_start < a_end


def get_muhurtas(
    target_date: date,
    *,
    lat: float,
    lon: float,
    tz_name: str = "Asia/Kathmandu",
    birth_nakshatra: str | int | None = None,
) -> dict[str, Any]:
    sunrise, sunset, next_sunrise = _default_sun_times(target_date, lat=lat, lon=lon, tz_name=tz_name)

    day_muhurtas = _split_muhurtas(sunrise, sunset, count=15, index_offset=0, period="day")
    night_muhurtas = _split_muhurtas(sunset, next_sunrise, count=15, index_offset=15, period="night")
    muhurta_rows = day_muhurtas + night_muhurtas

    day_horas, night_horas = _build_horas(sunrise, sunset, next_sunrise, target_date.weekday())

    day_chaughadia = _build_chaughadia(
        sunrise,
        sunset,
        names=CHAUGHADIA_DAY_BY_WEEKDAY[target_date.weekday()],
        period="day",
    )
    night_chaughadia = _build_chaughadia(
        sunset,
        next_sunrise,
        names=CHAUGHADIA_NIGHT_BY_WEEKDAY[target_date.weekday()],
        period="night",
    )

    tara_bala = _tara_bala_profile(
        target_date=target_date,
        lat=lat,
        lon=lon,
        birth_nakshatra=birth_nakshatra,
    )

    day_duration_minutes = round((sunset - sunrise).total_seconds() / 60, 1)
    night_duration_minutes = round((next_sunrise - sunset).total_seconds() / 60, 1)

    return {
        "date": target_date.isoformat(),
        "sunrise": sunrise.isoformat(),
        "sunset": sunset.isoformat(),
        "next_sunrise": next_sunrise.isoformat(),
        "total_muhurtas": 30,
        "day_muhurtas": day_muhurtas,
        "night_muhurtas": night_muhurtas,
        "muhurtas": muhurta_rows,
        "daylight_minutes": day_duration_minutes,
        "night_minutes": night_duration_minutes,
        "muhurta_duration_minutes": {
            "day": round(day_duration_minutes / 15, 1),
            "night": round(night_duration_minutes / 15, 1),
        },
        "abhijit_muhurta": day_muhurtas[ABHIJIT_INDEX],
        "hora": {
            "day": day_horas,
            "night": night_horas,
        },
        "chaughadia": {
            "day": day_chaughadia,
            "night": night_chaughadia,
        },
        "tara_bala": tara_bala,
    }


def get_rahu_kalam(
    target_date: date,
    *,
    lat: float,
    lon: float,
    tz_name: str = "Asia/Kathmandu",
) -> dict[str, Any]:
    sunrise, sunset, _ = _default_sun_times(target_date, lat=lat, lon=lon, tz_name=tz_name)
    daytime = (sunset - sunrise).total_seconds()
    segment_seconds = daytime / 8
    weekday = target_date.weekday()  # Monday=0

    return {
        "date": target_date.isoformat(),
        "weekday": target_date.strftime("%A"),
        "sunrise": sunrise.isoformat(),
        "sunset": sunset.isoformat(),
        "segment_model": "weekday_ashta_kala_v2",
        "rahu_kalam": _segment_window(sunrise, segment_seconds, RAHU_SEGMENT_BY_WEEKDAY[weekday]),
        "yamaganda": _segment_window(sunrise, segment_seconds, YAMAGANDA_SEGMENT_BY_WEEKDAY[weekday]),
        "gulika": _segment_window(sunrise, segment_seconds, GULIKA_SEGMENT_BY_WEEKDAY[weekday]),
    }


def get_auspicious_windows(
    target_date: date,
    *,
    lat: float,
    lon: float,
    ceremony_type: str | None = None,
    tz_name: str = "Asia/Kathmandu",
    birth_nakshatra: str | int | None = None,
    assumption_set_id: str = "np-mainstream-v2",
) -> dict[str, Any]:
    muhurta_data = get_muhurtas(
        target_date,
        lat=lat,
        lon=lon,
        tz_name=tz_name,
        birth_nakshatra=birth_nakshatra,
    )
    kalam_data = get_rahu_kalam(target_date, lat=lat, lon=lon, tz_name=tz_name)

    ceremony_key = (ceremony_type or "").strip().lower() or "general"
    profile = CEREMONY_PROFILES.get(ceremony_key, CEREMONY_PROFILES["general"])
    assumption_set = ASSUMPTION_SETS.get(assumption_set_id, ASSUMPTION_SETS["np-mainstream-v2"])

    tara_bala = muhurta_data["tara_bala"]
    tara_quality = tara_bala.get("quality", "unknown")

    ranked_windows: list[dict[str, Any]] = []
    for window in muhurta_data["day_muhurtas"]:
        midpoint = _window_midpoint(window)
        hora = _find_window_for_time(midpoint, muhurta_data["hora"]["day"])
        chaughadia = _find_window_for_time(midpoint, muhurta_data["chaughadia"]["day"])

        overlaps_avoidance = any(
            _overlaps(window, kalam_data[key]) for key in ("rahu_kalam", "yamaganda", "gulika")
        )

        score = assumption_set["quality_weights"][window["quality"]]
        breakdown = {
            "base_quality": assumption_set["quality_weights"][window["quality"]],
            "hora": 0,
            "chaughadia": 0,
            "tara_bala": 0,
            "avoidance": 0,
        }

        if hora:
            if hora["lord"] in profile["preferred_hora_lords"]:
                breakdown["hora"] += assumption_set["hora_preferred_bonus"]
            if hora["lord"] in profile["avoid_hora_lords"]:
                breakdown["hora"] += assumption_set["hora_avoid_penalty"]

        if chaughadia:
            if chaughadia["name"] in profile["preferred_chaughadia"]:
                breakdown["chaughadia"] += assumption_set["chaughadia_preferred_bonus"]
            if chaughadia["name"] in profile["avoid_chaughadia"]:
                breakdown["chaughadia"] += assumption_set["chaughadia_avoid_penalty"]

        if tara_bala.get("available"):
            if tara_quality == "auspicious":
                breakdown["tara_bala"] += assumption_set["tara_favorable_bonus"]
            elif tara_quality == "inauspicious":
                breakdown["tara_bala"] += assumption_set["tara_unfavorable_penalty"]

        if overlaps_avoidance:
            breakdown["avoidance"] += assumption_set["avoidance_overlap_penalty"]

        score += breakdown["hora"]
        score += breakdown["chaughadia"]
        score += breakdown["tara_bala"]
        score += breakdown["avoidance"]

        ranked_windows.append(
            {
                **window,
                "score": score,
                "score_breakdown": breakdown,
                "hora": hora,
                "chaughadia": chaughadia,
                "overlaps_avoidance": overlaps_avoidance,
            }
        )

    ranked_windows.sort(key=lambda row: (row["score"], row["start"]), reverse=True)

    minimum_score = profile["minimum_score"]
    selected = [row for row in ranked_windows if row["score"] >= minimum_score]

    if selected:
        best_window = selected[0]
    else:
        best_window = {
            **muhurta_data["abhijit_muhurta"],
            "score": 0,
            "score_breakdown": {
                "base_quality": 0,
                "hora": 0,
                "chaughadia": 0,
                "tara_bala": 0,
                "avoidance": 0,
            },
            "hora": _find_window_for_time(_window_midpoint(muhurta_data["abhijit_muhurta"]), muhurta_data["hora"]["day"]),
            "chaughadia": _find_window_for_time(_window_midpoint(muhurta_data["abhijit_muhurta"]), muhurta_data["chaughadia"]["day"]),
            "overlaps_avoidance": any(
                _overlaps(muhurta_data["abhijit_muhurta"], kalam_data[key])
                for key in ("rahu_kalam", "yamaganda", "gulika")
            ),
            "fallback_reason": "No ranked window met minimum score; using Abhijit Muhurta fallback.",
        }

    return {
        "date": target_date.isoformat(),
        "ceremony_type": ceremony_key,
        "assumption_set_id": assumption_set_id if assumption_set_id in ASSUMPTION_SETS else "np-mainstream-v2",
        "ranking_profile": {
            "preferred_hora_lords": sorted(profile["preferred_hora_lords"]),
            "avoid_hora_lords": sorted(profile["avoid_hora_lords"]),
            "preferred_chaughadia": sorted(profile["preferred_chaughadia"]),
            "avoid_chaughadia": sorted(profile["avoid_chaughadia"]),
            "minimum_score": minimum_score,
        },
        "tara_bala": tara_bala,
        "auspicious_muhurtas": selected,
        "ranked_muhurtas": ranked_windows,
        "best_window": best_window,
        "avoid": {
            "rahu_kalam": kalam_data["rahu_kalam"],
            "yamaganda": kalam_data["yamaganda"],
            "gulika": kalam_data["gulika"],
        },
    }
