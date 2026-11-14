"""Swiss Ephemeris (Moshier) wrapper: sidereal Sun and Moon, sunrise, and event solving.

Every datetime that crosses this boundary is timezone-aware.  Longitudes are sidereal
with the Lahiri ayanamsa, which is what Nepali and Indian almanacs use.  Moshier is
accurate to a few arcseconds, three orders of magnitude finer than a tithi (12 deg).

    pip install parva-calendar[astro]
"""

from __future__ import annotations

import math
import threading
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

NPT = ZoneInfo("Asia/Kathmandu")
KATHMANDU = (85.3240, 27.7172, 1400.0)  # (longitude E, latitude N, altitude m) - swe geopos order

_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
_LOCK = threading.Lock()  # libswe keeps global state; one caller at a time

RASHI = (
    "mesha",
    "vrishabha",
    "mithuna",
    "karka",
    "simha",
    "kanya",
    "tula",
    "vrishchika",
    "dhanu",
    "makara",
    "kumbha",
    "meena",
)
NAKSHATRA = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)
TITHI = (
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
)


# ------------------------------------------------------------------ time
def jd(t: datetime) -> float:
    """Aware datetime -> Julian day (UT)."""
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("An explicit time zone is required.")
    u = t.astimezone(UTC)
    return float(swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + (u.second + u.microsecond / 1e6) / 3600))


def from_jd(j: float) -> datetime:
    y, m, d, h = swe.revjul(j)
    return datetime(y, m, d, tzinfo=UTC) + timedelta(hours=h)


# ------------------------------------------------------------------ positions
def longitudes(t: datetime) -> tuple[float, float]:
    """Sidereal ecliptic longitudes (sun, moon) in degrees at instant t."""
    with _LOCK:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        j = jd(t)
        sun = swe.calc_ut(j, swe.SUN, _FLAGS)[0][0]
        moon = swe.calc_ut(j, swe.MOON, _FLAGS)[0][0]
    return sun % 360, moon % 360


def sun_longitude(t: datetime) -> float:
    return longitudes(t)[0]


def elongation(t: datetime) -> float:
    """Moon minus Sun, 0-360.  A tithi is 12 degrees of this."""
    sun, moon = longitudes(t)
    return (moon - sun) % 360


def tithi(t: datetime) -> int:
    """1..30 prevailing at t (1-15 shukla paksha, 16-30 krishna paksha)."""
    return int(elongation(t) // 12) + 1


def nakshatra(t: datetime) -> int:
    """1..27 (Moon's sidereal longitude in 13d20m arcs)."""
    return int(longitudes(t)[1] // (360 / 27)) + 1


def sun_rashi(t: datetime) -> int:
    """0 = Mesha ... 11 = Meena."""
    return int(sun_longitude(t) // 30)


# ------------------------------------------------------------------ sun events
def _rise_set(d: date, which: int, geo: tuple[float, float, float], tz: ZoneInfo) -> datetime:
    if not all(math.isfinite(value) for value in geo) or not -180 <= geo[0] <= 180 or not -90 <= geo[1] <= 90:
        raise ValueError("Invalid geographic coordinates.")
    j0 = jd(datetime.combine(d, time(0), tzinfo=tz))  # local midnight; first event after it is today's
    with _LOCK:
        rc, times = swe.rise_trans(j0, swe.SUN, which, geo, 0.0, 0.0, swe.FLG_MOSEPH)
    if rc < 0:
        raise ValueError(f"the sun does not {'rise' if which == swe.CALC_RISE else 'set'} at {geo} on {d}")
    return from_jd(times[0])


def sunrise(d: date, geo: tuple[float, float, float] = KATHMANDU, tz: ZoneInfo = NPT) -> datetime:
    """Upper-limb sunrise with refraction, for civil date d at geo.  Returned in UTC."""
    return _rise_set(d, swe.CALC_RISE, geo, tz)


def sunset(d: date, geo: tuple[float, float, float] = KATHMANDU, tz: ZoneInfo = NPT) -> datetime:
    return _rise_set(d, swe.CALC_SET, geo, tz)


# ------------------------------------------------------------------ event solving
def solve(
    f: Callable[[datetime], float],
    start: datetime,
    target: float,
    step: timedelta = timedelta(days=1),
    tolerance: timedelta = timedelta(seconds=15),
) -> datetime:
    """First instant after `start` at which the increasing angle f (mod 360) reaches `target`.

    g = (f - target) mod 360 is a sawtooth that falls to 0 exactly at the crossing.
    Walk forward one `step` at a time until g falls, then bisect inside that step.
    Valid while `step` is shorter than f's period (a day, for the Sun or the Moon-Sun angle).
    """
    if step <= timedelta(0) or tolerance <= timedelta(0):
        raise ValueError("Step and tolerance must be positive.")

    def g(t: datetime) -> float:
        value = (f(t) - target) % 360
        if not math.isfinite(value):
            raise ValueError("Event solver received a non-finite angle.")
        return value

    lo, g_lo = start, g(start)
    for _ in range(400):
        hi, g_hi = lo + step, g(lo + step)
        if g_hi < g_lo:
            break
        lo, g_lo = hi, g_hi
    else:
        raise ValueError("No angular crossing found within 400 steps.")
    while hi - lo > tolerance:
        mid = lo + (hi - lo) / 2
        if g(mid) < g_lo:
            hi = mid
        else:
            lo, g_lo = mid, g(mid)
    return hi


def new_moons(after: datetime, count: int) -> list[datetime]:
    """Successive amavasya instants (elongation -> 0) after `after`."""
    out: list[datetime] = []
    t = after
    for _ in range(count):
        t = solve(elongation, t, 0.0)
        out.append(t)
        t += timedelta(days=27)
    return out


def sankrantis(after: datetime, count: int) -> list[tuple[datetime, int]]:
    """Successive (instant, rashi) sidereal solar ingresses after `after`."""
    out: list[tuple[datetime, int]] = []
    t = after
    for _ in range(count):
        rashi = (sun_rashi(t) + 1) % 12
        t = solve(sun_longitude, t, 30.0 * rashi)
        out.append((t, rashi))
        t += timedelta(days=25)
    return out
