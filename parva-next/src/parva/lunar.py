"""Lunar months and tithi days as Nepal actually reckons them.

  * An **amanta** month runs new moon to new moon.
  * It is **named by the sidereal sankranti that falls inside it**:
        Mesha -> Chaitra, Vrishabha -> Baishakh, Mithuna -> Jestha, Karka -> Ashadh,
        Simha -> Shrawan, Kanya -> Bhadra, Tula -> Ashwin, Vrishchika -> Kartik,
        Dhanu -> Mangsir, Makara -> Poush, Kumbha -> Magh, Meena -> Falgun.
  * A month with **no** sankranti is **adhik** and borrows the *next* month's name.
  * Nepal writes festival dates in **purnimanta** terms:
        purnimanta month M = krishna paksha of amanta (M-1) + shukla paksha of amanta M
    so "Falgun Krishna Chaturdashi" (Shivaratri) is the krishna paksha of amanta Magh.
  * A tithi's **civil day** is the day on which it prevails at an anchor moment:
    sunrise (udaya, the default), afternoon (aparahna: Vijaya Dashami), evening
    (pradosh: Laxmi Puja, Janmashtami, Holi) or midnight (nishita: Shivaratri).
    If a tithi never touches the anchor (kshaya) it is observed on the day whose
    daylight it filled.  Doubled or skipped tithis are exactly what the almanac
    committee adjudicates, which is why a gazetted date always outranks this.

What this module deliberately does not do: derive BS (solar) month starts from computed
sankrantis.  Against the 72 gazetted month starts of BS 2078-2083, no sunrise, noon,
sunset or midnight threshold on Lahiri ingress times reproduces the official days
(best: 66/72).  The published table is the only correct source for those, so solar
festivals are rules on the table (`bs: [month, day]`), never on the ephemeris.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from functools import lru_cache
from itertools import pairwise
from typing import Any, Literal
from zoneinfo import ZoneInfo

from . import astro
from .astro import NPT
from .bs import WEEKDAYS_NE

Anchor = Literal["sunrise", "afternoon", "evening", "midnight"]

# sidereal rashi (0 = Mesha ... 11 = Meena) -> amanta month index (1 = Baishakh ... 12 = Chaitra)
RASHI_TO_MONTH = {0: 12, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11}

YOGA = (
    "Vishkumbha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyan",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
)
KARANA_MOVABLE = ("Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti")
KARANA_FIXED = ("Shakuni", "Chatushpada", "Naga")  # karanas 58-60; karana 1 is always Kimstughna
VARA = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def _karana(elongation: float) -> str:
    """Half-tithi index (0-59) -> name: four fixed karanas bracket the movable seven."""
    k = int(elongation % 360 // 6)
    if k == 0:
        return "Kimstughna"
    if k >= 57:
        return KARANA_FIXED[k - 57]
    return KARANA_MOVABLE[(k - 1) % 7]


@dataclass(frozen=True)
class Month:
    start: datetime  # amavasya, UTC
    end: datetime  # next amavasya, UTC
    index: int  # 1 = Baishakh ... 12 = Chaitra  (amanta name)
    adhik: bool

    @property
    def name(self) -> str:
        from .bs import NAMES

        return ("Adhik " if self.adhik else "") + NAMES[self.index - 1]


@lru_cache(maxsize=32)
def months(ad_year: int) -> tuple[Month, ...]:
    """Amanta months from November of the previous year through the following spring."""
    t0 = datetime(ad_year - 1, 11, 1, tzinfo=UTC)
    new_moons = astro.new_moons(t0, 19)
    ingresses = astro.sankrantis(t0, 21)
    out = []
    for a, b in pairwise(new_moons):
        inside = [rashi for t, rashi in ingresses if a <= t < b]
        if inside:
            out.append(Month(a, b, RASHI_TO_MONTH[inside[0]], adhik=False))
        else:
            following = next(rashi for t, rashi in ingresses if t >= b)
            out.append(Month(a, b, RASHI_TO_MONTH[following], adhik=True))
    return tuple(out)


def tithi_span(m: Month, n: int) -> tuple[datetime, datetime]:
    """[start, end) of absolute tithi n (1..30) within amanta month m."""
    start = m.start if n == 1 else astro.solve(astro.elongation, m.start, 12.0 * (n - 1))
    end = m.end if n == 30 else astro.solve(astro.elongation, start, 12.0 * n)
    return start, end


def anchor(d: date, at: Anchor) -> datetime:
    """The moment of civil day d at which a festival's tithi must prevail."""
    rise = astro.sunrise(d)
    if at == "sunrise":  # udaya
        return rise
    dusk = astro.sunset(d)
    if at == "afternoon":  # aparahna: the fourth fifth of the day
        return rise + (dusk - rise) * 0.7
    if at == "evening":  # pradosh: the six ghatis after sunset; its middle
        return dusk + timedelta(minutes=72)
    return dusk + (astro.sunrise(d + timedelta(days=1)) - dusk) / 2  # nishita: the middle of the night ending day d


def civil_day(start: datetime, end: datetime, at: Anchor = "sunrise") -> date:
    """The civil day whose anchor moment falls inside the tithi interval [start, end).

    A tithi shorter than a day can miss the anchor entirely (kshaya).  Then it is observed
    on the day whose daylight it filled - the day whose noon it covers.
    """
    first = start.astimezone(NPT).date()
    # a night anchor belongs to the day before it, so look one day back as well
    candidates = (first - timedelta(days=1), first, first + timedelta(days=1))
    for d in candidates:
        if start <= anchor(d, at) < end:
            return d
    for d in candidates:
        if start <= datetime.combine(d, time(12), tzinfo=NPT) < end:
            return d
    return first


def festival_day(
    ad_year: int,
    month: int,
    paksha: Literal["shukla", "krishna"],
    tithi: int,
    adhik: Literal["nija", "adhik"] = "nija",
    at: Anchor = "sunrise",
) -> date | None:
    """Civil date in ad_year of a purnimanta (month, paksha, tithi), or None if it has none."""
    n = tithi if paksha == "shukla" else 15 + tithi
    amanta = month if paksha == "shukla" else (month - 2) % 12 + 1  # krishna paksha lives in the previous amanta month
    for m in months(ad_year):
        if m.index == amanta and m.adhik == (adhik == "adhik"):
            d = civil_day(*tithi_span(m, n), at)
            if d.year == ad_year:
                return d
    return None


def panchanga(d: date, geo: tuple[float, float, float] = astro.KATHMANDU, tz: ZoneInfo = NPT) -> dict[str, Any]:
    """Day-level panchanga at sunrise for civil date d at geo."""
    rise = astro.sunrise(d, geo, tz)
    t = astro.tithi(rise)
    sun, moon = astro.longitudes(rise)
    m = next((m for m in months(d.year) if m.start <= rise < m.end), None)
    return {
        "sunrise": rise.astimezone(tz).isoformat(timespec="seconds"),
        "sunset": astro.sunset(d, geo, tz).astimezone(tz).isoformat(timespec="seconds"),
        "tithi": t,
        "tithi_name": astro.TITHI[t - 1],
        "paksha": "shukla" if t <= 15 else "krishna",
        "nakshatra": astro.NAKSHATRA[astro.nakshatra(rise) - 1],
        "yoga": YOGA[int((sun + moon) % 360 // (360 / 27))],
        "karana": _karana(moon - sun),
        "vara": VARA[d.weekday()],
        "vara_ne": WEEKDAYS_NE[d.weekday()],
        "lunar_month": m.name if m else None,
        "adhik_month": bool(m and m.adhik),
    }
