"""Festival dates: the gazette first, the engine second, and the two always compared.

`occurrence()` answers "when is X in year Y" with one `source`.  `audit()` lists every
festival where the Ministry of Home Affairs and the astronomy disagree - the number
that tells you how far to trust either.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from functools import lru_cache
from importlib.resources import files
from typing import Any

from . import bs, holidays, lunar

Rule = dict[str, Any]

_DATA = files("parva") / "data"
RULES: dict[str, Rule] = {
    k: v for k, v in json.loads((_DATA / "festival_rules.json").read_text("utf-8")).items() if not k.startswith("_")
}
INFO: dict[str, dict[str, Any]] = {
    f["id"]: f for f in json.loads((_DATA / "festivals.json").read_text("utf-8"))["festivals"]
}
MONTH = {name.lower(): i + 1 for i, name in enumerate(bs.NAMES)}
MIN_YEAR, MAX_YEAR = bs.START[bs.MIN_YEAR].year + 1, bs.END.year - 1


def validate_year(year: int) -> None:
    if type(year) is not int or not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError(f"Festival calculations support Gregorian years {MIN_YEAR}-{MAX_YEAR}.")


@dataclass(frozen=True)
class Occurrence:
    id: str
    start: date | None
    end: date | None
    source: str  # "moha-2083" | "computed" | "undetermined"
    gazette: date | None  # what the Ministry of Home Affairs says, if anything
    engine: date | None  # what astronomy + the rule says, if there is a rule

    def as_dict(self) -> dict[str, Any]:
        return {k: v.isoformat() if isinstance(v, date) else v for k, v in asdict(self).items()}


def ids() -> list[str]:
    return list(RULES)


def days(fid: str) -> int:
    return int(RULES[fid].get("days", INFO.get(fid, {}).get("duration_days", 1)))


@lru_cache(maxsize=4096)
def engine_date(fid: str, ad_year: int) -> date | None:
    """What the rule table and the ephemeris say, ignoring the gazette."""
    validate_year(ad_year)
    r = RULES[fid]
    if "same_as" in r:
        return engine_date(r["same_as"], ad_year)
    if "after" in r:
        base = engine_date(r["after"], ad_year)
        return base + timedelta(days=r["offset"]) if base else None
    if "bs" in r:  # fixed BS date: the BS year whose date lands in ad_year
        for bs_year in (ad_year + 56, ad_year + 57):
            if bs_year in bs.MONTHS and (d := bs.to_ad(bs_year, *r["bs"])).year == ad_year:
                return d
        return None
    if "month" in r:
        return lunar.festival_day(
            ad_year, MONTH[r["month"]], r["paksha"], r["tithi"], r.get("adhik", "nija"), r.get("at", "sunrise")
        )
    return None  # committee-decided; only the gazette knows


def gazette_date(fid: str, ad_year: int) -> tuple[date, str] | None:
    """(date, source id) from the gazette, following `gazette` and `same_as` links."""
    row = holidays.gazetted(RULES[fid].get("gazette", fid), ad_year)
    if row is None:
        alias = RULES[fid].get("same_as")
        return gazette_date(alias, ad_year) if alias else None
    return date.fromisoformat(row["ad"]), holidays.source(int(row["bs"][:4])) or "gazette"


def occurrence(fid: str, ad_year: int) -> Occurrence:
    validate_year(ad_year)
    if fid not in RULES:
        raise KeyError(fid)
    engine = engine_date(fid, ad_year)
    gaz = gazette_date(fid, ad_year)
    start: date | None
    if gaz:
        start, source = gaz
    else:
        start, source = engine, ("computed" if engine else "undetermined")
    end = start + timedelta(days=days(fid) - 1) if start else None
    return Occurrence(fid, start, end, source, gaz[0] if gaz else None, engine)


def in_year(ad_year: int) -> list[Occurrence]:
    return sorted((occurrence(f, ad_year) for f in RULES), key=lambda o: (o.start is None, o.start or date.min))


def upcoming(from_date: date, count: int = 10) -> list[Occurrence]:
    if not 1 <= count <= 100:
        raise ValueError("count must be between 1 and 100")
    bs.to_bs(from_date)
    pool = in_year(from_date.year)
    if from_date.year < MAX_YEAR:
        pool += in_year(from_date.year + 1)
    future: dict[str, Occurrence] = {}
    for occurrence in sorted(pool, key=lambda o: o.start or date.max):
        if occurrence.start and occurrence.start >= from_date:
            future.setdefault(occurrence.id, occurrence)
    return list(future.values())[:count]


def audit(ad_year: int) -> list[dict[str, Any]]:
    """Every festival where the gazette and the engine both speak and disagree."""
    return [
        {
            "id": o.id,
            "gazette": o.gazette.isoformat(),
            "engine": o.engine.isoformat(),
            "delta_days": (o.engine - o.gazette).days,
        }
        for o in in_year(ad_year)
        if o.gazette and o.engine and o.gazette != o.engine
    ]
